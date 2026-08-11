"""Solving the model, twice over, by routes that share no code.

The first route converts to the exact rational simplex from the duality guide
and runs branch and bound on top of it. The second enumerates every whole
point inside the column bounds and checks it. The second is hopeless above toy
sizes, which is the point: it cannot be wrong in the same way the first one
can, so the tests can use it to hold the first one honest.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from fractions import Fraction as F

from lpduality.lp import LP, solve as solve_lp_exact

from .model import Model


@dataclass
class Answer:
    status: str                  # "optimal" | "infeasible"
    x: tuple[F, ...] = ()
    value: F | None = None
    nodes: int = 0               # branch-and-bound nodes, for the MIP route


def to_lp(m: Model) -> tuple[LP, tuple[F, ...]]:
    """Rewrite as the duality guide's LP: every variable at or above zero.

    Returns the LP and the shift, so a solution can be read back.
    """
    if any(c.lo is None for c in m.cols):
        raise ValueError("every column needs a finite lower bound to shift from")
    shift = tuple(c.lo for c in m.cols)

    A, b, ops, names = [], [], [], []
    for row in m.rows:
        dense = [F(0)] * m.n_cols
        for j, a in row.coefs:
            dense[j] = a
        offset = sum((a * shift[j] for j, a in row.coefs), F(0))
        if row.hi is not None:
            A.append(dense); b.append(row.hi - offset); ops.append("<=")
            names.append(f"{row.name}<=")
        if row.lo is not None:
            A.append(dense); b.append(row.lo - offset); ops.append(">=")
            names.append(f"{row.name}>=")
    for j, col in enumerate(m.cols):
        if col.hi is not None:
            dense = [F(0)] * m.n_cols
            dense[j] = F(1)
            A.append(dense); b.append(col.hi - shift[j]); ops.append("<=")
            names.append(f"{col.name}<=")

    lp = LP.build(c=list(m.cost), A=A, b=b, op=ops, sense=m.sense,
                  var_names=[c.name for c in m.cols], row_names=names)
    return lp, shift


def relax(m: Model) -> Answer:
    """The LP relaxation: integrality ignored."""
    if m.n_cols == 0:
        return Answer("optimal", (), m.constant)
    lp, shift = to_lp(m)
    sol = solve_lp_exact(lp)
    if not sol.ok:
        return Answer("infeasible" if sol.status == "infeasible" else sol.status)
    x = tuple(s + v for s, v in zip(shift, sol.x))
    return Answer("optimal", x, m.objective(x))


def _fractional(m: Model, x) -> int | None:
    for j, col in enumerate(m.cols):
        if col.integer and x[j].denominator != 1:
            return j
    return None


def solve_mip(m: Model, node_cap: int = 20_000) -> Answer:
    """Branch and bound over the relaxation. Counts the nodes it opened."""
    import math
    from dataclasses import replace

    better = (lambda a, b: a > b) if m.sense == "max" else (lambda a, b: a < b)
    best: Answer = Answer("infeasible")
    stack = [m]
    nodes = 0
    while stack:
        node = stack.pop()
        nodes += 1
        if nodes > node_cap:
            raise RuntimeError("branch and bound ran away; refusing to guess")
        r = relax(node)
        if r.status != "optimal":
            continue
        if best.value is not None and not better(r.value, best.value):
            continue                                   # bound cannot beat it
        j = _fractional(node, r.x)
        if j is None:
            if best.value is None or better(r.value, best.value):
                best = Answer("optimal", r.x, r.value)
            continue
        v = r.x[j]
        for lo, hi in ((None, F(math.floor(v))), (F(math.ceil(v)), None)):
            cols = list(node.cols)
            col = cols[j]
            new_lo = col.lo if lo is None else (lo if col.lo is None else max(col.lo, lo))
            new_hi = col.hi if hi is None else (hi if col.hi is None else min(col.hi, hi))
            if new_lo is not None and new_hi is not None and new_lo > new_hi:
                continue
            cols[j] = replace(col, lo=new_lo, hi=new_hi)
            stack.append(replace(node, cols=tuple(cols)))
    return Answer(best.status, best.x, best.value, nodes)


def brute_force(m: Model) -> Answer:
    """Every whole point in the box, checked. Independent of everything above."""
    ranges = []
    for col in m.cols:
        if not col.integer or col.lo is None or col.hi is None:
            raise ValueError("brute force needs every column integral and boxed")
        ranges.append(range(int(col.lo), int(col.hi) + 1))
    best_x, best_v = None, None
    better = (lambda a, b: a > b) if m.sense == "max" else (lambda a, b: a < b)
    for point in itertools.product(*ranges):
        x = tuple(F(v) for v in point)
        if not m.is_feasible(x):
            continue
        v = m.objective(x)
        if best_v is None or better(v, best_v):
            best_x, best_v = x, v
    if best_v is None:
        return Answer("infeasible")
    return Answer("optimal", best_x, best_v)
