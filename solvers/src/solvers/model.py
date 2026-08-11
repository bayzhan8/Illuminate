"""A small mixed-integer model, held exactly.

The rows are ranges rather than inequalities: every row carries a lower and an
upper limit, either of which may be absent. That is how real solvers store a
model, and it matters here because presolve spends most of its time comparing
a row's reachable range against its stated one.

Everything is `Fraction`. Presolve is exactly the kind of code where floating
point turns "this row can never be violated" into "this row is violated by
1e-16", so the arithmetic has to be exact for the claims to mean anything.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from fractions import Fraction as F
from typing import Iterable, Optional

Num = Optional[F]          # None is an absent bound: minus or plus infinity


@dataclass(frozen=True)
class Row:
    """lo <= sum(coef * x) <= hi, with either limit optionally absent."""

    coefs: tuple[tuple[int, F], ...]      # (column index, coefficient), sorted
    lo: Num
    hi: Num
    name: str

    @property
    def columns(self) -> tuple[int, ...]:
        return tuple(j for j, _ in self.coefs)

    def coef(self, j: int) -> F:
        for k, a in self.coefs:
            if k == j:
                return a
        return F(0)


@dataclass(frozen=True)
class Col:
    """lo <= x <= hi, optionally required to be a whole number."""

    lo: Num
    hi: Num
    integer: bool
    name: str

    @property
    def fixed(self) -> bool:
        return self.lo is not None and self.lo == self.hi


@dataclass(frozen=True)
class Model:
    """minimise (or maximise) cost·x over the rows and column bounds."""

    cost: tuple[F, ...]
    rows: tuple[Row, ...]
    cols: tuple[Col, ...]
    sense: str = "min"
    constant: F = F(0)       # picked up as columns get substituted out

    # --- shape -----------------------------------------------------------

    @property
    def n_rows(self) -> int:
        return len(self.rows)

    @property
    def n_cols(self) -> int:
        return len(self.cols)

    @property
    def nonzeros(self) -> int:
        return sum(len(r.coefs) for r in self.rows)

    @property
    def shape(self) -> tuple[int, int, int]:
        return self.n_rows, self.n_cols, self.nonzeros

    # --- evaluation ------------------------------------------------------

    def objective(self, x: Iterable[F]) -> F:
        return self.constant + sum((c * v for c, v in zip(self.cost, x)), F(0))

    def row_activity(self, row: Row, x) -> F:
        return sum((a * x[j] for j, a in row.coefs), F(0))

    def violations(self, x) -> list[str]:
        """Every reason *x* is not a solution. Empty means it is one."""
        bad = []
        for j, col in enumerate(self.cols):
            if col.lo is not None and x[j] < col.lo:
                bad.append(f"{col.name} below its lower bound")
            if col.hi is not None and x[j] > col.hi:
                bad.append(f"{col.name} above its upper bound")
            if col.integer and x[j].denominator != 1:
                bad.append(f"{col.name} is not a whole number")
        for row in self.rows:
            act = self.row_activity(row, x)
            if row.lo is not None and act < row.lo:
                bad.append(f"{row.name} under its lower limit")
            if row.hi is not None and act > row.hi:
                bad.append(f"{row.name} over its upper limit")
        return bad

    def is_feasible(self, x) -> bool:
        return not self.violations(x)

    # --- the range a row can reach, given the current column bounds -------

    def row_bounds(self, row: Row) -> tuple[Num, Num]:
        """(smallest, largest) activity the row can take. None where unbounded.

        This single routine is what almost every reduction below is built on:
        compare what a row *can* reach against what it is *allowed* to reach.
        """
        low: Num = F(0)
        high: Num = F(0)
        for j, a in row.coefs:
            col = self.cols[j]
            near, far = (col.lo, col.hi) if a > 0 else (col.hi, col.lo)
            low = None if (low is None or near is None) else low + a * near
            high = None if (high is None or far is None) else high + a * far
        return low, high

    def with_col(self, j: int, **kw) -> "Model":
        cols = list(self.cols)
        cols[j] = replace(cols[j], **kw)
        return replace(self, cols=tuple(cols))


def build(cost, rows, cols, sense="min") -> Model:
    """Readable constructor: rows as (name, {col: coef}, lo, hi)."""
    names = [c[0] for c in cols]
    index = {name: j for j, name in enumerate(names)}
    built_cols = tuple(
        Col(lo=None if lo is None else F(lo), hi=None if hi is None else F(hi),
            integer=integer, name=name)
        for name, lo, hi, integer in cols)
    built_rows = tuple(
        Row(coefs=tuple(sorted((index[k], F(v)) for k, v in coefs.items())),
            lo=None if lo is None else F(lo),
            hi=None if hi is None else F(hi), name=name)
        for name, coefs, lo, hi in rows)
    return Model(cost=tuple(F(c) for c in cost), rows=built_rows,
                 cols=built_cols, sense=sense)
