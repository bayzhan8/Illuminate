import random
from fractions import Fraction as Q
from pathlib import Path

from figures import fig17a_ranges as ranges
from linprog.sensitivity import (
    basis_inverse, cost_range, new_column, rhs_range,
)
from linprog.simplex import dictionary, two_phase

ROOT = Path(__file__).resolve().parents[1]
MILL_A = (
    (Q(1), Q(2), Q(1), Q(0)),
    (Q(1), Q(1), Q(0), Q(1)),
)
MILL_B = (Q(32), Q(20))
MILL_C = (Q(3), Q(5), Q(0), Q(0))
MILL_BASIS = (0, 1)
DECISION_BASIS = ((Q(1), Q(2)), (Q(1), Q(1)))


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Q(0))


def matvec(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def point_from_dictionary(state, basis, variable_count):
    point = [Q(0)] * variable_count
    for index, value in zip(basis, state.x_B):
        point[index] = value
    return tuple(point)


def solve(matrix, rhs, objective):
    return two_phase(
        matrix, rhs, objective, rule="bland", max_pivots=100
    )


def random_mill(rng):
    plan = (Q(rng.randint(2, 12)), Q(rng.randint(2, 12)))
    rhs = matvec(DECISION_BASIS, plan)
    prices = (Q(rng.randint(1, 6)), Q(rng.randint(1, 6)))
    objective = (
        prices[0] + prices[1],
        2 * prices[0] + prices[1],
        Q(0),
        Q(0),
    )
    result = solve(MILL_A, rhs, objective)
    assert result.status == "optimal"
    assert result.x[:2] == plan
    assert set(result.basis) == {0, 1}
    return rhs, objective, result


def assert_fixed_basis_optimal(matrix, rhs, objective, basis):
    state = dictionary(matrix, rhs, objective, basis)
    assert all(value >= 0 for value in state.x_B)
    assert all(value <= 0 for value in state.reduced_costs)
    point = point_from_dictionary(state, basis, len(objective))
    return dot(objective, point)


def assert_solved_value(matrix, rhs, objective, value):
    result = solve(matrix, rhs, objective)
    assert result.status == "optimal"
    assert result.value == value


def assert_outside_changes_basis_or_is_infeasible(
        matrix, rhs, objective, basis):
    result = solve(matrix, rhs, objective)
    assert result.status in {"optimal", "infeasible"}
    if result.status == "optimal":
        assert result.basis != basis


def test_mill_inverse_ranges_and_value_changes_are_exact():
    inverse = basis_inverse(MILL_A, MILL_B, MILL_C, MILL_BASIS)
    assert inverse == ((Q(-1), Q(2)), (Q(1), Q(-1)))
    assert matvec(inverse, MILL_B) == (Q(8), Q(12))

    state = dictionary(MILL_A, MILL_B, MILL_C, MILL_BASIS)
    slack_columns = (2, 3)
    displayed_slack_coefficients = tuple(
        tuple(-state.rows[row][column] for column in slack_columns)
        for row in range(2)
    )
    assert tuple(
        tuple(-coefficient for coefficient in row)
        for row in displayed_slack_coefficients
    ) == inverse

    assert rhs_range(MILL_A, MILL_B, MILL_C, MILL_BASIS, 0) \
        == (Q(20), Q(40))
    assert rhs_range(MILL_A, MILL_B, MILL_C, MILL_BASIS, 1) \
        == (Q(16), Q(32))
    assert cost_range(MILL_A, MILL_B, MILL_C, MILL_BASIS, 0) \
        == (Q(5, 2), Q(5))
    assert cost_range(MILL_A, MILL_B, MILL_C, MILL_BASIS, 1) \
        == (Q(3), Q(6))
    assert cost_range(MILL_A, MILL_B, MILL_C, MILL_BASIS, 2) \
        == (None, Q(2))
    assert cost_range(MILL_A, MILL_B, MILL_C, MILL_BASIS, 3) \
        == (None, Q(1))

    for delta in (Q(-12), Q(-4), Q(0), Q(8)):
        rhs = (MILL_B[0] + delta, MILL_B[1])
        plan = matvec(inverse, rhs)
        assert plan == (Q(8) - delta, Q(12) + delta)
        assert dot(MILL_C[:2], plan) == Q(84) + 2 * delta
    for delta in (Q(-4), Q(0), Q(7), Q(12)):
        rhs = (MILL_B[0], MILL_B[1] + delta)
        plan = matvec(inverse, rhs)
        assert plan == (Q(8) + 2 * delta, Q(12) - delta)
        assert dot(MILL_C[:2], plan) == Q(84) + delta
    assert matvec(inverse, (Q(33), Q(22))) == (Q(11), Q(11))
    assert dot(MILL_C[:2], matvec(inverse, (Q(33), Q(22)))) == 88


def test_stock_and_value_range_endpoints_are_ties():
    three_ply = (Q(1), Q(1))
    five_ply = (Q(2), Q(1))
    assert (Q(40), Q(20)) == tuple(20 * value for value in five_ply)
    assert (Q(20), Q(20)) == tuple(20 * value for value in three_ply)
    lathe_row = (Q(1), Q(2))
    press_row = (Q(1), Q(1))
    assert tuple(Q(5, 2) * value for value in lathe_row) \
        == (Q(5, 2), Q(5))
    assert tuple(Q(5) * value for value in press_row) == (Q(5), Q(5))
    assert cost_range(MILL_A, MILL_B, MILL_C, MILL_BASIS, 0) \
        == (Q(5, 2), Q(5))
    assert cost_range(MILL_A, MILL_B, MILL_C, MILL_BASIS, 1) \
        == (Q(3), Q(6))


def test_random_rhs_and_cost_ranges_match_resolved_lp_boundaries():
    rng = random.Random(1701)
    epsilon = Q(1, 100)
    for _ in range(8):
        rhs, objective, optimum = random_mill(rng)
        basis = optimum.basis
        for index in range(len(rhs)):
            low, high = rhs_range(MILL_A, rhs, objective, basis, index)
            assert low is None or low <= rhs[index]
            assert high is None or rhs[index] <= high
            if low is not None:
                gap = rhs[index] - low
                assert gap > 0
                inside = low + min(epsilon, gap / 2)
                changed_rhs = list(rhs)
                changed_rhs[index] = inside
                value = assert_fixed_basis_optimal(
                    MILL_A, changed_rhs, objective, basis
                )
                assert_solved_value(
                    MILL_A, changed_rhs, objective, value
                )
                changed_rhs[index] = low - epsilon
                assert_outside_changes_basis_or_is_infeasible(
                    MILL_A, changed_rhs, objective, basis
                )
            if high is not None:
                gap = high - rhs[index]
                assert gap > 0
                inside = high - min(epsilon, gap / 2)
                changed_rhs = list(rhs)
                changed_rhs[index] = inside
                value = assert_fixed_basis_optimal(
                    MILL_A, changed_rhs, objective, basis
                )
                assert_solved_value(
                    MILL_A, changed_rhs, objective, value
                )
                changed_rhs[index] = high + epsilon
                assert_outside_changes_basis_or_is_infeasible(
                    MILL_A, changed_rhs, objective, basis
                )

        for index in range(len(objective)):
            low, high = cost_range(MILL_A, rhs, objective, basis, index)
            assert low is None or low <= objective[index]
            assert high is None or objective[index] <= high
            if low is not None:
                gap = objective[index] - low
                assert gap > 0
                inside = low + min(epsilon, gap / 2)
                changed_objective = list(objective)
                changed_objective[index] = inside
                value = assert_fixed_basis_optimal(
                    MILL_A, rhs, changed_objective, basis
                )
                assert_solved_value(
                    MILL_A, rhs, changed_objective, value
                )
                changed_objective[index] = low - epsilon
                assert_outside_changes_basis_or_is_infeasible(
                    MILL_A, rhs, changed_objective, basis
                )
            if high is not None:
                gap = high - objective[index]
                assert gap > 0
                inside = high - min(epsilon, gap / 2)
                changed_objective = list(objective)
                changed_objective[index] = inside
                value = assert_fixed_basis_optimal(
                    MILL_A, rhs, changed_objective, basis
                )
                assert_solved_value(
                    MILL_A, rhs, changed_objective, value
                )
                changed_objective[index] = high + epsilon
                assert_outside_changes_basis_or_is_infeasible(
                    MILL_A, rhs, changed_objective, basis
                )


def test_new_column_matches_reoptimization_and_birch_example():
    rng = random.Random(1702)
    offsets = (Q(-2), Q(-1), Q(0), Q(1), Q(2))
    for iteration in range(15):
        rhs, objective, optimum = random_mill(rng)
        state = dictionary(MILL_A, rhs, objective, optimum.basis)
        column = (Q(rng.randint(1, 4)), Q(rng.randint(1, 4)))
        value = dot(state.y, column) + offsets[iteration % len(offsets)]
        reduced_cost, transformed = new_column(
            MILL_A, rhs, objective, optimum.basis, column, value
        )
        inverse = basis_inverse(
            MILL_A, rhs, objective, optimum.basis
        )
        assert transformed == matvec(inverse, column)
        assert reduced_cost == value - dot(state.y, column)

        extended_A = tuple(
            row + (column[row_index],)
            for row_index, row in enumerate(MILL_A)
        )
        extended_c = objective + (value,)
        reoptimized = solve(extended_A, rhs, extended_c)
        assert reoptimized.status == "optimal"
        assert (reoptimized.value > optimum.value) == (reduced_cost > 0)

    reduced_cost, transformed = new_column(
        MILL_A, MILL_B, MILL_C, MILL_BASIS, (Q(2), Q(2)), Q(7)
    )
    assert reduced_cost == 1
    assert transformed == (Q(2), Q(0))
    positive_ratios = tuple(
        MILL_BASIS[row]
        for row, value in enumerate(transformed) if value > 0
    )
    assert positive_ratios == (0,)
    assert dictionary(
        MILL_A, MILL_B, MILL_C, MILL_BASIS
    ).x_B[0] / transformed[0] == 4
    assert new_column(
        MILL_A, MILL_B, MILL_C, MILL_BASIS, (Q(2), Q(2)), Q(6)
    )[0] == 0

    expanded_A = tuple(
        row + ((Q(2), Q(2))[index],)
        for index, row in enumerate(MILL_A)
    )
    expanded_c = MILL_C + (Q(7),)
    birch = solve(expanded_A, MILL_B, expanded_c)
    assert birch.status == "optimal"
    assert birch.x == (Q(0), Q(12), Q(0), Q(0), Q(4))
    assert birch.value == 88
    prices = dictionary(
        expanded_A, MILL_B, expanded_c, birch.basis
    ).y
    assert prices == (Q(3, 2), Q(2))
    assert matvec(expanded_A, birch.x) == MILL_B
    assert prices[0] * expanded_A[0][0] \
        + prices[1] * expanded_A[1][0] == Q(7, 2) >= MILL_C[0]
    assert dot(prices, MILL_B) == birch.value == 88


def test_sensitivity_figure_anchors_prose_and_generated_asset():
    assert ranges.INVERSE == ((Q(-1), Q(2)), (Q(1), Q(-1)))
    assert ranges.LATHE_RANGE == (Q(20), Q(40))
    assert ranges.PRESS_RANGE == (Q(16), Q(32))
    assert ranges.THREE_PLY_RANGE == (Q(5, 2), Q(5))
    assert ranges.FIVE_PLY_RANGE == (Q(3), Q(6))
    assert ranges.STOCK_START == (Q(20), Q(20))
    assert ranges.STOCK_FINAL == (Q(40), Q(20))
    assert ranges.PRICE_START == (Q(5, 2), Q(5))
    assert ranges.PRICE_FINAL == (Q(5), Q(5))
    assert ranges.plan_at_stock((Q(32), Q(20))) == (Q(8), Q(12))
    assert ranges.plan_at_stock(ranges.STOCK_START) == (Q(20), Q(0))
    assert ranges.plan_at_stock(ranges.STOCK_FINAL) == (Q(0), Q(20))
    assert ranges.value_at_stock(ranges.STOCK_START) == 60
    assert ranges.value_at_stock(ranges.STOCK_FINAL) == 100
    assert ranges.prices_at(ranges.PRICE_START) == (Q(5, 2), Q(0))
    assert ranges.prices_at(ranges.PRICE_FINAL) == (Q(0), Q(5))
    assert ranges.STOCK_TIE_ANCHORS == (
        ranges.STOCK_START, ranges.STOCK_FINAL
    )
    assert ranges.STOCK_POINT_ANCHOR == ranges.STOCK_START
    assert ranges.PRICE_TIE_ANCHORS == (
        ranges.PRICE_START, ranges.PRICE_FINAL
    )
    assert ranges.STOCK_RAYS == ((Q(1), Q(1)), (Q(2), Q(1)))
    assert ranges.VALUE_RAYS == ((Q(1), Q(2)), (Q(1), Q(1)))
    assert ranges.STOCK_BASE_ANCHOR == (Q(32), Q(20))
    assert ranges.PRICE_BASE_ANCHOR == (Q(3), Q(5))
    assert ranges.stock_formula_text() == (
        "δ = b₁ − 32: plan = (8 − δ, 12 + δ), value = 84 + 2δ"
    )
    assert ranges.price_formula_text() == (
        "δ = c₁ − 3: y = (2 − δ, 1 + 2δ)"
    )
    assert ranges.TITLE
    assert tuple(ranges.frame_state(index)[0]
                 for index in ranges.HOLD_INDICES) == (0, 2)
    assert all(ranges.subtitle_for_frame(index).strip()
               for index in range(ranges.TOTAL_FRAMES))
    assert (ROOT / "chapters/17-sensitivity/ranges.gif").is_file()

    prose = (ROOT / "lesson.md").read_text()
    flat = " ".join(prose.split())
    for phrase in (
        "B⁻¹ = [ −1 2 ] (row t)",
        "B⁻¹(32, 20) = (−32 + 40, 32 − 20) = (8, 12)",
        "20 ≤ lathe ≤ 40",
        "16 ≤ press ≤ 32",
        "84 + 2δ₁ + δ₂",
        "(40, 20) = 20·(2, 1)",
        "(20, 20) = 20·(1, 1)",
        "2.5 ≤ value of 3-ply ≤ 5",
        "3 ≤ value of 5-ply ≤ 6",
        "(2.5, 5) is parallel to the lathe row",
        "(5, 5) is parallel to the press row",
        "c̄ = 7 − (2·2 + 1·2) = 7 − 6 = 1 > 0.",
        "B⁻¹(2, 2) = (−2 + 4, 2 − 2) = (2, 0)",
        "8 ÷ 2 = 4",
        "(t, f, birch) = (0, 12, 4)",
        "24 + 8 = 32 lathe hours and 12 + 8 = 20 press hours",
        "y = (3/2, 2)",
        "3/2 + 2 = 7/2 ≥ 3",
        "32·3/2 + 20·2 = 88",
        "worth adding exactly when its value is above 6",
        "chapters/17-sensitivity/ranges.gif",
    ):
        assert phrase in flat
