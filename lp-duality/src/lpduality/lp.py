"""Linear programs, and a simplex method that never rounds anything.

Every number here is a :class:`fractions.Fraction`.  That is not fussiness: the
whole guide turns on two quantities being *equal*, and a reader who is told
"350 and 350, which are the same number" deserves that to be true rather than
true to six decimals.  Floating point would put 349.99999999999994 in one of
those two places, and the one claim the guide is built on would become a claim
about a tolerance.

The solver is a textbook two-phase tableau simplex with Bland's rule.  Bland's
rule is slower than the usual steepest-ascent choice and is used anyway,
because it is the pivoting rule that provably cannot cycle.  Speed is not a
concern at this size, and a solver that silently loops forever on a degenerate
problem would be a bad thing to hand someone who is here to learn.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Iterable, Sequence

Number = Fraction | int | str | float


def F(x: Number) -> Fraction:
    """Coerce to an exact Fraction.

    Floats are accepted and converted through their decimal string, so 0.1
    becomes 1/10 rather than the binary value that is actually a hair above it.
    """
    if isinstance(x, Fraction):
        return x
    if isinstance(x, float):
        return Fraction(str(x))
    return Fraction(x)


# --- the model -------------------------------------------------------------

@dataclass(frozen=True)
class LP:
    """max (or min) c·x subject to the listed rows, with every x at or above zero.

    Rows are held exactly as written, ``op`` and all, because the guide shows
    the reader the rows as written and any silent rewriting here would make the
    pictures disagree with the prose.
    """

    c: tuple[Fraction, ...]
    A: tuple[tuple[Fraction, ...], ...]
    b: tuple[Fraction, ...]
    op: tuple[str, ...]
    sense: str = "max"
    var_names: tuple[str, ...] = ()
    row_names: tuple[str, ...] = ()

    @staticmethod
    def build(c, A, b, op="<=", sense="max", var_names=(), row_names=()) -> "LP":
        m = len(A)
        ops = tuple([op] * m) if isinstance(op, str) else tuple(op)
        lp = LP(
            c=tuple(F(v) for v in c),
            A=tuple(tuple(F(v) for v in row) for row in A),
            b=tuple(F(v) for v in b),
            op=ops,
            sense=sense,
            var_names=tuple(var_names) or tuple(f"x{j + 1}" for j in range(len(c))),
            row_names=tuple(row_names) or tuple(f"r{i + 1}" for i in range(m)),
        )
        lp.validate()
        return lp

    @property
    def n(self) -> int:
        return len(self.c)

    @property
    def m(self) -> int:
        return len(self.A)

    def validate(self) -> None:
        assert self.sense in ("max", "min"), self.sense
        assert len(self.b) == self.m == len(self.op) == len(self.row_names)
        assert len(self.var_names) == self.n
        assert all(len(row) == self.n for row in self.A), "ragged constraint matrix"
        assert all(o in ("<=", ">=", "=") for o in self.op), self.op

    # --- evaluation ------------------------------------------------------

    def objective(self, x: Sequence[Number]) -> Fraction:
        return sum((ci * F(xi) for ci, xi in zip(self.c, x)), Fraction(0))

    def row_value(self, i: int, x: Sequence[Number]) -> Fraction:
        return sum((a * F(xi) for a, xi in zip(self.A[i], x)), Fraction(0))

    def slack(self, i: int, x: Sequence[Number]) -> Fraction:
        """How much of row *i* is left over: positive means the row is not tight."""
        gap = self.b[i] - self.row_value(i, x)
        return gap if self.op[i] == "<=" else -gap

    def is_feasible(self, x: Sequence[Number]) -> bool:
        if any(F(xi) < 0 for xi in x):
            return False
        for i in range(self.m):
            lhs, rhs = self.row_value(i, x), self.b[i]
            if self.op[i] == "<=" and lhs > rhs:
                return False
            if self.op[i] == ">=" and lhs < rhs:
                return False
            if self.op[i] == "=" and lhs != rhs:
                return False
        return True


@dataclass
class Solution:
    status: str                       # "optimal" | "infeasible" | "unbounded"
    x: tuple[Fraction, ...] = ()
    value: Fraction | None = None
    prices: tuple[Fraction, ...] = ()  # one multiplier per row, as written
    basis: tuple[int, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == "optimal"


# --- exact linear algebra --------------------------------------------------

def solve_exact(M: list[list[Fraction]], rhs: list[Fraction]) -> list[Fraction]:
    """Gaussian elimination with exact arithmetic; M must be square and invertible."""
    n = len(M)
    aug = [list(M[i]) + [rhs[i]] for i in range(n)]
    for col in range(n):
        piv = next((r for r in range(col, n) if aug[r][col] != 0), None)
        if piv is None:
            raise ValueError("singular matrix")
        aug[col], aug[piv] = aug[piv], aug[col]
        p = aug[col][col]
        aug[col] = [v / p for v in aug[col]]
        for r in range(n):
            if r != col and aug[r][col] != 0:
                f = aug[r][col]
                aug[r] = [a - f * b for a, b in zip(aug[r], aug[col])]
    return [aug[i][n] for i in range(n)]


# --- canonical form --------------------------------------------------------

@dataclass
class _Canonical:
    """max c·x, A x <= b, x >= 0 -- plus how to map its rows back to the original."""

    c: list[Fraction]
    A: list[list[Fraction]]
    b: list[Fraction]
    source: list[tuple[int, Fraction]]  # canonical row -> (original row, weight)
    flip_objective: bool


def _canonicalise(lp: LP) -> _Canonical:
    """Rewrite any LP as a maximisation with only <= rows.

    ">=" rows are negated.  "=" rows become a <= and a >= pair, so an equality's
    multiplier is recovered as the difference of the pair's, which is how it
    ends up free in sign -- exactly what the textbook rule says.
    """
    flip = lp.sense == "min"
    c = [-v for v in lp.c] if flip else list(lp.c)
    A: list[list[Fraction]] = []
    b: list[Fraction] = []
    source: list[tuple[int, Fraction]] = []
    for i, op in enumerate(lp.op):
        if op in ("<=", "="):
            A.append(list(lp.A[i]))
            b.append(lp.b[i])
            source.append((i, Fraction(1)))
        if op in (">=", "="):
            A.append([-v for v in lp.A[i]])
            b.append(-lp.b[i])
            source.append((i, Fraction(-1)))
    return _Canonical(c=c, A=A, b=b, source=source, flip_objective=flip)


# --- the simplex method ----------------------------------------------------

def _pivot(T: list[list[Fraction]], r: int, col: int) -> None:
    p = T[r][col]
    T[r] = [v / p for v in T[r]]
    for i in range(len(T)):
        if i != r and T[i][col] != 0:
            f = T[i][col]
            T[i] = [a - f * b for a, b in zip(T[i], T[r])]


def _price_out(T, basis, cost) -> None:
    """Rebuild the objective row so every basic column reads zero in it."""
    width = len(T[0])
    T[0] = [-v for v in cost] + [Fraction(0)] * (width - len(cost))
    for i, col in enumerate(basis, start=1):
        if T[0][col] != 0:
            f = T[0][col]
            T[0] = [a - f * b for a, b in zip(T[0], T[i])]


def _iterate(T, basis, ncols) -> str:
    """Bland's rule: lowest-index improving column, ties in the ratio test
    broken by lowest basic index. Cannot cycle, so this always terminates."""
    while True:
        entering = next((j for j in range(ncols) if T[0][j] < 0), None)
        if entering is None:
            return "optimal"
        best = None
        for i in range(1, len(T)):
            if T[i][entering] > 0:
                ratio = T[i][ncols] / T[i][entering]
                key = (ratio, basis[i - 1])
                if best is None or key < best[0]:
                    best = (key, i)
        if best is None:
            return "unbounded"
        row = best[1]
        _pivot(T, row, entering)
        basis[row - 1] = entering


def solve(lp: LP) -> Solution:
    """Solve, and return the optimal plan together with one multiplier per row.

    The multipliers are not read out of the final tableau.  They are recovered
    by solving ``B^T y = c_B`` against an untouched copy of the standard-form
    columns, which sidesteps every sign convention the tableau accumulates on
    the way.  Two routes to the same numbers is the point: the tests check this
    one against the dual program solved from scratch.
    """
    can = _canonicalise(lp)
    m, n = len(can.A), len(can.c)
    total = n + m  # structural variables, then one slack per row

    # untouched standard-form columns [A | I], used only to recover prices
    M = [row + [Fraction(1) if j == i else Fraction(0) for j in range(m)]
         for i, row in enumerate(can.A)]
    cost_std = list(can.c) + [Fraction(0)] * m

    # tableau rows, negated where needed so every right-hand side is >= 0
    rows, needs_artificial = [], []
    for i in range(m):
        row = list(M[i]) + [can.b[i]]
        if can.b[i] < 0:
            row = [-v for v in row]
            needs_artificial.append(i)
        rows.append(row)

    n_art = len(needs_artificial)
    art_cols = {}
    for k, i in enumerate(needs_artificial):
        art_cols[i] = total + k
    for i, row in enumerate(rows):
        extra = [Fraction(0)] * n_art
        if i in art_cols:
            extra[art_cols[i] - total] = Fraction(1)
        rows[i] = row[:-1] + extra + [row[-1]]

    width = total + n_art
    basis = [art_cols[i] if i in art_cols else n + i for i in range(m)]
    T = [[Fraction(0)] * (width + 1)] + rows

    if n_art:
        phase1 = [Fraction(0)] * total + [Fraction(-1)] * n_art
        _price_out(T, basis, phase1)
        _iterate(T, basis, width)
        if T[0][width] != 0:
            return Solution(status="infeasible")
        # push any artificial still sitting in the basis at zero back out
        for i in range(1, m + 1):
            if basis[i - 1] >= total:
                col = next((j for j in range(total) if T[i][j] != 0), None)
                if col is None:
                    continue  # a redundant row; harmless, leave it be
                _pivot(T, i, col)
                basis[i - 1] = col
        for i in range(len(T)):  # drop the artificial columns
            T[i] = T[i][:total] + [T[i][width]]
        width = total

    _price_out(T, basis, cost_std)
    status = _iterate(T, basis, width)
    if status == "unbounded":
        return Solution(status="unbounded")

    x_full = [Fraction(0)] * total
    for i, col in enumerate(basis):
        if col < total:
            x_full[col] = T[i + 1][width]
    x = tuple(x_full[:n])
    value = sum((ci * xi for ci, xi in zip(can.c, x)), Fraction(0))

    # prices: solve B^T y = c_B against the pristine columns
    B_T = [[M[r][col] for r in range(m)] for col in basis]
    c_B = [cost_std[col] for col in basis]
    y_can = solve_exact(B_T, c_B)

    prices = [Fraction(0)] * lp.m
    for k, (orig, weight) in enumerate(can.source):
        prices[orig] += weight * y_can[k]
    if can.flip_objective:
        value = -value
        prices = [-p for p in prices]

    return Solution(status="optimal", x=x, value=value,
                    prices=tuple(prices), basis=tuple(basis))


# --- a second opinion ------------------------------------------------------

def vertices(lp: LP) -> list[tuple[Fraction, ...]]:
    """Every corner of the feasible region, by brute force.

    Takes each pair of boundary lines (constraints and the two axes), intersects
    them, and keeps the point if it satisfies everything.  Hopeless past a
    handful of variables and completely independent of the simplex code, which
    is the only reason it exists: the tests solve small programs both ways and
    insist on the same answer.
    """
    from itertools import combinations

    assert lp.n == 2, "the brute-force check is only written for two variables"
    lines = [(row[0], row[1], rhs) for row, rhs in zip(lp.A, lp.b)]
    lines += [(Fraction(-1), Fraction(0), Fraction(0)),
              (Fraction(0), Fraction(-1), Fraction(0))]
    out = []
    for (a1, b1, r1), (a2, b2, r2) in combinations(lines, 2):
        det = a1 * b2 - a2 * b1
        if det == 0:
            continue
        x = (r1 * b2 - r2 * b1) / det
        y = (a1 * r2 - a2 * r1) / det
        if lp.is_feasible((x, y)) and (x, y) not in out:
            out.append((x, y))
    return out


def solve_by_enumeration(lp: LP) -> Solution:
    pts = vertices(lp)
    if not pts:
        return Solution(status="infeasible")
    pick = (max if lp.sense == "max" else min)(pts, key=lp.objective)
    return Solution(status="optimal", x=pick, value=lp.objective(pick))
