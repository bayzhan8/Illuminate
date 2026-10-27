"""The mathematics, each claim reached by two routes that share no code."""

import random
from fractions import Fraction

import pytest

from linprog import mill as f
from linprog.lp import LP, best_by_enumeration, dual_by_enumeration, simplex, vertices


def random_lp(rng):
    n, m = 2, rng.randint(1, 4)
    A = [[rng.randint(1, 6) for _ in range(n)] for _ in range(m)]
    b = [rng.randint(4, 40) for _ in range(m)]
    c = [rng.randint(1, 9) for _ in range(n)]
    return LP.build(c, A, b)


def test_the_mill_has_the_four_corners_the_table_lists():
    assert sorted(f.CORNERS) == [(0, 0), (0, 16), (8, 12), (20, 0)]


def test_simplex_and_enumeration_agree_on_the_mill():
    for rule in ("dantzig", "bland"):
        walk = simplex(f.MILL, rule)
        assert walk.x == f.BEST == (8, 12)
        assert walk.value == f.BEST_VALUE == 84


@pytest.mark.parametrize("rule", ["dantzig", "bland"])
def test_simplex_and_enumeration_agree_on_random_mills(rule):
    rng = random.Random(7)
    for _ in range(300):
        lp = random_lp(rng)
        assert simplex(lp, rule).value == best_by_enumeration(lp)[1]


def test_every_step_of_the_walk_is_a_corner_and_goes_uphill():
    rng = random.Random(3)
    for _ in range(200):
        lp = random_lp(rng)
        walk = simplex(lp)
        corners = vertices(lp)
        assert all(p in corners for p in walk.corners)
        values = [lp.value(p) for p in walk.corners]
        assert values == sorted(values)


def test_the_hero_walk_is_the_one_drawn():
    assert f.WALK.corners == [(0, 0), (0, 16), (8, 12)]


def test_prices_from_the_walk_match_the_prices_problem_solved_fresh():
    rng = random.Random(11)
    for lp in [f.MILL] + [random_lp(rng) for _ in range(200)]:
        y, bill = dual_by_enumeration(lp)
        walk = simplex(lp)
        assert bill == walk.value
        assert sum(p * s for p, s in zip(walk.prices, lp.b)) == walk.value


def test_the_greedy_plan_is_worse_by_the_amount_quoted():
    assert f.ALL_FIVE == (0, 16)
    assert f.ALL_FIVE_VALUE == 80
    assert f.ALL_FIVE_IDLE_PRESS == 4
    assert f.BEST_VALUE - f.ALL_FIVE_VALUE == 4


def test_the_swap_in_chapter_two_keeps_lathe_time_and_gains_a_thousand():
    swap = (Fraction(2), Fraction(-1))   # two more batches of 3-ply, one less of 5-ply
    assert f.MILL.A[0][0] * swap[0] + f.MILL.A[0][1] * swap[1] == 0
    assert f.MILL.A[1][0] * swap[0] + f.MILL.A[1][1] * swap[1] == 1
    assert f.MILL.value(swap) == 1


def test_equal_values_make_the_press_edge_tie():
    even = f.MILL.with_c((1, 1))
    tied = [p for p in vertices(even) if even.value(p) == best_by_enumeration(even)[1]]
    assert sorted(tied) == [(8, 12), (20, 0)]
    assert best_by_enumeration(even)[1] == 20


def test_the_value_arrow_is_the_prices_times_the_walls_arrows():
    combo = tuple(sum(f.PRICES[i] * f.MILL.A[i][j] for i in range(f.MILL.m))
                  for j in range(f.MILL.n))
    assert f.PRICES == (2, 1) and combo == f.MILL.c == (3, 5)
    assert all(p > 0 for p in f.PRICES)


def test_the_arrow_proof_bounds_every_plan():
    # c·x = 84 + sum_i y_i (a_i·x - b_i) <= 84, checked on a grid of plans
    for t in range(0, 21):
        for five in range(0, 17):
            x = (Fraction(t), Fraction(five))
            if f.MILL.feasible(x):
                rhs = f.BEST_VALUE - sum(f.PRICES[i] * f.MILL.slack(i, x) for i in range(f.MILL.m))
                assert f.MILL.value(x) == rhs <= f.BEST_VALUE


def test_every_plan_on_the_lathe_wall_has_the_same_shadow():
    a, b = f.MILL.A[0], f.MILL.b[0]
    for t in range(0, 21):
        x = (Fraction(t), (b - t) / 2)
        assert a[0] * x[0] + a[1] * x[1] == b
    off = (Fraction(21), Fraction(21, 2))
    assert a[0] * off[0] + a[1] * off[1] > b
