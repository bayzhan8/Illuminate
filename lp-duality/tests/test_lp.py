"""The mathematics has to be right.

Two habits run through this file.  Where a claim can be checked against a
method that shares no code with the one under test, it is: the simplex answers
are checked against brute-force corner enumeration, and the prices are checked
against the dual program solved as a separate problem.  And where a claim is
about two numbers being *equal*, the comparison is exact, because everything
here is a Fraction and there is no tolerance to hide in.
"""

import random
from fractions import Fraction

import pytest

from lpduality import workshop as w
from lpduality.duality import (ceiling_from, complementary_slackness, dual,
                               duality_gap, farkas_certificate, mixture,
                               solve_pair, verify_farkas)
from lpduality.lp import LP, solve, solve_by_enumeration, vertices


def random_workshop(rng, n=None, m=None) -> LP:
    """A workshop that is always feasible (build nothing) and always bounded."""
    n = n or rng.randint(2, 4)
    m = m or rng.randint(2, 4)
    return LP.build(
        c=[rng.randint(1, 40) for _ in range(n)],
        A=[[rng.randint(1, 9) for _ in range(n)] for _ in range(m)],
        b=[rng.randint(5, 60) for _ in range(m)],
        op="<=", sense="max")


# --- the solver ------------------------------------------------------------

def test_the_workshop_has_the_answer_the_guide_quotes():
    found = solve(w.PRIMAL)
    assert found.status == "optimal"
    assert found.x == (Fraction(9), Fraction(4))
    assert found.value == Fraction(350)


def test_simplex_agrees_with_looking_at_every_corner():
    """The two routines share no code, so agreeing is worth something."""
    rng = random.Random(3)
    for _ in range(120):
        lp = random_workshop(rng, n=2)
        assert solve(lp).value == solve_by_enumeration(lp).value


def test_the_answer_really_is_a_plan_you_could_carry_out():
    found = solve(w.PRIMAL)
    assert w.PRIMAL.is_feasible(found.x)


def test_everything_stays_an_exact_fraction():
    found = solve(w.PRIMAL)
    assert all(isinstance(v, Fraction) for v in found.x)
    assert all(isinstance(v, Fraction) for v in found.prices)
    assert isinstance(found.value, Fraction)


def test_a_degenerate_program_terminates():
    """More rules than needed meeting at one corner. Bland's rule cannot cycle,
    and a solver without it can sit here forever."""
    lp = LP.build(c=[1, 1], A=[[1, 1], [1, 1], [2, 2], [1, 0]],
                  b=[4, 4, 8, 4], op="<=", sense="max")
    assert solve(lp).value == Fraction(4)


# --- the two programs ------------------------------------------------------

def test_the_dual_of_the_dual_is_the_original():
    back = dual(dual(w.PRIMAL))
    assert (back.c, back.A, back.b, back.sense) == \
           (w.PRIMAL.c, w.PRIMAL.A, w.PRIMAL.b, w.PRIMAL.sense)


def test_prices_from_the_tableau_match_the_dual_solved_from_scratch():
    plan, prices = solve_pair(w.PRIMAL)
    assert plan.prices == prices.x
    assert plan.value == prices.value


def test_weak_duality_holds_for_every_plan_and_every_price_list():
    """Any plan is a floor and any covering price list is a ceiling, and this
    is true of bad plans and expensive prices too -- that is the whole point."""
    rng = random.Random(17)
    for _ in range(300):
        plan = (Fraction(rng.randint(0, 11)), Fraction(rng.randint(0, 10)))
        if not w.PRIMAL.is_feasible(plan):
            continue
        y = [Fraction(rng.randint(0, 12)) for _ in range(3)]
        ceiling = ceiling_from(w.PRIMAL, y)
        if ceiling is None:
            continue
        assert w.PRIMAL.objective(plan) <= ceiling


def test_strong_duality_on_many_unrelated_programs():
    rng = random.Random(5)
    for _ in range(200):
        lp = random_workshop(rng)
        plan, prices = solve(lp), solve(dual(lp))
        assert plan.ok and prices.ok
        assert plan.value == prices.value, "the gap must be exactly zero"


def test_the_gap_here_is_zero_and_not_merely_small():
    assert duality_gap(w.PRIMAL, w.PLAN, w.PRICES) == 0


def test_complementary_slackness_pairs_up():
    for line in complementary_slackness(w.PRIMAL, w.PLAN, w.PRICES):
        assert line.consistent, f"{line.name} has both slack and a price"


def test_the_spare_resource_is_the_one_worth_nothing():
    spare = [i for i in range(w.PRIMAL.m) if w.PRIMAL.slack(i, w.PLAN) > 0]
    assert spare == [w.SAW]
    assert w.PRICES[w.SAW] == 0
    assert all(w.PRICES[i] > 0 for i in (w.WOOD, w.LABOUR))


def test_complementary_slackness_holds_on_random_programs():
    rng = random.Random(23)
    for _ in range(150):
        lp = random_workshop(rng)
        plan, prices = solve(lp), solve(dual(lp))
        for line in complementary_slackness(lp, plan.x, prices.x):
            assert line.consistent


# --- the edges -------------------------------------------------------------

def test_profit_that_runs_away_leaves_the_dual_with_nothing():
    assert solve(w.ENDLESS).status == "unbounded"
    assert solve(dual(w.ENDLESS)).status == "infeasible"


def test_an_impossible_order_is_impossible():
    assert solve(w.IMPOSSIBLE).status == "infeasible"


def test_the_impossible_order_has_a_short_proof():
    y = farkas_certificate(w.IMPOSSIBLE)
    assert y is not None
    assert verify_farkas(w.IMPOSSIBLE, y)


def test_the_proof_the_chapter_talks_through_is_a_real_one():
    """Chapter 9 walks through one specific certificate. The search is free to
    return a different valid one, so the chapter's is checked on its own."""
    y = (Fraction(1, 4), 0, 0, Fraction(1))
    assert verify_farkas(w.IMPOSSIBLE, y)
    coefficients, total = mixture(w.IMPOSSIBLE, y)
    assert coefficients == (Fraction(0), Fraction(1, 2))
    assert total == Fraction(-1)


def test_a_feasible_program_has_no_such_proof():
    assert farkas_certificate(w.PRIMAL) is None


# --- what one more is worth ------------------------------------------------

def test_the_plank_price_is_the_slope_of_the_value_curve():
    assert w.WOOD_PRICE == w.PRICES[w.WOOD] == Fraction(25, 4)


def test_the_value_curve_has_the_three_pieces_the_guide_draws():
    slopes = [s.slope for s in w.WOOD_CURVE]
    assert slopes == [Fraction(10), Fraction(25, 4), Fraction(0)]
    bends = [s.end for s in w.WOOD_CURVE[:-1]]
    assert bends == [Fraction(20), Fraction(316, 7)]


def test_the_curve_bends_one_way_only():
    """More of a resource is never worth more per unit than the last lot."""
    slopes = [s.slope for s in w.WOOD_CURVE]
    assert all(a > b for a, b in zip(slopes, slopes[1:]))


def test_the_price_range_brackets_where_the_workshop_actually_is():
    assert w.WOOD_FROM <= w.PRIMAL.b[w.WOOD] <= w.WOOD_TO
    assert (w.WOOD_FROM, w.WOOD_TO) == (Fraction(20), Fraction(316, 7))


@pytest.mark.parametrize("stock,expected", [
    (Fraction(20), Fraction(200)),
    (Fraction(44), Fraction(350)),
    (Fraction(316, 7), Fraction(2500, 7)),
    (Fraction(60), Fraction(2500, 7)),
])
def test_the_curve_agrees_with_re_solving_at_the_interesting_points(stock, expected):
    from lpduality.sensitivity import value_at
    assert value_at(w.PRIMAL, w.WOOD, stock) == expected


def test_a_grid_too_coarse_to_see_a_bend_complains_instead_of_lying():
    """The bend at 316/7 is missed by a grid of three, and that has to be an
    error rather than a smooth-looking wrong answer."""
    from lpduality.sensitivity import value_function
    with pytest.raises(ValueError):
        value_function(w.PRIMAL, w.WOOD, 0, 60, samples=3)
