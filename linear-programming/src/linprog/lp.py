"""Small linear programs, solved two different ways, in exact fractions.

Every program here has the shape the guide starts from: maximise c·x subject to
rows A x <= b and x >= 0. The simplex method records every corner it stands on,
because later chapters draw the walk; enumeration of corners is the slow,
obviously-correct second opinion the tests hold it to.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Sequence


def F(x) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(str(x) if isinstance(x, float) else x)


@dataclass(frozen=True)
class LP:
    c: tuple[Fraction, ...]
    A: tuple[tuple[Fraction, ...], ...]
    b: tuple[Fraction, ...]
    var_names: tuple[str, ...] = ()
    row_names: tuple[str, ...] = ()

    @staticmethod
    def build(c, A, b, var_names=(), row_names=()) -> "LP":
        return LP(tuple(map(F, c)), tuple(tuple(map(F, r)) for r in A),
                  tuple(map(F, b)), tuple(var_names), tuple(row_names))

    @property
    def n(self) -> int:
        return len(self.c)

    @property
    def m(self) -> int:
        return len(self.b)

    def value(self, x: Sequence) -> Fraction:
        return sum((ci * F(xi) for ci, xi in zip(self.c, x)), Fraction(0))

    def used(self, i: int, x: Sequence) -> Fraction:
        return sum((a * F(xi) for a, xi in zip(self.A[i], x)), Fraction(0))

    def slack(self, i: int, x: Sequence) -> Fraction:
        return self.b[i] - self.used(i, x)

    def feasible(self, x: Sequence) -> bool:
        return all(F(v) >= 0 for v in x) and all(self.slack(i, x) >= 0 for i in range(self.m))

    def with_c(self, c) -> "LP":
        return LP.build(c, self.A, self.b, self.var_names, self.row_names)

    def with_b(self, b) -> "LP":
        return LP.build(self.c, self.A, b, self.var_names, self.row_names)


def solve_square(M, rhs):
    """Gauss-Jordan in fractions; None when the rows do not pin down one point."""
    n = len(M)
    a = [list(map(F, row)) + [F(r)] for row, r in zip(M, rhs)]
    for col in range(n):
        piv = next((r for r in range(col, n) if a[r][col] != 0), None)
        if piv is None:
            return None
        a[col], a[piv] = a[piv], a[col]
        for r in range(n):
            if r != col and a[r][col] != 0:
                f = a[r][col] / a[col][col]
                a[r] = [x - f * y for x, y in zip(a[r], a[col])]
    return tuple(a[i][n] / a[i][i] for i in range(n))


def walls(lp: LP):
    """Every boundary as (coefficients, right-hand side): the rows, then x_j >= 0."""
    out = [(lp.A[i], lp.b[i]) for i in range(lp.m)]
    for j in range(lp.n):
        out.append((tuple(F(int(k == j)) for k in range(lp.n)), F(0)))
    return out


def vertices(lp: LP) -> list[tuple[Fraction, ...]]:
    """Every corner: each choice of n walls that meet in a single feasible point."""
    found = []
    ws = walls(lp)
    for pick in combinations(range(len(ws)), lp.n):
        x = solve_square([ws[k][0] for k in pick], [ws[k][1] for k in pick])
        if x is not None and lp.feasible(x) and x not in found:
            found.append(x)
    return found


def best_by_enumeration(lp: LP):
    pts = vertices(lp)
    best = max(pts, key=lp.value)
    return best, lp.value(best)


@dataclass
class Walk:
    corners: list[tuple[Fraction, ...]]   # the corner after each pivot, start included
    x: tuple[Fraction, ...]
    value: Fraction
    prices: tuple[Fraction, ...]          # one per row, read off the final table


def simplex(lp: LP, rule: str = "dantzig") -> Walk:
    """Tableau simplex from the all-zero corner (so needs b >= 0).

    rule="dantzig" enters the column with the best rate, the textbook choice;
    rule="bland" enters the lowest-numbered improving column, which cannot cycle.
    """
    if any(v < 0 for v in lp.b):
        raise ValueError("start at the origin needs every b >= 0")
    m, n = lp.m, lp.n
    T = [list(lp.A[i]) + [F(int(k == i)) for k in range(m)] + [lp.b[i]] for i in range(m)]
    z = [-v for v in lp.c] + [F(0)] * m + [F(0)]
    basis = [n + i for i in range(m)]

    def point():
        x = [F(0)] * (n + m)
        for r, col in enumerate(basis):
            x[col] = T[r][-1]
        return tuple(x[:n])

    corners = [point()]
    while True:
        improving = [j for j in range(n + m) if z[j] < 0]
        if not improving:
            break
        col = min(improving) if rule == "bland" else min(improving, key=lambda j: (z[j], j))
        rows = [r for r in range(m) if T[r][col] > 0]
        if not rows:
            raise ValueError("unbounded")
        ratio = min(T[r][-1] / T[r][col] for r in rows)
        tied = [r for r in rows if T[r][-1] / T[r][col] == ratio]
        r = min(tied, key=lambda r: basis[r])
        p = T[r][col]
        T[r] = [v / p for v in T[r]]
        for k in range(m):
            if k != r and T[k][col] != 0:
                f = T[k][col]
                T[k] = [a - f * b for a, b in zip(T[k], T[r])]
        f = z[col]
        z = [a - f * b for a, b in zip(z, T[r])]
        basis[r] = col
        corners.append(point())
    x = point()
    return Walk(corners, x, lp.value(x), tuple(z[n:n + m]))


def dual_by_enumeration(lp: LP):
    """The prices problem solved from scratch: cheapest y >= 0 with yA >= c.

    Written as its own corner search over the dual's walls, so it shares no
    code path with the simplex prices it is used to check.
    """
    m, n = lp.m, lp.n
    rows = [(tuple(lp.A[i][j] for i in range(m)), lp.c[j]) for j in range(n)]
    rows += [(tuple(F(int(k == i)) for k in range(m)), F(0)) for i in range(m)]
    best = None
    for pick in combinations(range(len(rows)), m):
        y = solve_square([rows[k][0] for k in pick], [rows[k][1] for k in pick])
        if y is None or any(v < 0 for v in y):
            continue
        if any(sum(y[i] * lp.A[i][j] for i in range(m)) < lp.c[j] for j in range(n)):
            continue
        bill = sum(y[i] * lp.b[i] for i in range(m))
        if best is None or bill < best[1]:
            best = (y, bill)
    return best
