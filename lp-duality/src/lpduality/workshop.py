"""The one example the whole guide runs on.

A workshop makes tables and chairs out of three things it does not have enough
of.  Every number the guide quotes about it -- the best plan, the prices, the
range a price survives -- is computed here and nowhere else, so the prose, the
figures and the playable pages cannot quietly disagree with each other.

The example is deliberately small enough to draw on a page and deliberately not
symmetric: one of its three rows has capacity left over at the optimum, which
is what gives complementary slackness something to say.
"""

from __future__ import annotations

from fractions import Fraction

from .duality import complementary_slackness, dual
from .lp import LP, solve
from .sensitivity import price_range, value_function

# --- the workshop ----------------------------------------------------------

PRODUCTS = ("tables", "chairs")
RESOURCES = ("planks", "hours", "saw time")

UNITS = {"planks": "planks", "hours": "hours", "saw time": "saw-hours"}

#            planks  hours  saw
RECIPE = {"tables": (4, 2, 3),
          "chairs": (2, 3, 1)}
STOCK = {"planks": 44, "hours": 30, "saw time": 32}
PROFIT = {"tables": 30, "chairs": 20}

PRIMAL = LP.build(
    c=[PROFIT["tables"], PROFIT["chairs"]],
    A=[[RECIPE["tables"][i], RECIPE["chairs"][i]] for i in range(3)],
    b=[STOCK[r] for r in RESOURCES],
    op="<=",
    sense="max",
    var_names=PRODUCTS,
    row_names=RESOURCES,
)

DUAL = dual(PRIMAL)

# --- the answers, computed once --------------------------------------------

_primal = solve(PRIMAL)
_dual = solve(DUAL)

PLAN = _primal.x                  # (9 tables, 4 chairs)
BEST_PROFIT = _primal.value       # 350
PRICES = _dual.x                  # (25/4 per plank, 5/2 per hour, 0 per saw-hour)
PRICE_TOTAL = _dual.value         # 350, the same number

SLACKNESS = complementary_slackness(PRIMAL, PLAN, PRICES)

WOOD, LABOUR, SAW = 0, 1, 2

# how far the plank price holds, and the whole shape of the value curve
WOOD_FROM, WOOD_TO, WOOD_PRICE = price_range(PRIMAL, WOOD, 0, 60)
WOOD_CURVE = value_function(PRIMAL, WOOD, 0, 60)


# --- the two ladders the guide animates ------------------------------------

# Real plans, each one better than the last. Every one is honestly feasible, so
# each is a genuine floor under the answer: "at least this much is possible."
ASCENT: tuple[tuple[tuple[int, int], str], ...] = (
    ((0, 0), "make nothing"),
    ((0, 10), "chairs only, until the hours run out"),
    ((Fraction(32, 3), 0), "tables only, until the saw runs out"),
    ((10, 2), "mostly tables"),
    ((9, 4), "the best plan"),
)

# Real price sets, each one cheaper than the last. Every one covers both
# recipes, so each is a genuine ceiling over the answer: "no more than this."
DESCENT: tuple[tuple[tuple, str], ...] = (
    ((0, 0, 30), "charge for saw time alone"),
    ((10, 0, 0), "charge for planks alone"),
    ((8, 2, 0), "planks, and a little for hours"),
    ((7, 3, 0), "cheaper planks, dearer hours"),
    ((Fraction(13, 2), Fraction(14, 5), 0), "closer"),
    ((Fraction(25, 4), Fraction(5, 2), 0), "the cheapest honest prices"),
)


# --- two ways for a program to have no answer ------------------------------

# An order for twelve tables, in a workshop whose planks cannot make eleven.
IMPOSSIBLE = LP.build(
    c=[PROFIT["tables"], PROFIT["chairs"]],
    A=[[RECIPE["tables"][i], RECIPE["chairs"][i]] for i in range(3)] + [[-1, 0]],
    b=[STOCK[r] for r in RESOURCES] + [-12],
    op="<=",
    sense="max",
    var_names=PRODUCTS,
    row_names=RESOURCES + ("the order",),
)

# Chairs with no ceiling on them: profit runs away, and no price set can cover
# the chair recipe, so the dual has no answer either.
ENDLESS = LP.build(
    c=[PROFIT["tables"], PROFIT["chairs"]],
    A=[[2, -1]],
    b=[10],
    op="<=",
    sense="max",
    var_names=PRODUCTS,
    row_names=("a balance rule",),
)


def money(x, cents: bool = False) -> str:
    """Render a Fraction as money, exactly, without ever printing a rounded cent.

    ``cents=True`` keeps the trailing zeroes, which is what a column of figures
    wants; the default drops them, which is what a sentence wants.  Anything
    that is not a whole number of cents is shown as the fraction it really is
    rather than being quietly rounded into one.
    """
    q = Fraction(x)
    if (q * 100).denominator != 1:
        return f"${q.numerator}/{q.denominator}"
    if q.denominator == 1 and not cents:
        return f"${q.numerator:,}"
    return f"${float(q):,.2f}"


def number(x) -> str:
    """Render a Fraction the way the prose says it out loud."""
    q = Fraction(x)
    if q.denominator == 1:
        return str(q.numerator)
    if (q * 100).denominator == 1:
        return f"{float(q):g}"
    return f"{q.numerator}/{q.denominator}"
