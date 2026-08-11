"""Presolve: the reductions a solver applies before any algorithm runs.

Each reduction on its own is nearly trivial. The point of the module is the
loop around them: a reduction changes the model, which lets the next one fire,
and the interesting behaviour is entirely in that cascade.

Two rules the code holds to, both borrowed from how real solvers get this
wrong:

* every reduction that removes a column records what it needs to put the
  column back, so `postsolve` can rebuild a solution to the model the user
  actually handed over
* when the loop cannot be trusted it raises rather than returning something
  plausible. A presolve that silently drops a feasible region is the worst
  bug in this subject, because every downstream answer still looks sensible
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from fractions import Fraction as F

from .model import Col, Model, Row

MAX_ROUNDS = 100


@dataclass(frozen=True)
class Reduction:
    """One thing presolve did, and the round it did it in."""

    round: int
    kind: str
    target: str
    detail: str


@dataclass
class Presolved:
    status: str                       # "reduced" | "infeasible" | "unbounded"
    model: Model | None               # the compacted model, if there is one
    log: tuple[Reduction, ...]
    kept_cols: tuple[int, ...]        # reduced column -> original column
    kept_rows: tuple[int, ...]        # reduced row -> original row
    fixed: dict[int, F]               # original column -> value it was fixed at
    before: tuple[int, int, int]
    after: tuple[int, int, int]

    @property
    def rounds(self) -> int:
        return max((r.round for r in self.log), default=0)

    def counts(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for r in self.log:
            out[r.kind] = out.get(r.kind, 0) + 1
        return out


class Infeasible(Exception):
    """The reductions proved no solution exists. That is an answer, not a bug."""


class _State:
    """The model being chewed on, in a form that is cheap to edit."""

    def __init__(self, m: Model):
        self.sense = m.sense
        self.cost = list(m.cost)
        self.constant = m.constant
        self.cols = list(m.cols)
        self.rows = list(m.rows)
        self.live_rows = set(range(len(m.rows)))
        self.live_cols = set(range(len(m.cols)))
        self.fixed: dict[int, F] = {}
        self.log: list[Reduction] = []
        self.round = 0

    # --- helpers ---------------------------------------------------------

    def note(self, kind: str, target: str, detail: str) -> None:
        self.log.append(Reduction(self.round, kind, target, detail))

    def snapshot(self) -> Model:
        return Model(cost=tuple(self.cost), rows=tuple(self.rows),
                     cols=tuple(self.cols), sense=self.sense,
                     constant=self.constant)

    def bounds_of(self, row: Row) -> tuple[F | None, F | None]:
        return self.snapshot().row_bounds(row)

    def tighten(self, j: int, lo=None, hi=None) -> bool:
        """Raise a lower bound or lower an upper one. True if anything moved."""
        col = self.cols[j]
        new_lo, new_hi = col.lo, col.hi
        if lo is not None and (new_lo is None or lo > new_lo):
            new_lo = lo
        if hi is not None and (new_hi is None or hi < new_hi):
            new_hi = hi
        if col.integer:
            if new_lo is not None:
                new_lo = F(math.ceil(new_lo))
            if new_hi is not None:
                new_hi = F(math.floor(new_hi))
        if (new_lo, new_hi) == (col.lo, col.hi):
            return False
        if new_lo is not None and new_hi is not None and new_lo > new_hi:
            raise Infeasible(f"{col.name} has no value left between its bounds")
        self.cols[j] = replace(col, lo=new_lo, hi=new_hi)
        return True

    def fix(self, j: int, value: F, why: str) -> None:
        col = self.cols[j]
        if col.lo is not None and value < col.lo:
            raise Infeasible(f"{col.name} fixed below its lower bound")
        if col.hi is not None and value > col.hi:
            raise Infeasible(f"{col.name} fixed above its upper bound")
        self.fixed[j] = value
        self.live_cols.discard(j)
        self.constant += self.cost[j] * value
        for i in list(self.live_rows):
            row = self.rows[i]
            a = row.coef(j)
            if a == 0:
                continue
            shift = a * value
            self.rows[i] = Row(
                coefs=tuple((k, c) for k, c in row.coefs if k != j),
                lo=None if row.lo is None else row.lo - shift,
                hi=None if row.hi is None else row.hi - shift,
                name=row.name)
        self.note("fixed column", col.name, why)

    def drop_row(self, i: int, why: str) -> None:
        self.live_rows.discard(i)
        self.note("dropped row", self.rows[i].name, why)


# --- the individual reductions --------------------------------------------

def _empty_and_redundant_rows(s: _State) -> bool:
    moved = False
    for i in sorted(s.live_rows):
        row = s.rows[i]
        live = tuple((j, a) for j, a in row.coefs if j in s.live_cols)
        if not live:
            if (row.lo is not None and row.lo > 0) or (row.hi is not None and row.hi < 0):
                raise Infeasible(f"{row.name} has nothing left in it and cannot hold")
            s.drop_row(i, "every column in it has gone")
            moved = True
            continue
        lo, hi = s.bounds_of(row)
        if row.hi is not None and lo is not None and lo > row.hi:
            raise Infeasible(f"{row.name} cannot get down to its upper limit")
        if row.lo is not None and hi is not None and hi < row.lo:
            raise Infeasible(f"{row.name} cannot reach its lower limit")
        slack_below = row.lo is None or (lo is not None and lo >= row.lo)
        slack_above = row.hi is None or (hi is not None and hi <= row.hi)
        if slack_below and slack_above:
            s.drop_row(i, "the columns in it can never push it outside its limits")
            moved = True
    return moved


def _singleton_rows(s: _State) -> bool:
    moved = False
    for i in sorted(s.live_rows):
        row = s.rows[i]
        live = tuple((j, a) for j, a in row.coefs if j in s.live_cols)
        if len(live) != 1:
            continue
        j, a = live[0]
        lo = None if row.lo is None else row.lo / a
        hi = None if row.hi is None else row.hi / a
        if a < 0:
            lo, hi = hi, lo
        s.tighten(j, lo=lo, hi=hi)
        s.drop_row(i, f"one column left, so it is really a bound on {s.cols[j].name}")
        moved = True
    return moved


def _forcing_rows(s: _State) -> bool:
    """A row already at its limit when every column is at its best corner."""
    moved = False
    for i in sorted(s.live_rows):
        row = s.rows[i]
        live = [(j, a) for j, a in row.coefs if j in s.live_cols]
        if len(live) < 2:
            continue
        lo, hi = s.bounds_of(row)
        for limit, reach, corner in ((row.hi, lo, "lowest"), (row.lo, hi, "highest")):
            if limit is None or reach is None or reach != limit:
                continue
            for j, a in live:
                col = s.cols[j]
                if corner == "lowest":
                    value = col.lo if a > 0 else col.hi
                else:
                    value = col.hi if a > 0 else col.lo
                if value is None:
                    continue
                s.fix(j, value, f"{row.name} only holds if it sits at this bound")
            s.drop_row(i, "it forced every column in it and has nothing left to say")
            moved = True
            break
    return moved


def _fixed_columns(s: _State) -> bool:
    moved = False
    for j in sorted(s.live_cols):
        col = s.cols[j]
        if col.fixed:
            s.fix(j, col.lo, "its two bounds met")
            moved = True
    return moved


def _empty_columns(s: _State) -> bool:
    """A column in no remaining row is settled by its cost alone."""
    moved = False
    used = {j for i in s.live_rows for j, _ in s.rows[i].coefs if j in s.live_cols}
    for j in sorted(s.live_cols - used):
        col, c = s.cols[j], s.cost[j]
        want_low = (c > 0) == (s.sense == "min")
        value = col.lo if (c == 0 or want_low) else col.hi
        if value is None:
            raise ValueError(f"{col.name} is in no row and its cost runs off to infinity")
        s.fix(j, value, "no row mentions it, so only its cost decides")
        moved = True
    return moved


def _tighten_bounds(s: _State) -> bool:
    """What one row implies about one column, given all the others."""
    moved = False
    for i in sorted(s.live_rows):
        row = s.rows[i]
        live = [(j, a) for j, a in row.coefs if j in s.live_cols]
        if len(live) < 2:
            continue
        lo, hi = s.bounds_of(row)
        for j, a in live:
            col = s.cols[j]
            near, far = (col.lo, col.hi) if a > 0 else (col.hi, col.lo)
            rest_lo = None if (lo is None or near is None) else lo - a * near
            rest_hi = None if (hi is None or far is None) else hi - a * far
            new_hi = None if (row.hi is None or rest_lo is None) else (row.hi - rest_lo) / a
            new_lo = None if (row.lo is None or rest_hi is None) else (row.lo - rest_hi) / a
            if a < 0:
                new_lo, new_hi = new_hi, new_lo
            if s.tighten(j, lo=new_lo, hi=new_hi):
                after = s.cols[j]
                s.note("tightened bound", col.name,
                       f"{row.name} leaves it no room outside "
                       f"[{_show(after.lo)}, {_show(after.hi)}]")
                moved = True
    return moved


def _round_integers(s: _State) -> bool:
    moved = False
    for j in sorted(s.live_cols):
        col = s.cols[j]
        if not col.integer:
            continue
        lo = col.lo if col.lo is None else F(math.ceil(col.lo))
        hi = col.hi if col.hi is None else F(math.floor(col.hi))
        if (lo, hi) != (col.lo, col.hi):
            s.cols[j] = replace(col, lo=lo, hi=hi)
            if lo is not None and hi is not None and lo > hi:
                raise Infeasible(f"{col.name} has no whole number left")
            s.note("rounded bound", col.name,
                   f"whole numbers only, so [{_show(lo)}, {_show(hi)}]")
            moved = True
    return moved


def _show(v) -> str:
    return "-" if v is None else str(v)


ORDER = (_fixed_columns, _singleton_rows, _round_integers, _empty_and_redundant_rows,
         _forcing_rows, _tighten_bounds, _empty_columns)


# --- the loop --------------------------------------------------------------

def presolve(m: Model, stop_after: int | None = None) -> Presolved:
    """Apply the reductions until none of them fires.

    ``stop_after`` halts the loop early, which is only useful for showing the
    reader what the model looked like partway through.
    """
    s = _State(m)
    before = m.shape
    limit = MAX_ROUNDS if stop_after is None else min(stop_after, MAX_ROUNDS)
    try:
        for rnd in range(1, limit + 1):
            s.round = rnd
            if not any(step(s) for step in ORDER):
                break
        else:
            if stop_after is None:
                raise RuntimeError(
                    "presolve did not settle; refusing to return a half-reduced model")
    except Infeasible:
        return Presolved("infeasible", None, tuple(s.log), (), (), dict(s.fixed),
                         before, before)

    kept = tuple(sorted(s.live_cols))
    kept_rows = tuple(sorted(s.live_rows))
    where = {j: k for k, j in enumerate(kept)}
    rows = tuple(
        Row(coefs=tuple((where[j], a) for j, a in s.rows[i].coefs if j in s.live_cols),
            lo=s.rows[i].lo, hi=s.rows[i].hi, name=s.rows[i].name)
        for i in kept_rows)
    reduced = Model(cost=tuple(s.cost[j] for j in kept), rows=rows,
                    cols=tuple(s.cols[j] for j in kept), sense=s.sense,
                    constant=s.constant)
    return Presolved("reduced", reduced, tuple(s.log), kept, kept_rows,
                     dict(s.fixed), before, reduced.shape)


def postsolve(p: Presolved, reduced_x) -> tuple[F, ...]:
    """Rebuild a solution to the original model from one to the reduced model.

    Every column presolve removed was removed by being *fixed*, so this is a
    matter of putting the recorded values back in the right slots. It is short
    on purpose: a postsolve that has to be clever is a postsolve that will
    eventually be wrong.
    """
    total = len(p.kept_cols) + len(p.fixed)
    out: list[F | None] = [None] * total
    for k, j in enumerate(p.kept_cols):
        out[j] = reduced_x[k]
    for j, v in p.fixed.items():
        out[j] = v
    missing = [j for j, v in enumerate(out) if v is None]
    if missing:
        raise RuntimeError(f"postsolve has no value for columns {missing}")
    return tuple(out)
