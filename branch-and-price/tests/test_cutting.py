"""Mathematics, verified by a route that shares no code with the thing tested.

Column generation is checked against solving the master over every pattern.
Branch-and-price is checked against brute-force integer optimisation over every
pattern. Both comparisons are useless above about thirty patterns, so they run
only on instances where the slow method still terminates.

Runtime is dominated by test_branch_and_price_agrees_with_brute_force. Leave it
that way.
"""

import itertools
import math
from fractions import Fraction

import pytest

from bandp import mill as m
from bandp.cutting import (Instance, all_patterns, column_generation,
                           count_patterns, master, price, reduced_cost,
                           starting_patterns)
from bandp.search import (branch_and_price, emergency_price,
                          integer_optimum_by_enumeration, solve_node)
from lpduality.lp import solve


def small_instances():
    """Every instance the slow checks can afford, deduplicated."""
    out = []
    for width in (16, 20, 25):
        for widths in itertools.combinations(range(4, width // 2 + 1), 3):
            for demands in ((3, 4, 5), (2, 5, 7), (6, 3, 4)):
                out.append(Instance(width, widths, demands))
    return out


# --- patterns --------------------------------------------------------------

def test_every_pattern_fits_on_a_board():
    for pattern in m.PATTERNS:
        assert m.BOARDS.waste(pattern) >= 0


def test_every_pattern_is_maximal():
    """A pattern with room for another piece is one nobody would ever choose."""
    for pattern in m.PATTERNS:
        assert m.BOARDS.is_maximal(pattern)


def test_counting_patterns_agrees_with_listing_them():
    for width in (16, 20, 25, 30):
        for widths in ((4, 9, 10), (5, 7, 11), (3, 8, 13)):
            listed = len(all_patterns(Instance(width, widths, (1, 1, 1)),
                                      maximal_only=False))
            assert listed == count_patterns(width, widths)


def test_the_small_order_has_the_six_patterns_the_guide_draws():
    assert len(m.PATTERNS) == 6


# --- the relaxations -------------------------------------------------------

def test_column_generation_matches_solving_over_every_pattern():
    """The loop's answer must equal the answer you get by writing the whole
    model down, which is the only thing that makes skipping columns safe."""
    for inst in small_instances():
        loop = column_generation(inst)[-1].value
        whole = solve(master(inst, all_patterns(inst))).value
        assert loop == whole, f"{inst.widths} {inst.demands}"


def test_the_loop_stops_because_nothing_is_left_rather_than_by_running_out():
    for inst in small_instances():
        last = column_generation(inst)[-1]
        assert not last.added
        assert last.best_value <= 1
        assert reduced_cost(last.best_value) >= 0


def test_every_round_but_the_last_really_did_improve_things():
    values = [r.value for r in m.ROUNDS]
    assert all(a >= b for a, b in zip(values, values[1:])), values
    assert values[0] > values[-1]


def test_the_pattern_model_is_never_weaker_than_the_obvious_one():
    """P_IP inside P_DW inside P_LP, checked rather than asserted."""
    for inst in small_instances():
        dw = column_generation(inst)[-1].value
        naive = m.material_bound(inst)
        integer = integer_optimum_by_enumeration(inst)
        assert naive <= dw, f"{inst.widths} {inst.demands}"
        assert dw <= integer, f"{inst.widths} {inst.demands}"


def test_the_guides_two_bounds_are_the_quoted_ones():
    assert m.NAIVE_BOUND == Fraction(136, 25)
    assert m.DW_BOUND == Fraction(13, 2)
    assert math.ceil(m.NAIVE_BOUND) == 6
    assert math.ceil(m.DW_BOUND) == 7


def test_the_stronger_bound_is_what_rules_out_six_boards():
    """The whole reason chapter 3 exists."""
    assert math.ceil(m.NAIVE_BOUND) < math.ceil(m.DW_BOUND) == m.ANSWER


# --- pricing ---------------------------------------------------------------

def test_the_knapsack_returns_a_pattern_that_fits():
    for inst in small_instances():
        for duals in ([Fraction(1, 3)] * 3, [Fraction(1)] * 3, [Fraction(0)] * 3):
            _, pattern = price(inst, duals)
            assert inst.fits(pattern)


def test_the_knapsack_really_finds_the_best_pattern():
    """Checked against scoring every pattern one at a time."""
    import random
    rng = random.Random(4)
    for inst in small_instances()[:40]:
        for _ in range(4):
            duals = [Fraction(rng.randint(0, 8), rng.randint(1, 6))
                     for _ in range(inst.m)]
            value, _ = price(inst, duals)
            best = max(sum(d * n for d, n in zip(duals, p))
                       for p in all_patterns(inst, maximal_only=False))
            assert value == best


def test_a_pattern_already_in_the_model_is_never_worth_more_than_one():
    """At optimality the prices satisfy the dual constraint of every column
    that is present -- that is what the restricted master guarantees."""
    last = m.ROUNDS[-1]
    for pattern in last.patterns:
        assert sum(d * n for d, n in zip(last.duals, pattern)) <= 1


# --- the search ------------------------------------------------------------

def test_branch_and_price_agrees_with_brute_force():
    """The check that caught two real bugs. Do not delete it."""
    for inst in small_instances():
        assert branch_and_price(inst).best == integer_optimum_by_enumeration(inst), \
            f"{inst.width} {inst.widths} {inst.demands}"


def test_the_answer_to_the_small_order_is_seven_boards():
    assert m.ANSWER == 7
    assert sum(m.SEARCH.plan.values()) == 7


def test_the_plan_really_fills_the_order():
    produced = [0] * m.BOARDS.m
    for pattern, count in m.SEARCH.plan.items():
        for i, n in enumerate(pattern):
            produced[i] += n * count
    assert all(p >= d for p, d in zip(produced, m.BOARDS.demands)), produced


def test_the_root_of_the_tree_is_the_relaxation():
    assert m.SEARCH.root_bound == m.DW_BOUND


def test_a_node_that_bans_a_pattern_is_not_reported_infeasible():
    """The second of the two traps: an under-supplied restricted master is not
    an infeasible node, and reading it as one loses real answers."""
    from bandp.search import Bound
    pattern = m.PATTERNS[0]
    here, _ = solve_node(m.BOARDS, (Bound(pattern, 0, "<="),))
    assert here.ok
    assert here.value >= m.DW_BOUND


def test_emergency_columns_are_priced_out_of_any_real_answer():
    assert emergency_price(m.BOARDS) > m.ANSWER


# --- the bigger order ------------------------------------------------------

def test_the_loop_ignores_most_of_the_bigger_order():
    assert m.SCALE_HELD == 6            # columns the loop ends holding
    assert m.SCALE_TOUCHED == 5         # of which this many are maximal
    assert len(m.SCALE_PATTERNS) == 30
    assert m.SCALE_TOUCHED < len(m.SCALE_PATTERNS) / 4


def test_the_mill_is_the_size_the_guide_says():
    assert m.MILL_PATTERNS == 3_972_952_644_549
