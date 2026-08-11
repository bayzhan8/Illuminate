"""A simplex method whose pivoting rule you can change, and count steps for.

The guide's central claim is that the exponential worst case belongs to a
*rule*, not to the method. Making the rule a parameter is the only honest way
to show that: same problem, same code, same arithmetic, one substitution, and
the step count goes from linear to doubling.

Exact rationals throughout, so a step count is a step count and not an artefact
of rounding near a degenerate vertex.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from typing import Callable

Rule = Callable[[list, int], int | None]


@dataclass
class Result:
    x: tuple
    value: F
    steps: int
    visited: list          # the vertex at each step, for drawing the walk


def _pivot(T: list[list[F]], row: int, col: int) -> None:
    piece = T[row][col]
    T[row] = [v / piece for v in T[row]]
    for i in range(len(T)):
        if i != row and T[i][col] != 0:
            factor = T[i][col]
            T[i] = [a - factor * b for a, b in zip(T[i], T[row])]


def dantzig(objective: list[F], width: int) -> int | None:
    """Take the column that improves the objective fastest per unit.

    Dantzig's original rule, and the one Klee and Minty built their cube
    against. It is greedy about the immediate rate of improvement and pays no
    attention to how far it will be able to move.
    """
    best, at = F(0), None
    for j in range(width):
        if objective[j] < best:
            best, at = objective[j], j
    return at


def bland(objective: list[F], width: int) -> int | None:
    """Take the lowest-numbered column that improves anything at all.

    Slower per step in practice and provably cannot cycle, which is why the
    other guides in this repository use it.
    """
    for j in range(width):
        if objective[j] < 0:
            return j
    return None


def steepest_edge(objective: list[F], width: int, tableau=None) -> int | None:
    """Improvement per unit of movement rather than per unit of variable.

    A stand-in for the family of rules real solvers use. It costs more per
    iteration and usually takes far fewer of them.
    """
    if tableau is None:
        return dantzig(objective, width)
    best_score, at = None, None
    for j in range(width):
        if objective[j] >= 0:
            continue
        length = sum(row[j] ** 2 for row in tableau[1:]) + 1
        score = objective[j] ** 2 / length
        if best_score is None or score > best_score:
            best_score, at = score, j
    return at


def solve(c, A, b, rule: Rule = dantzig, limit: int = 100_000) -> Result:
    """Maximise c·x subject to Ax <= b, x >= 0, counting the corners visited.

    Written for a problem with non-negative right-hand sides, which is all the
    guide needs and lets the slack basis start feasible with no phase one to
    confuse the step count.
    """
    c = [F(v) for v in c]
    A = [[F(v) for v in row] for row in A]
    b = [F(v) for v in b]
    assert all(v >= 0 for v in b), "this walk starts from the origin"
    rows, cols = len(A), len(c)
    width = cols + rows

    T = [[-v for v in c] + [F(0)] * rows + [F(0)]]
    for i, row in enumerate(A):
        slack = [F(1) if j == i else F(0) for j in range(rows)]
        T.append(list(row) + slack + [b[i]])
    basis = [cols + i for i in range(rows)]

    def current() -> tuple:
        x = [F(0)] * cols
        for i, col in enumerate(basis):
            if col < cols:
                x[col] = T[i + 1][width]
        return tuple(x)

    visited = [current()]
    for step in range(limit):
        entering = (steepest_edge(T[0], width, T) if rule is steepest_edge
                    else rule(T[0], width))
        if entering is None:
            return Result(current(), T[0][width], step, visited)
        best = None
        for i in range(1, rows + 1):
            if T[i][entering] > 0:
                ratio = T[i][width] / T[i][entering]
                key = (ratio, basis[i - 1])
                if best is None or key < best[0]:
                    best = (key, i)
        if best is None:
            raise ValueError("unbounded")
        _pivot(T, best[1], entering)
        basis[best[1] - 1] = entering
        visited.append(current())
    raise RuntimeError("did not terminate within the step limit")


# --- the cube --------------------------------------------------------------

def klee_minty(n: int) -> tuple[list, list, list]:
    """A squashed n-dimensional cube with 2^n corners, in the standard form.

    maximise  sum of 2^(n-j) x_j
    subject to, for each i:  2 * sum_{j<i} 10^(i-j) x_j  +  x_i  <=  100^(i-1)

    Every one of its 2^n corners is a vertex of the feasible region, and the
    deformation is chosen so that the greedy rule is tempted into all of them
    before arriving at the answer. Nothing about the region is pathological --
    it is a cube. What is pathological is how a particular rule reads it.
    """
    c = [F(2) ** (n - j - 1) for j in range(n)]
    A, b = [], []
    for i in range(n):
        row = [F(2) * F(10) ** (i - j) for j in range(i)] + [F(1)] + [F(0)] * (n - i - 1)
        A.append(row)
        b.append(F(100) ** i)
    return c, A, b


def corner_count(n: int) -> int:
    return 2 ** n
