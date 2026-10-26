"""The farm every chapter uses: two crops, a fixed amount of land and water.

It is Tovey's section 6.2.1 example with a story attached, chosen because its
best plan mixes both crops, the greedy guess (all corn) is wrong by a quotable
amount, and both prices come out as whole numbers.
"""

from fractions import Fraction

from .lp import LP, best_by_enumeration, simplex, vertices

CROPS = ("wheat", "corn")
RESOURCES = ("water", "land")
PROFIT = (3, 5)            # thousand dollars an acre
USE = {"wheat": (1, 1), "corn": (2, 1)}   # (water, land) per acre
STOCK = (32, 20)           # units of water, acres of land

FARM = LP.build(c=PROFIT, A=[[1, 2], [1, 1]], b=STOCK,
                var_names=CROPS, row_names=RESOURCES)

CORNERS = vertices(FARM)
BEST, BEST_PROFIT = best_by_enumeration(FARM)
WALK = simplex(FARM)
PRICES = WALK.prices

# the obvious plan: corn earns more an acre, so plant as much corn as the
# water and land allow, and nothing else
ALL_CORN_ACRES = min(STOCK[0] / Fraction(USE["corn"][0]), STOCK[1] / Fraction(USE["corn"][1]))
ALL_CORN = (Fraction(0), ALL_CORN_ACRES)
ALL_CORN_PROFIT = FARM.value(ALL_CORN)
ALL_CORN_IDLE_LAND = FARM.slack(1, ALL_CORN)


def money(thousands) -> str:
    v = Fraction(thousands) * 1000
    assert v.denominator == 1, v
    return f"${int(v):,}"


def acres(v) -> str:
    v = Fraction(v)
    return str(v.numerator) if v.denominator == 1 else f"{float(v):g}"
