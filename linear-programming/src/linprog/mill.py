"""The mill every chapter uses: two sheets, a fixed amount of lathe and press time.

It is Tovey's section 6.2.1 example with a story attached, chosen because its
best plan mixes both sheets, the greedy guess (all 5-ply) is wrong by a
quotable amount, and both resource prices come out as whole numbers.
"""

from fractions import Fraction

from .lp import LP, best_by_enumeration, simplex, vertices

PRODUCTS = ("3-ply", "5-ply")
RESOURCES = ("lathe", "press")
VALUE = (3, 5)            # thousand roubles per batch
USE = {"3-ply": (1, 1), "5-ply": (2, 1)}   # (lathe, press) hours per batch
STOCK = (32, 20)           # lathe hours, press hours

MILL = LP.build(c=VALUE, A=[[1, 2], [1, 1]], b=STOCK,
                var_names=PRODUCTS, row_names=RESOURCES)

CORNERS = vertices(MILL)
BEST, BEST_VALUE = best_by_enumeration(MILL)
WALK = simplex(MILL)
PRICES = WALK.prices

# the obvious plan: 5-ply has more value per batch, so make as much as the
# lathe and press allow, and nothing else
ALL_FIVE_BATCHES = min(STOCK[0] / Fraction(USE["5-ply"][0]),
                       STOCK[1] / Fraction(USE["5-ply"][1]))
ALL_FIVE = (Fraction(0), ALL_FIVE_BATCHES)
ALL_FIVE_VALUE = MILL.value(ALL_FIVE)
ALL_FIVE_IDLE_PRESS = MILL.slack(1, ALL_FIVE)


def money(thousands) -> str:
    v = Fraction(thousands) * 1000
    assert v.denominator == 1, v
    return f"{int(v):,} roubles"


def batches(v) -> str:
    v = Fraction(v)
    return str(v.numerator) if v.denominator == 1 else f"{float(v):g}"
