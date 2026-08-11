"""The second program hiding inside the first one.

Everything the guide claims about duality is computed here rather than
asserted: the dual program itself, the bound a set of prices proves, which
rows are doing the work at the optimum, and -- when a system has no solution at
all -- the short proof of that.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .lp import LP, F, Solution, solve


def dual(lp: LP) -> LP:
    """The dual program, built by the swap the guide describes in words.

    One row of the primal becomes one variable of the dual, one variable of the
    primal becomes one row of the dual, the objective and the right-hand side
    trade places, and the inequalities turn around.  Only the two symmetric
    forms are built here, which are the only two the guide uses; anything else
    would need the sign rules for free variables and would be a different
    lesson.
    """
    if lp.sense == "max":
        assert all(o == "<=" for o in lp.op), "dual() wants a max with only <= rows"
        new_sense, new_op = "min", ">="
    else:
        assert all(o == ">=" for o in lp.op), "dual() wants a min with only >= rows"
        new_sense, new_op = "max", "<="

    transpose = [[lp.A[i][j] for i in range(lp.m)] for j in range(lp.n)]
    return LP.build(
        c=lp.b,
        A=transpose,
        b=lp.c,
        op=new_op,
        sense=new_sense,
        var_names=tuple(f"price of {name}" for name in lp.row_names),
        row_names=tuple(lp.var_names),
    )


def mixture(lp: LP, y) -> tuple[tuple[Fraction, ...], Fraction]:
    """Add up the rows with weights *y*: the coefficients, and the total.

    This is the whole trick of weak duality in one function.  Scale each row of
    a max program by a non-negative weight and add them, and you get one new
    inequality that every feasible plan still obeys.  If its coefficients cover
    the objective's, its right-hand side is a ceiling on the objective.
    """
    weights = [F(v) for v in y]
    coeffs = tuple(
        sum((w * lp.A[i][j] for i, w in enumerate(weights)), Fraction(0))
        for j in range(lp.n)
    )
    total = sum((w * lp.b[i] for i, w in enumerate(weights)), Fraction(0))
    return coeffs, total


def covers_objective(lp: LP, y) -> bool:
    """Do these weights produce coefficients at or above every objective coefficient?"""
    coeffs, _ = mixture(lp, y)
    return all(F(v) >= 0 for v in y) and all(a >= c for a, c in zip(coeffs, lp.c))


def ceiling_from(lp: LP, y) -> Fraction | None:
    """The ceiling these weights prove, or None if they prove nothing."""
    if not covers_objective(lp, y):
        return None
    return mixture(lp, y)[1]


@dataclass(frozen=True)
class SlacknessLine:
    kind: str          # "row" or "variable"
    name: str
    slack: Fraction    # left-over capacity, or the amount the dual row overshoots
    dual: Fraction     # the matching multiplier, or the activity level
    tight: bool

    @property
    def consistent(self) -> bool:
        """Complementary slackness: at most one of the pair is allowed to be nonzero."""
        return self.slack == 0 or self.dual == 0


def complementary_slackness(lp: LP, x, y) -> list[SlacknessLine]:
    """Pair every row with its price and every variable with its dual row.

    The rule the guide states -- a resource with any left over is worth nothing,
    and a product that earns less than its ingredients cost is not made -- is
    just this list with every line consistent.
    """
    xs = [F(v) for v in x]
    ys = [F(v) for v in y]
    out: list[SlacknessLine] = []
    for i in range(lp.m):
        s = lp.slack(i, xs)
        out.append(SlacknessLine("row", lp.row_names[i], s, ys[i], s == 0))
    for j in range(lp.n):
        ingredient_cost = sum((ys[i] * lp.A[i][j] for i in range(lp.m)), Fraction(0))
        over = ingredient_cost - lp.c[j]
        out.append(SlacknessLine("variable", lp.var_names[j], over, xs[j], over == 0))
    return out


def duality_gap(lp: LP, x, y) -> Fraction:
    """What the plan earns, subtracted from what the prices charge."""
    return sum((F(yi) * bi for yi, bi in zip(y, lp.b)), Fraction(0)) - lp.objective(x)


# --- when there is no plan at all ------------------------------------------

def farkas_certificate(lp: LP) -> tuple[Fraction, ...] | None:
    """Weights proving the rows contradict each other, or None if they do not.

    For rows that all read <= with every variable at or above zero, a system is
    unsolvable exactly when some non-negative mix of the rows produces
    coefficients that are all at or above zero while the totals add to
    something below zero: "a non-negative amount of everything is at most a
    negative number", which nothing satisfies.  Searching for that mix is
    itself a small linear program, solved here with the same simplex code.
    """
    assert lp.sense == "max" and all(o == "<=" for o in lp.op)
    m, n = lp.m, lp.n
    # min b·y over { y >= 0, A^T y >= 0, sum y = 1 }.  The last row just keeps
    # the search bounded: the certificates form a cone, so any point on it does.
    rows = [[lp.A[i][j] for i in range(m)] for j in range(n)]
    rows.append([Fraction(1)] * m)
    ops = [">="] * n + ["="]
    rhs = [Fraction(0)] * n + [Fraction(1)]
    search = LP.build(c=lp.b, A=rows, b=rhs, op=ops, sense="min")
    found = solve(search)
    if not found.ok or found.value >= 0:
        return None
    return found.x


def verify_farkas(lp: LP, y) -> bool:
    ys = [F(v) for v in y]
    coeffs, total = mixture(lp, ys)
    return all(v >= 0 for v in ys) and all(a >= 0 for a in coeffs) and total < 0


def solve_pair(lp: LP) -> tuple[Solution, Solution]:
    """Solve the program and its dual independently, from scratch, both ways.

    Nothing is copied from one solve into the other.  The point of the guide is
    that the two numbers agree; the point of returning both is that the tests
    can check they really do, rather than checking a number against itself.
    """
    return solve(lp), solve(dual(lp))
