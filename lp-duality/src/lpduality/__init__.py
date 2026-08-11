"""Linear programming duality: exact-arithmetic LP, its dual, and sensitivity.

    from lpduality import workshop
    workshop.BEST_PROFIT   # 350
    workshop.PRICES        # (25/4, 5/2, 0)
"""

from .lp import LP, Solution, solve, solve_by_enumeration, vertices
from .duality import (ceiling_from, complementary_slackness, dual, duality_gap,
                      farkas_certificate, mixture, solve_pair, verify_farkas)
from .sensitivity import Segment, price_range, value_at, value_function, with_rhs

__all__ = [
    "LP", "Solution", "solve", "solve_by_enumeration", "vertices",
    "dual", "mixture", "ceiling_from", "complementary_slackness", "duality_gap",
    "farkas_certificate", "verify_farkas", "solve_pair",
    "Segment", "value_function", "value_at", "with_rhs", "price_range",
]
