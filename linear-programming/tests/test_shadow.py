"""Exact checks for shadow values and complementary slackness."""

import random
import re
from fractions import Fraction
from pathlib import Path

from linprog import mill as f
from linprog.lp import (LP, best_by_enumeration, dual_by_enumeration,
                        simplex, solve_square, vertices)
from linprog.modeling import two_week_inventory
from figures.fig07a_lathe_slide import wall_label_anchors
from figures.fig07b_value_curves import fair_offer_corners, offer_line_table
from test_formulation import complete_sets_lp

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "lesson.md").read_text()
FLAT = " ".join(TEXT.split())
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")


def dual_feasible_lp(primal):
    return LP.build(
        c=tuple(-value for value in primal.b),
        A=tuple(tuple(-primal.A[i][j] for i in range(primal.m))
                for j in range(primal.n)),
        b=tuple(-value for value in primal.c),
    )


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def optimal_dual_corners(primal):
    optimum = dual_by_enumeration(primal)[1]
    return {
        tuple(point) for point in vertices(dual_feasible_lp(primal))
        if dot(point, primal.b) == optimum
    }


def lathe_lp(b):
    return f.MILL.with_b((Fraction(b), f.MILL.b[1]))


def press_lp(b):
    return f.MILL.with_b((f.MILL.b[0], Fraction(b)))


def lathe_formula(b):
    return min(3 * b, 2 * b + f.MILL.b[1], 5 * f.MILL.b[1])


def press_formula(b):
    return min(5 * b, 2 * f.MILL.b[0] + b, 3 * f.MILL.b[0])


def test_every_integer_stock_has_the_exact_primal_and_dual_value():
    for b in range(51):
        lp = lathe_lp(b)
        value = lathe_formula(b)
        enumerated_point, enumerated_value = best_by_enumeration(lp)
        walked = simplex(lp)
        dual = dual_by_enumeration(lp)
        if b <= f.MILL.b[1]:
            expected_plan = (b, 0)
        elif b <= 2 * f.MILL.b[1]:
            expected_plan = (2 * f.MILL.b[1] - b, b - f.MILL.b[1])
        else:
            expected_plan = (0, f.MILL.b[1])
        assert enumerated_point == expected_plan
        assert enumerated_value == walked.value == dual[1] == value
        assert walked.x == expected_plan

    for b in range(41):
        lp = press_lp(b)
        value = press_formula(b)
        enumerated_point, enumerated_value = best_by_enumeration(lp)
        walked = simplex(lp)
        dual = dual_by_enumeration(lp)
        if b <= f.MILL.b[0] / 2:
            expected_plan = (0, b)
        elif b <= f.MILL.b[0]:
            expected_plan = (2 * b - f.MILL.b[0], f.MILL.b[0] - b)
        else:
            expected_plan = (f.MILL.b[0], 0)
        assert enumerated_point == expected_plan
        assert enumerated_value == walked.value == dual[1] == value
        assert walked.x == expected_plan


def test_the_two_middle_ranges_and_bend_ties_are_exact():
    for b in range(20, 41):
        lp = lathe_lp(b)
        value = best_by_enumeration(lp)[1]
        assert dot((Fraction(2), Fraction(1)), lp.b) == value
    for b in range(16, 33):
        lp = press_lp(b)
        value = best_by_enumeration(lp)[1]
        assert dot((Fraction(2), Fraction(1)), lp.b) == value

    assert optimal_dual_corners(lathe_lp(20)) == {
        (Fraction(2), Fraction(1)), (Fraction(3), Fraction(0))
    }
    assert optimal_dual_corners(lathe_lp(40)) == {
        (Fraction(0), Fraction(5)), (Fraction(2), Fraction(1))
    }
    assert optimal_dual_corners(press_lp(16)) == {
        (Fraction(0), Fraction(5)), (Fraction(2), Fraction(1))
    }
    assert optimal_dual_corners(press_lp(32)) == {
        (Fraction(2), Fraction(1)), (Fraction(3), Fraction(0))
    }


def test_marginal_values_are_the_differences_away_from_the_bends():
    lathe_values = [lathe_formula(b) for b in range(52)]
    press_values = [press_formula(b) for b in range(42)]
    assert all(lathe_values[b + 1] - lathe_values[b] == 3
               for b in range(0, 19))
    assert all(lathe_values[b + 1] - lathe_values[b] == 2
               for b in range(21, 39))
    assert all(lathe_values[b + 1] - lathe_values[b] == 0
               for b in range(41, 51))
    assert all(press_values[b + 1] - press_values[b] == 5
               for b in range(0, 15))
    assert all(press_values[b + 1] - press_values[b] == 1
               for b in range(17, 31))
    assert all(press_values[b + 1] - press_values[b] == 0
               for b in range(33, 41))


def test_sample_bills_match_their_best_values():
    offers = tuple(sorted(
        vertices(dual_feasible_lp(f.MILL)),
        key=lambda offer: (-offer[0], -offer[1]),
    ))
    assert offers == (
        (Fraction(3), Fraction(0)),
        (Fraction(2), Fraction(1)),
        (Fraction(0), Fraction(5)),
    )
    for b in (10, 32, 50):
        stock = (Fraction(b), f.MILL.b[1])
        bills = tuple(dot(offer, stock) for offer in offers)
        value = best_by_enumeration(lathe_lp(b))[1]
        assert bills == (
            3 * b, 2 * b + f.MILL.b[1], 5 * f.MILL.b[1]
        )
        assert value == min(bills)
    assert best_by_enumeration(lathe_lp(10))[1] == 30
    assert best_by_enumeration(lathe_lp(32))[1] == 84
    assert best_by_enumeration(lathe_lp(50))[1] == 100
    assert best_by_enumeration(press_lp(20))[1] == 84


def test_value_curve_labels_anchor_to_their_own_bill_lines():
    offers = fair_offer_corners()
    expected = {
        0: {
            (Fraction(3), Fraction(0)): ("(3, 0): 3b", (50, 150)),
            (Fraction(2), Fraction(1)): ("(2, 1): 2b + 20", (50, 120)),
            (Fraction(0), Fraction(5)): ("(0, 5): 100", (50, 100)),
        },
        1: {
            (Fraction(3), Fraction(0)): ("(3, 0): 96", (40, 96)),
            (Fraction(2), Fraction(1)): ("(2, 1): 64 + b", (40, 104)),
            (Fraction(0), Fraction(5)): ("(0, 5): 5b", (40, 200)),
        },
    }
    for axis, maximum in ((0, 50), (1, 40)):
        for line in offer_line_table(axis, maximum, offers):
            label, anchor = expected[axis][line.offer]
            assert line.label == label
            assert line.anchor == tuple(Fraction(value) for value in anchor)
            x, y = line.anchor
            assert y == line.slope * x + line.intercept


def test_wall_label_anchors_follow_their_walls_at_sampled_stocks():
    for stock in (Fraction(16), Fraction(201, 10), Fraction(32),
                  Fraction(401, 10), Fraction(44)):
        lathe_anchor, press_anchor = wall_label_anchors(stock)
        assert dot(f.MILL.A[0], lathe_anchor) == stock
        assert dot(f.MILL.A[1], press_anchor) == f.MILL.b[1]
        assert 0 <= lathe_anchor[0] <= 23
        assert 0 <= lathe_anchor[1] <= 22
        assert 0 <= press_anchor[0] <= 23
        assert 0 <= press_anchor[1] <= 22


def test_complementary_slackness_examples_and_idle_resource_prices():
    best_plan = (Fraction(8), Fraction(12))
    forced = solve_square(
        tuple(tuple(f.MILL.A[i][j] for i in range(f.MILL.m))
              for j in range(f.MILL.n)),
        f.MILL.c,
    )
    assert forced == (2, 1)
    assert f.MILL.feasible(best_plan)
    assert f.MILL.value(best_plan) == dot(forced, f.MILL.b) == 84
    assert all(
        sum((forced[i] * f.MILL.A[i][j] for i in range(f.MILL.m)),
            Fraction(0)) == f.MILL.c[j]
        for j in range(f.MILL.n)
    )
    assert all(f.MILL.slack(i, best_plan) == 0 for i in range(f.MILL.m))

    nonbest_plan = (Fraction(0), Fraction(16))
    assert f.MILL.feasible(nonbest_plan)
    idle_press = f.MILL.slack(1, nonbest_plan)
    forced_press_price = Fraction(0) if idle_press else None
    forced_five_ply = (f.MILL.c[1] - forced_press_price * f.MILL.A[1][1]) / f.MILL.A[0][1]
    assert (forced_five_ply, forced_press_price) == (
        Fraction(5, 2), Fraction(0)
    )
    priced_products = (
        forced_five_ply * f.MILL.A[0][0],
        forced_five_ply * f.MILL.A[0][1],
    )
    assert idle_press == 4
    assert forced_five_ply == Fraction(5, 2)
    assert priced_products == (Fraction(5, 2), Fraction(5))
    assert priced_products[0] < f.MILL.c[0]
    assert f.MILL.value(nonbest_plan) == 80

    sets = complete_sets_lp()
    sets_plan = (Fraction(10), Fraction(10), Fraction(10))
    sets_prices = (Fraction(0), Fraction(1, 2),
                   Fraction(1, 2), Fraction(1, 2))
    covered = tuple(
        sum((sets_prices[i] * sets.A[i][j] for i in range(sets.m)),
            Fraction(0))
        for j in range(sets.n)
    )
    assert covered == sets.c
    assert sets.slack(0, sets_plan) == 2
    assert sets_prices[0] == 0
    assert dot(sets_prices, sets.b) == 10

    inventory = two_week_inventory()
    inventory_plan, inventory_value = best_by_enumeration(inventory)
    inventory_dual = dual_by_enumeration(inventory)
    assert inventory.slack(3, inventory_plan) == 12
    assert inventory_dual[0][3] == 0
    assert inventory_value == inventory_dual[1] == 130


def random_bounded_lp(rng):
    n = rng.choice((2, 3))
    point = tuple(Fraction(rng.randint(1, 5)) for _ in range(n))
    rows = []
    bounds = []
    for _ in range(3):
        row = tuple(Fraction(rng.randint(1, 5)) for _ in range(n))
        rows.append(row)
        bounds.append(dot(row, point) + rng.randint(0, 5))
    for j in range(n):
        row = tuple(Fraction(int(i == j)) for i in range(n))
        rows.append(row)
        bounds.append(10)
    objective = tuple(Fraction(rng.randint(1, 8)) for _ in range(n))
    return LP.build(objective, rows, bounds), point


def dual_prices(lp, y):
    return tuple(
        sum((y[i] * lp.A[i][j] for i in range(lp.m)), Fraction(0))
        for j in range(lp.n)
    )


def gaps(lp, x, y):
    gap1 = sum(((price - value) * amount
                for price, value, amount
                in zip(dual_prices(lp, y), lp.c, x)), Fraction(0))
    gap2 = sum((y[i] * lp.slack(i, x) for i in range(lp.m)), Fraction(0))
    return gap1, gap2


def test_two_hundred_random_bounded_programs_obey_both_rules_and_gap_identity():
    rng = random.Random(71207)
    for _ in range(200):
        lp, feasible_point = random_bounded_lp(rng)
        assert lp.feasible(feasible_point)
        optimum_x, optimum_value = best_by_enumeration(lp)
        optimum_y, dual_value = dual_by_enumeration(lp)
        prices = dual_prices(lp, optimum_y)
        assert lp.feasible(optimum_x)
        assert all(value >= 0 for value in optimum_y)
        assert all(prices[j] >= lp.c[j] for j in range(lp.n))
        assert optimum_value == dual_value
        assert gaps(lp, optimum_x, optimum_y) == (0, 0)
        assert all((prices[j] - lp.c[j]) * optimum_x[j] == 0
                   for j in range(lp.n))
        assert all(optimum_y[i] * lp.slack(i, optimum_x) == 0
                   for i in range(lp.m))

        nonbest_x = feasible_point
        if lp.value(nonbest_x) == optimum_value:
            nonbest_x = tuple(Fraction(0) for _ in range(lp.n))
        extra = [rng.randint(0, 2) for _ in range(lp.m)]
        if not any(extra):
            extra[0] = 1
        nonbest_y = tuple(optimum_y[i] + extra[i] for i in range(lp.m))
        assert lp.feasible(nonbest_x)
        assert all(value >= 0 for value in nonbest_y)
        assert all(price >= lp.c[j]
                   for j, price in enumerate(dual_prices(lp, nonbest_y)))
        gap1, gap2 = gaps(lp, nonbest_x, nonbest_y)
        assert gap1 >= 0 and gap2 >= 0
        assert gap1 + gap2 == dot(nonbest_y, lp.b) - lp.value(nonbest_x)
        assert lp.value(nonbest_x) < optimum_value


def test_chapter_seven_numbers_and_figure_paths_match_the_computation():
    offers = tuple(sorted(
        vertices(dual_feasible_lp(f.MILL)),
        key=lambda offer: (-offer[0], -offer[1]),
    ))
    for b in (10, 32, 50):
        bills = tuple(dot(offer, (Fraction(b), f.MILL.b[1]))
                      for offer in offers)
        value = best_by_enumeration(lathe_lp(b))[1]
        if b == 10:
            sentence = (
                f"At b = {b} the bills are {bills[0]}, {bills[1]} and "
                f"{bills[2]}, and the value is {value}."
            )
        else:
            sentence = (
                f"At b = {b} they are {bills[0]}, {bills[1]} and "
                f"{bills[2]}, and it is {value}."
            )
        assert sentence in FLAT

    bend20 = best_by_enumeration(lathe_lp(20))[1]
    bend40 = best_by_enumeration(lathe_lp(40))[1]
    press16 = best_by_enumeration(press_lp(16))[1]
    press32 = best_by_enumeration(press_lp(32))[1]
    assert bend20 == 60 and bend40 == 100
    assert press16 == 80 and press32 == 96
    assert best_by_enumeration(lathe_lp(32))[1] == 84
    assert best_by_enumeration(press_lp(20))[1] == 84
    assert f"b = 20 (value {bend20})" in FLAT
    assert f"b = 40 (value {bend40})" in FLAT
    assert f"b = 16 (value {press16})" in FLAT
    assert f"b = 32 (value {press32})" in FLAT
    assert f"({32}, {best_by_enumeration(lathe_lp(32))[1]}) is marked" in FLAT
    assert f"({20}, {best_by_enumeration(press_lp(20))[1]}) marked" in FLAT
    assert (f"At b = 20 the offers (3, 0) and (2, 1) bill the same "
            f"{bend20}, and the next hour is worth "
            f"{lathe_formula(21) - lathe_formula(20)} while the last one "
            f"was worth {lathe_formula(20) - lathe_formula(19)}.") in FLAT
    assert "Each extra lathe hour adds exactly 2 thousand roubles" in FLAT
    assert "For lathe stock b between 20 and 40" in FLAT
    assert "the best value is the smallest of the three" in FLAT
    assert "slopes 3, 2 and 0" in FLAT
    assert "slopes 5, 1 and 0" in FLAT
    assert "left 2 lathe hours idle" in FLAT
    assert "left 12 lathe hours idle" in FLAT
    assert "y1 = 5/2" in FLAT

    referenced = {path for _, path in IMAGE.findall(TEXT)}
    for name in ("lathe_slide.gif", "value_curves.png"):
        relative = f"chapters/07-one-more/{name}"
        assert relative in referenced
        assert (ROOT / relative).is_file()
