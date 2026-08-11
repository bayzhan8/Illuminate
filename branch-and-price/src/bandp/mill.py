"""The instances this guide runs on, and every number it quotes about them.

Three of them, doing three different jobs, in the spirit of learning on
something you can hold before meeting something you cannot:

``BOARDS`` is small enough to draw every pattern on one page.  It is where the
reader watches the loop work.

``SCALE`` is small enough to solve exactly and large enough that column
generation visibly ignores most of it -- it settles having looked at six
patterns out of thirty.

``MILL`` is never solved here at all.  It exists so that the number of patterns
can be counted and printed, because that number is the reason any of this
machinery exists.
"""

from __future__ import annotations

import math
from fractions import Fraction

from .cutting import (Instance, all_patterns, column_generation, count_patterns,
                      starting_patterns)
from .search import branch_and_price, integer_optimum_by_enumeration

# --- the three instances ---------------------------------------------------

BOARDS = Instance(width=25, widths=(4, 9, 10), demands=(3, 6, 7),
                  name="the small order")

SCALE = Instance(width=55, widths=(7, 9, 16, 17), demands=(4, 7, 5, 9),
                 name="the bigger order")

MILL_ROLL = 5600
MILL_WIDTHS = (135, 108, 93, 42, 51, 76, 29, 63, 87, 119)
MILL_PATTERNS = count_patterns(MILL_ROLL, MILL_WIDTHS)


def material_bound(inst: Instance) -> Fraction:
    """What the obvious model's relaxation gives: total width over roll width.

    It is the answer you get from assigning pieces to rolls and relaxing, and
    it amounts to pretending a piece can be poured rather than cut -- that the
    leftover at the end of one roll can be carried to the next.  It is a real
    lower bound and it is usually far too low.
    """
    return Fraction(sum(w * b for w, b in zip(inst.widths, inst.demands)),
                    inst.width)


# --- everything the prose quotes, computed once ----------------------------

PATTERNS = all_patterns(BOARDS)              # the six maximal patterns
ROUNDS = column_generation(BOARDS)           # the loop, round by round
DW_BOUND = ROUNDS[-1].value                  # 13/2
NAIVE_BOUND = material_bound(BOARDS)         # 136/25
SEARCH = branch_and_price(BOARDS)
ANSWER = SEARCH.best                         # 7 boards

SCALE_PATTERNS = all_patterns(SCALE)
SCALE_ROUNDS = column_generation(SCALE)
SCALE_TOUCHED = len(SCALE_ROUNDS[-1].patterns)
SCALE_DW = SCALE_ROUNDS[-1].value
SCALE_NAIVE = material_bound(SCALE)
SCALE_SEARCH = branch_and_price(SCALE)


def rolls(value) -> str:
    """A count of rolls, exactly: whole when it is whole, a fraction when not."""
    q = Fraction(value)
    if q.denominator == 1:
        return f"{q.numerator}"
    whole, rest = divmod(q.numerator, q.denominator)
    return f"{whole} and {rest}/{q.denominator}"


def decimal(value, places: int = 3) -> str:
    return f"{float(Fraction(value)):.{places}f}"


def thousands(n: int) -> str:
    return f"{n:,}"
