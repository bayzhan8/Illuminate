"""Exact checks for the extra rows and yes-or-no models."""

import math
from fractions import Fraction
from pathlib import Path

from exact_radicals import SQRT5, Sqrt5
from linprog import mill as f
from linprog.lp import LP, best_by_enumeration, dual_by_enumeration, simplex
from linprog.modeling import (SETUP_MOVE_STEPS, CHEAP_OVERTIME_PRICE,
                              DEAR_OVERTIME_PRICE,
                              concave_overtime, either_or, overtime_cost,
                              overtime_epigraph, overtime_tiers, ratio,
                              scenarios, semicontinuous,
                              semicontinuous_relaxation, setup, setup_bound_at,
                              setup_relaxation, shortfall, solve_binary,
                              two_week_inventory)

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "lesson.md").read_text()
FLAT = " ".join(TEXT.split())


def exact_lp_routes(lp):
    enumerated = best_by_enumeration(lp)
    walked = simplex(lp)
    assert (walked.x, walked.value) == enumerated
    return enumerated


def enumeration_and_dual(lp):
    point, value = best_by_enumeration(lp)
    dual = dual_by_enumeration(lp)
    assert dual is not None
    assert dual[1] == value
    return point, value


def test_overtime_tiers_epigraph_and_concave_branches():
    assert exact_lp_routes(f.MILL) == ((8, 12), Fraction(84))
    assert (CHEAP_OVERTIME_PRICE, DEAR_OVERTIME_PRICE) == (1, 3)

    tier_point, tier_value = exact_lp_routes(overtime_tiers())
    assert tier_point == (4, 16, 4, 0)
    assert tier_value == 88
    epigraph_point, epigraph_value = exact_lp_routes(overtime_epigraph())
    assert epigraph_point == (4, 16, 4, 4)
    assert epigraph_value == 88

    reversed_lp = overtime_tiers(DEAR_OVERTIME_PRICE, CHEAP_OVERTIME_PRICE)
    reversed_point, reversed_value = exact_lp_routes(reversed_lp)
    assert reversed_value == 88
    assert reversed_point == (4, 16, 0, 4)

    no_second_crew = concave_overtime(0)
    called_second_crew = concave_overtime(1)
    assert exact_lp_routes(no_second_crew.lp) == (
        (8, 12, 0, 0), Fraction(84)
    )
    assert exact_lp_routes(called_second_crew.lp) == (
        (0, 20, 4), Fraction(96)
    )
    assert no_second_crew.offset == 0
    assert called_second_crew.offset == -12
    assert no_second_crew.lp.value((8, 12, 0, 0)) + no_second_crew.offset == 84
    assert called_second_crew.lp.value((0, 20, 4)) + called_second_crew.offset == 84
    assert 2 * 4 - overtime_cost(4) == 4
    assert 2 * 8 - overtime_cost(8) == 0
    sampled_gains = {
        Fraction(i, 2): 2 * Fraction(i, 2) - overtime_cost(Fraction(i, 2))
        for i in range(17)
    }
    assert max(sampled_gains.values()) == 4
    assert [u for u, gain in sampled_gains.items() if gain == 4] == [Fraction(4)]


def test_shortfall_models_have_exact_optima_and_the_q_three_certificate():
    half = shortfall(Fraction(1, 2))
    half_point, half_value = enumeration_and_dual(half)
    assert half_point == (8, 12, 2)
    assert half_value == 83

    three = shortfall(3)
    three_point, three_value = enumeration_and_dual(three)
    assert three_point == (4, 14, 0)
    assert three_value == 82

    multipliers = (Fraction(3), Fraction(0), Fraction(1))
    covered = tuple(
        sum((multipliers[i] * three.A[i][j] for i in range(three.m)),
            Fraction(0))
        for j in range(three.n)
    )
    assert covered == (3, 5, -1)
    assert all(covered[j] >= three.c[j] for j in range(three.n))
    assert sum((multipliers[i] * three.b[i] for i in range(three.m)),
               Fraction(0)) == 82
    assert three.value(three_point) == 82

    tied = shortfall(1)
    tied_value = best_by_enumeration(tied)[1]
    assert dual_by_enumeration(tied)[1] == tied_value == 82
    for step in range(6):
        s = Fraction(step, 5)
        point = (8 - 4 * s, 12 + 2 * s, 2 - 2 * s)
        assert tied.feasible(point)
        assert tied.value(point) == tied_value


def test_ratio_row_and_multiplier_certificate():
    lp = ratio()
    point, value = exact_lp_routes(lp)
    assert point == (12, 8)
    assert value == 76
    assert dual_by_enumeration(lp)[1] == value
    assert lp.feasible((0, 0))

    multipliers = (Fraction(0), Fraction(19, 5), Fraction(2, 5))
    covered = tuple(
        sum((multipliers[i] * lp.A[i][j] for i in range(lp.m)), Fraction(0))
        for j in range(lp.n)
    )
    assert covered == lp.c == (3, 5)
    assert sum((multipliers[i] * lp.b[i] for i in range(lp.m)),
               Fraction(0)) == 76


def test_two_week_inventory_plan_and_balance_multiplier_bill():
    lp = two_week_inventory()
    point, value = exact_lp_routes(lp)
    assert point == (8, 12, 8, 4, 0, 10, 14)
    assert value == 130
    assert dual_by_enumeration(lp)[1] == 130
    t1, f1, sold1, stored, t2, f2, sold2 = point
    assert (t1, f1, sold1, stored) == (8, 12, 8, 4)
    assert (t2, f2, sold2) == (0, 10, 14)
    assert (lp.used(0, point), lp.used(1, point), lp.used(2, point)) == (32, 20, 8)
    assert (lp.used(3, point), lp.used(4, point), lp.used(5, point)) == (20, 10, 14)
    assert 3 * t1 + 5 * sold1 + 3 * t2 + 5 * sold2 - stored == 130

    rows = (
        (1, 2, 0, 0, 0, 0, 0),
        (1, 1, 0, 0, 0, 0, 0),
        (0, 0, 0, 0, 1, 2, 0),
        (0, 0, 0, 0, 1, 1, 0),
        (0, -1, 1, 1, 0, 0, 0),
        (0, 0, 0, -1, 0, -1, 1),
        (0, 0, 1, 0, 0, 0, 0),
        (0, 0, 0, 0, 0, 0, 1),
    )
    bounds = (32, 20, 32, 10, 0, 0, 8, 16)
    multipliers = (1, 2, 0, 5, 4, 5, 1, 0)
    covered = tuple(
        sum((multipliers[i] * rows[i][j] for i in range(len(rows))),
            Fraction(0))
        for j in range(lp.n)
    )
    assert covered == (3, 0, 5, -1, 5, 0, 5)
    assert all(covered[j] >= lp.c[j] for j in range(lp.n))
    bill = sum((multipliers[i] * bounds[i] for i in range(len(rows))),
               Fraction(0))
    assert bill == value == 130


def test_scenario_models_use_one_plan_for_both_orders():
    half = scenarios(Fraction(1, 2))
    half_point, half_value = enumeration_and_dual(half)
    assert half_point[:2] == (0, 16)
    assert half_value == 80

    quarter = scenarios(Fraction(1, 4))
    quarter_point, quarter_value = enumeration_and_dual(quarter)
    assert quarter_point[:2] == (8, 12)
    assert quarter_value == 81


def test_smallest_disc_certificate_and_free_center_grid_search():
    radius = Sqrt5(Fraction(24), Fraction(-8))
    denominator = Sqrt5(Fraction(3), Fraction(1))
    assert radius * denominator == Sqrt5(Fraction(32), Fraction(0))

    alpha = Sqrt5(Fraction(3, 4), Fraction(-1, 4))
    beta = Sqrt5(Fraction(3, 2), Fraction(-1, 2))
    gamma = Sqrt5(Fraction(-5, 4), Fraction(3, 4))
    assert alpha * denominator == Sqrt5(1, 0)
    assert beta * denominator == Sqrt5(2, 0)
    assert gamma * denominator == SQRT5
    assert beta == 2 * alpha
    assert gamma == alpha * SQRT5
    assert alpha + beta + gamma == Sqrt5(1, 0)
    assert 32 * alpha == radius
    assert Fraction(3) ** 2 > Fraction(5)
    assert 9 * 5 > 25

    lathe_value = (3 + math.sqrt(5)) * float(radius.rational + radius.radical * math.sqrt(5))
    press_distance = abs(
        2 * float(radius.rational + radius.radical * math.sqrt(5)) - 20
    ) / math.sqrt(2)
    assert f"{lathe_value:.2f}" == "32.00"
    assert f"{press_distance:.2f}" == "5.50"
    assert f"{float(radius.rational + radius.radical * math.sqrt(5)):.2f}" == "6.11"

    root_two, root_five = math.sqrt(2), math.sqrt(5)
    grid_best = math.inf
    for ti in range(-40, 441):
        t = ti / 20
        for fi in range(-40, 441):
            f_value = fi / 20
            candidate = max(
                abs(t), abs(f_value),
                abs(t + 2 * f_value - 32) / root_five,
                abs(t + f_value - 20) / root_two,
            )
            grid_best = min(grid_best, candidate)
    exact_radius = float(radius.rational + radius.radical * root_five)
    assert grid_best >= exact_radius - 1e-9
    assert grid_best - exact_radius < 0.04


def test_semicontinuous_integer_and_relaxed_models():
    branches = semicontinuous()
    for branch in branches:
        point, value = exact_lp_routes(branch.lp)
        expected = Fraction(60) if branch.value == 0 else Fraction(82)
        assert value + branch.offset == expected
    best_branch, best_plan, best_value = solve_binary(branches)
    assert best_branch.value == 1
    assert best_plan == (4, 14)
    assert best_value == 82
    assert branches[0].lp.value((20, 0)) == 60
    assert branches[1].lp.value((4, 0)) == 12
    assert branches[1].restore((4, 0)) == (4, 14)

    relaxation = semicontinuous_relaxation()
    enumerated_point, enumerated_value = best_by_enumeration(relaxation)
    walked = simplex(relaxation)
    assert enumerated_value == walked.value == 84
    assert enumerated_point[:2] == walked.x[:2] == (8, 12)
    assert Fraction(3, 4) <= enumerated_point[2] <= Fraction(6, 7)
    assert Fraction(3, 4) <= walked.x[2] <= Fraction(6, 7)
    for z in (Fraction(3, 4), Fraction(4, 5), Fraction(6, 7)):
        assert relaxation.feasible((8, 12, z))
        assert relaxation.value((8, 12, z)) == 84


def test_setup_branches_relaxations_and_every_animation_sample():
    on_off = setup(30, 16)
    for branch in on_off:
        point, value = exact_lp_routes(branch.lp)
        assert value + branch.offset == (
            60 if branch.value == 0 else 54
        )
    best_branch, best_plan, best_value = solve_binary(on_off)
    assert best_branch.value == 0
    assert best_plan == (20, 0)
    assert best_value == 60

    expected = {
        Fraction(16): (Fraction(123, 2), Fraction(3, 4)),
        Fraction(100): (Fraction(402, 5), Fraction(3, 25)),
    }
    for U, (expected_value, expected_z) in expected.items():
        relaxation = setup_relaxation(30, U)
        point, value = exact_lp_routes(relaxation)
        assert point == (8, 12, expected_z)
        assert value == expected_value

    for step in range(SETUP_MOVE_STEPS + 1):
        U = setup_bound_at(step)
        point, _ = best_by_enumeration(setup_relaxation(30, U))
        assert point[:2] == (8, 12)
        assert point[2] == Fraction(12, 1) / U


def test_either_or_bounds_are_minimal_and_both_arms_are_solved():
    max_t, max_t_value = exact_lp_routes(LP.build(
        c=(1, 0), A=f.MILL.A, b=f.MILL.b
    ))
    max_f, max_f_value = exact_lp_routes(LP.build(
        c=(0, 1), A=f.MILL.A, b=f.MILL.b
    ))
    assert max_t == (20, 0) and max_t_value == 20
    assert max_f == (0, 16) and max_f_value == 16
    M1, M2 = max_t_value - 6, max_f_value - 6
    assert (M1, M2) == (14, 10)

    branches = either_or(M1, M2)
    branch_results = []
    for branch in branches:
        point, value = exact_lp_routes(branch.lp)
        branch_results.append((branch.value, point, value))
    assert branch_results == [(0, (6, 13), 83), (1, (14, 6), 72)]
    best_branch, best_point, best_value = solve_binary(branches)
    assert (best_branch.value, best_point, best_value) == (0, (6, 13), 83)

    wrong_branch = either_or(M1, 6)[0]
    wrong_point, wrong_value = exact_lp_routes(wrong_branch.lp)
    assert wrong_point == (6, 12)
    assert wrong_value == 78


def test_chapter_four_and_five_prose_numbers_and_figure_paths():
    for phrase in (
        "h(u) = max(u, 3u − 8)",
        "makes (4, 16): 92,000 roubles of plywood",
        "88,000 in all",
        "4,000 more than without overtime",
        "at q = ½",
        "keeping 83,000",
        "at q = 3",
        "keeps 82,000",
        "(19/5)(t + f) + (2/5)(3f − 2t)",
        "worth 76,000 roubles",
        "the rule costs 8,000",
        "| week 1 | 8 | 12 | 8 | 4 |",
        "| week 2 | 0 | 10 | 14 | |",
        "130 thousand roubles",
        "84 − 3 × ¼ × 4 = 81",
        "80,000 roubles",
        "24 − 8√5 ≈ 6.11",
        "5.50 from the centre",
        "14z ≤ f ≤ 16z",
        "the relaxation is at least the best value",
        "61.5",
        "80.4",
        "22.5 of the 30",
        "3.6",
        "M1 must be at least 20 − 6 = 14 and M2 at least 16 − 6 = 10",
        "(6, 13) worth 83",
        "(14, 6) worth 72",
        "(6, 12), worth 78",
    ):
        assert phrase in FLAT

    images = (
        "chapters/04-more-rows/tiers.png",
        "chapters/04-more-rows/shortfall.gif",
        "chapters/04-more-rows/ratio.png",
        "chapters/04-more-rows/two_discs.png",
        "chapters/05-yes-or-no/union.png",
        "chapters/05-yes-or-no/setup.gif",
        "chapters/05-yes-or-no/either_or.png",
    )
    for relative in images:
        assert relative in TEXT
        assert (ROOT / relative).is_file()


def test_chapter_headings_and_registered_folders_match_the_renumbering():
    from build import CHAPTERS

    expected = (
        (4, "04-more-rows", "More rows from words"),
        (5, "05-yes-or-no", "Yes-or-no decisions"),
        (6, "06-buying-the-hours", "Someone buying the hours"),
        (7, "07-one-more", "What one more is worth"),
        (8, "08-separation", "A wall between a point and a shape"),
        (9, "09-shadows", "Shadows: eliminating a variable"),
        (10, "10-plan-or-proof", "Either a plan or a proof"),
        (11, "11-corners-by-algebra", "Corners by algebra"),
        (12, "12-degeneracy", "Too many walls at one corner"),
        (13, "13-corners-and-escape", "Corners and escape routes"),
    )
    assert tuple((chapter.number, chapter.folder, chapter.title)
                 for chapter in CHAPTERS[4:]) == expected
    assert "## 4 · More rows from words" in TEXT
    assert "## 5 · Yes-or-no decisions" in TEXT
    assert "## 6 · Someone buying the hours" in TEXT
    assert "## 7 · What one more is worth" in TEXT
    assert "## 8 · A wall between a point and a shape" in TEXT
    assert "## 9 · Shadows: eliminating a variable" in TEXT
    assert "## 10 · Either a plan or a proof" in TEXT
    assert "## 11 · Corners by algebra" in TEXT
    assert "## 12 · Too many walls at one corner" in TEXT
    assert "## 13 · Corners and escape routes" in TEXT
