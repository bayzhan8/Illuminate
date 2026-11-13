import random
from fractions import Fraction as Q
from pathlib import Path

import pytest

from linprog.alternatives import cone_farkas
from linprog.corners import rank
from linprog.simplex import two_phase
from linprog.strict import strict_pair
from figures import fig20a_strict as figure

TOPIC = Path(__file__).resolve().parents[1]
GLUE_A = (
    (Q(1), Q(2)),
    (Q(1), Q(1)),
    (Q(2), Q(3)),
)
GLUE_B = (Q(32), Q(20), Q(52))
GLUE_C = (Q(3), Q(5))


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Q(0))


def primal_system(A, b, c):
    row_count = len(A)
    variable_count = len(c)
    matrix = tuple(
        tuple(row)
        + tuple(Q(int(column == row_index))
                for column in range(row_count))
        for row_index, row in enumerate(A)
    )
    return matrix, tuple(b), tuple(c) + (Q(0),) * row_count


def dual_system(A, c):
    row_count = len(A)
    variable_count = len(c)
    matrix = tuple(
        tuple(A[row][column] for row in range(row_count))
        + tuple(-Q(int(index == column))
                for index in range(variable_count))
        for column in range(variable_count)
    )
    return matrix, tuple(c), (Q(0),) * (row_count + variable_count)


def solve_primal(A, b, c):
    matrix, rhs, objective = primal_system(A, b, c)
    return two_phase(matrix, rhs, objective, rule="bland")


def solve_dual(A, b, c):
    matrix, rhs, _ = dual_system(A, c)
    objective = tuple(-value for value in b) + (Q(0),) * len(c)
    return two_phase(matrix, rhs, objective, rule="bland")


def random_rational(rng, low, high):
    return Q(rng.randint(low, high), rng.randint(1, 4))


def random_bounded_lp(rng, redundant=False, degenerate=False):
    variable_count = rng.randint(1, 3)
    resource_count = rng.randint(1, 2)
    witness = tuple(
        Q(rng.randint(0, 4), rng.randint(1, 3))
        for _ in range(variable_count)
    )
    resources = tuple(
        tuple(random_rational(rng, -3, 4)
              for _ in range(variable_count))
        for _ in range(resource_count)
    )
    slacks = tuple(
        Q(0) if degenerate and rng.randrange(3) == 0
        else random_rational(rng, 1, 5)
        for _ in range(resource_count)
    )
    bounds = tuple(
        dot(row, witness) + slack
        for row, slack in zip(resources, slacks)
    )
    bounds_rows = tuple(
        tuple(Q(int(column == index))
              for column in range(variable_count))
        for index in range(variable_count)
    )
    upper_bounds = tuple(
        witness[index] + Q(rng.randint(1, 5), rng.randint(1, 3))
        for index in range(variable_count)
    )
    matrix = resources + bounds_rows
    rhs = bounds + upper_bounds
    if redundant:
        matrix += (tuple(2 * value for value in resources[0]),)
        rhs += (2 * bounds[0],)
    costs = tuple(
        random_rational(rng, -4, 7)
        for _ in range(variable_count)
    )
    return matrix, rhs, costs


def random_local_cone_lp(rng):
    variable_count = rng.randint(1, 3)
    resource_count = rng.randint(1, 3)
    witness = tuple(
        Q(rng.randint(1, 5), rng.randint(1, 3))
        for _ in range(variable_count)
    )
    resources = tuple(
        tuple(Q(rng.randint(0, 4), rng.randint(1, 3))
              for _ in range(variable_count))
        for _ in range(resource_count)
    )
    resource_bounds = tuple(
        dot(row, witness) + Q(rng.randint(1, 5), rng.randint(1, 3))
        for row in resources
    )
    upper_rows = tuple(
        tuple(Q(int(column == index))
              for column in range(variable_count))
        for index in range(variable_count)
    )
    lower_rows = tuple(
        tuple(-Q(int(column == index))
              for column in range(variable_count))
        for index in range(variable_count)
    )
    upper_bounds = tuple(
        witness[index] + Q(rng.randint(1, 5), rng.randint(1, 3))
        for index in range(variable_count)
    )
    if rng.randrange(4) == 0:
        resources += (resources[0],)
        resource_bounds += (resource_bounds[0],)
    matrix = resources + upper_rows + lower_rows
    rhs = resource_bounds + upper_bounds + (Q(0),) * variable_count
    costs = (
        Q(rng.randint(1, 5), rng.randint(1, 3)),
    ) + tuple(
        Q(rng.randint(-5, 5), rng.randint(1, 3))
        for _ in range(variable_count - 1)
    )
    return matrix, rhs, costs


def tight_row_prices(matrix, tight_rows, costs):
    equality = tuple(
        tuple(matrix[row][column] for row in tight_rows)
        for column in range(len(costs))
    )
    status, prices = cone_farkas(equality, costs)
    assert status == "solution"
    return prices


def assert_primal(A, b, c, value, x):
    assert all(value >= 0 for value in x)
    assert all(dot(row, x) <= bound for row, bound in zip(A, b))
    assert dot(c, x) == value


def assert_dual(A, b, c, value, y):
    assert all(value >= 0 for value in y)
    for column, cost in enumerate(c):
        assert sum(
            (y[row] * A[row][column] for row in range(len(A))),
            Q(0),
        ) >= cost
    assert dot(b, y) == value


def test_glue_lp_returns_an_interior_strict_pair_and_basic_endpoints():
    result = strict_pair(GLUE_A, GLUE_B, GLUE_C)
    assert result.x == (Q(8), Q(12))
    assert 0 < result.y[2] < 1
    assert result.y == (
        Q(2) - result.y[2],
        Q(1) - result.y[2],
        result.y[2],
    )
    assert_primal(GLUE_A, GLUE_B, GLUE_C, Q(84), result.x)
    assert_dual(GLUE_A, GLUE_B, GLUE_C, Q(84), result.y)

    table = (
        (Q(0), (Q(2), Q(1), Q(0)), False),
        (Q(1, 2), (Q(3, 2), Q(1, 2), Q(1, 2)), True),
        (Q(1), (Q(1), Q(0), Q(1)), False),
    )
    for parameter, prices, is_strict in table:
        assert prices == (
            Q(2) - parameter,
            Q(1) - parameter,
            parameter,
        )
        assert dot(GLUE_B, prices) == Q(84)
        assert all(
            sum((prices[row] * GLUE_A[row][column]
                 for row in range(3)), Q(0)) >= GLUE_C[column]
            for column in range(2)
        )
        assert all(
            (GLUE_B[row] - sum(
                (GLUE_A[row][column] * result.x[column]
                 for column in range(2)), Q(0),
            ) > 0) != (prices[row] > 0)
            for row in range(3)
        ) is is_strict

    columns = tuple(
        tuple(GLUE_A[row][column] for row in range(3))
        for column in range(2)
    )
    endpoint_rows = (
        columns + ((Q(0), Q(0), Q(1)),),
        columns + ((Q(0), Q(1), Q(0)),),
    )
    assert all(rank(active) == 3 for active in endpoint_rows)
    assert result.plan_witnesses[0] is None
    assert result.plan_witnesses[1] is None
    assert result.plan_witnesses[2] is None
    assert result.price_witnesses[0] is not None
    assert result.price_witnesses[1] is not None
    assert result.price_witnesses[2] is not None


def test_both_infeasible_example_has_primal_and_dual_farkas_certificates():
    matrix = ((Q(1), Q(-1)), (Q(-1), Q(1)))
    rhs = (Q(1), Q(-2))
    costs = (Q(2), Q(-1))

    primal = solve_primal(matrix, rhs, costs)
    assert primal.status == "infeasible"
    primal_certificate = primal.certificate
    assert all(value >= 0 for value in primal_certificate)
    assert dot(primal_certificate, rhs) < 0
    for column in range(len(costs)):
        assert sum(
            (primal_certificate[row] * matrix[row][column]
             for row in range(len(matrix))),
            Q(0),
        ) >= 0

    dual_matrix, dual_rhs, dual_objective = dual_system(matrix, costs)
    dual = two_phase(
        dual_matrix, dual_rhs, dual_objective, rule="bland"
    )
    assert dual.status == "infeasible"
    primal_ray = tuple(-value for value in dual.certificate)
    assert all(value >= 0 for value in primal_ray)
    for row in range(len(matrix)):
        assert dot(matrix[row], primal_ray) <= 0
    assert dot(costs, primal_ray) > 0


def test_mill_optimum_is_the_tight_row_price_combination():
    matrix = (
        (Q(1), Q(2)),
        (Q(1), Q(1)),
        (Q(-1), Q(0)),
        (Q(0), Q(-1)),
    )
    rhs = (Q(32), Q(20), Q(0), Q(0))
    point = (Q(8), Q(12))
    costs = (Q(3), Q(5))
    tight = tuple(
        index for index, (row, bound) in enumerate(zip(matrix, rhs))
        if dot(row, point) == bound
    )
    assert tight == (0, 1)
    prices = tight_row_prices(matrix, tight, costs)
    assert prices == (Q(2), Q(1))
    assert tuple(
        sum((prices[index] * matrix[row][column]
             for index, row in enumerate(tight)), Q(0))
        for column in range(2)
    ) == costs
    assert dot(tuple(rhs[row] for row in tight), prices) \
        == dot(costs, point) == 84


def test_random_local_cone_proofs_and_improving_directions():
    rng = random.Random(2026)
    for _ in range(200):
        matrix, rhs, costs = random_local_cone_lp(rng)
        variable_count = len(costs)
        assert matrix[-variable_count:] == tuple(
            tuple(-Q(int(column == index))
                  for column in range(variable_count))
            for index in range(variable_count)
        )
        equality, bounds, objective = primal_system(matrix, rhs, costs)
        optimum = two_phase(
            equality, bounds, objective, rule="bland"
        )
        assert optimum.status == "optimal"
        point = optimum.x[:variable_count]
        value = dot(costs, point)
        assert_primal(matrix, rhs, costs, value, point)

        tight = tuple(
            index for index, (row, bound) in enumerate(zip(matrix, rhs))
            if dot(row, point) == bound
        )
        assert tight
        prices = tight_row_prices(matrix, tight, costs)
        assert all(price >= 0 for price in prices)
        assert tuple(
            sum((prices[index] * matrix[row][column]
                 for index, row in enumerate(tight)), Q(0))
            for column in range(variable_count)
        ) == costs
        assert dot(tuple(rhs[row] for row in tight), prices) == value

        nonoptimal = (Q(0),) * variable_count
        assert all(
            dot(row, nonoptimal) <= bound
            for row, bound in zip(matrix, rhs)
        )
        assert dot(costs, nonoptimal) < value
        tight_at_nonoptimal = tuple(
            index for index, (row, bound) in enumerate(zip(matrix, rhs))
            if dot(row, nonoptimal) == bound
        )
        direction = tuple(
            point[column] - nonoptimal[column]
            for column in range(variable_count)
        )
        assert all(
            dot(matrix[row], direction) <= 0
            for row in tight_at_nonoptimal
        )
        assert dot(costs, direction) > 0


def test_four_outcome_table_has_one_exact_example_in_each_cell():
    mill_A = ((Q(1), Q(2)), (Q(1), Q(1)))
    mill_b = (Q(32), Q(20))
    mill_c = (Q(3), Q(5))
    mill_primal = solve_primal(mill_A, mill_b, mill_c)
    mill_dual = solve_dual(mill_A, mill_b, mill_c)
    assert mill_primal.status == mill_dual.status == "optimal"
    assert mill_primal.value == -mill_dual.value == 84

    primal_unbounded_A = ((Q(0),),)
    primal_unbounded_b = (Q(0),)
    primal_unbounded_c = (Q(1),)
    assert solve_primal(
        primal_unbounded_A, primal_unbounded_b, primal_unbounded_c
    ).status == "unbounded"
    assert solve_dual(
        primal_unbounded_A, primal_unbounded_b, primal_unbounded_c
    ).status == "infeasible"

    dual_unbounded_A = ((Q(0),),)
    dual_unbounded_b = (Q(-1),)
    dual_unbounded_c = (Q(0),)
    assert solve_primal(
        dual_unbounded_A, dual_unbounded_b, dual_unbounded_c
    ).status == "infeasible"
    assert solve_dual(
        dual_unbounded_A, dual_unbounded_b, dual_unbounded_c
    ).status == "unbounded"

    both_infeasible = ((Q(1), Q(-1)), (Q(-1), Q(1)))
    both_b = (Q(1), Q(-2))
    both_c = (Q(2), Q(-1))
    assert solve_primal(both_infeasible, both_b, both_c).status \
        == "infeasible"
    assert solve_dual(both_infeasible, both_b, both_c).status \
        == "infeasible"


def test_strict_pair_requires_a_finite_primal_optimum():
    with pytest.raises(ValueError, match="finite primal optimum"):
        strict_pair(((Q(0),),), (Q(-1),), (Q(0),))
    with pytest.raises(ValueError, match="finite primal optimum"):
        strict_pair(((Q(0),),), (Q(0),), (Q(1),))


def test_random_feasible_bounded_primal_and_dual_values_agree():
    rng = random.Random(2001)
    for _ in range(200):
        matrix, rhs, costs = random_bounded_lp(rng, redundant=True)
        primal = solve_primal(matrix, rhs, costs)
        dual = solve_dual(matrix, rhs, costs)
        assert primal.status == dual.status == "optimal"
        assert primal.value == -dual.value
        point = primal.x[:len(costs)]
        prices = primal.certificate
        assert_primal(matrix, rhs, costs, primal.value, point)
        assert_dual(matrix, rhs, costs, primal.value, prices)


def test_random_strict_pairs_are_exactly_complementary_including_redundant_rows():
    rng = random.Random(2002)
    for _ in range(100):
        matrix, rhs, costs = random_bounded_lp(
            rng, redundant=True, degenerate=True
        )
        result = strict_pair(matrix, rhs, costs)
        value = dot(costs, result.x)
        assert_primal(matrix, rhs, costs, value, result.x)
        assert_dual(matrix, rhs, costs, value, result.y)

        row_slacks = tuple(
            bound - dot(row, result.x)
            for row, bound in zip(matrix, rhs)
        )
        assert all(slack >= 0 for slack in row_slacks)
        for slack, price in zip(row_slacks, result.y):
            assert (slack > 0) != (price > 0)

        losses = tuple(
            sum(
                (result.y[row] * matrix[row][column]
                 for row in range(len(matrix))),
                Q(0),
            ) - costs[column]
            for column in range(len(costs))
        )
        assert all(loss >= 0 for loss in losses)
        for amount, loss in zip(result.x, losses):
            assert (amount > 0) != (loss > 0)

        assert len(result.plan_witnesses) == len(matrix) + len(costs)
        assert len(result.price_witnesses) == len(matrix) + len(costs)
        for index, (plan, price) in enumerate(zip(
                result.plan_witnesses, result.price_witnesses)):
            assert (plan is not None) != (price is not None)
            if plan is not None:
                assert_primal(matrix, rhs, costs, value, plan)
                if index < len(matrix):
                    assert rhs[index] - dot(matrix[index], plan) > 0
                else:
                    assert plan[index - len(matrix)] > 0
            if price is not None:
                assert_dual(matrix, rhs, costs, value, price)
                if index < len(matrix):
                    assert price[index] > 0
                else:
                    column = index - len(matrix)
                    assert sum(
                        (price[row] * matrix[row][column]
                         for row in range(len(matrix))),
                        Q(0),
                    ) - costs[column] > 0


def test_chapter_20_proofs_numbers_and_figure_anchor():
    prose = (TOPIC / "lesson.md").read_text()
    asset = "chapters/20-strict/strict.gif"
    for phrase in (
        "Theorem.** If the mill's LP",
        "For any ε > 0, no plan reaches z* + ε",
        "yA − μc ≥ 0 and yb − μ(z* + ε) < 0",
        "The four outcomes",
        "two rows add to 0 ≤ −1",
        "y₁ − y₂ ≥ 2 and −y₁ + y₂ ≥ −1",
        "The plan (8, 12) leaves no lathe, press or glue idle",
        "y = (2 − s, 1 − s, s), 0 ≤ s ≤ 1",
        "(3/2, 1/2, 1/2)",
        "maximise s_i subject to Ax + s = b, cx ≥ z*, x, s ≥ 0.",
        "wA ≥ μc and wb = μz*",
        "The central path followed by interior-point methods",
        "### A third form: no better direction nearby",
        "Theorem (local ⇒ global ⇒ dual)",
        "no direction d with A_I d ≤ 0 has cd > 0",
        "c = Σ_{i∈I} y_i A_i for some y ≥ 0",
        "1 ⇒ 2.",
        "2 ⇒ 3.",
        "3 ⇒ 1.",
        "The step 2 ⇒ 1 is the surprising one.",
    ):
        assert phrase in prose
    assert asset in prose
    assert (TOPIC / asset).is_file()
    assert figure.RESULT.x == (Q(8), Q(12))
    assert figure.START_PRICES == (Q(2), Q(1), Q(0))
    assert figure.MIDDLE_PRICES == (Q(3, 2), Q(1, 2), Q(1, 2))
    assert figure.END_PRICES == (Q(1), Q(0), Q(1))
    assert figure.BILL == 84
    assert tuple(figure.frame_parameter(index)
                 for index in figure.HOLD_INDICES) == (
                     Q(0), Q(1, 2), Q(1)
                 )
    assert tuple(figure.prices_at(parameter)
                 for parameter in (Q(0), Q(1, 2), Q(1))) == (
                     figure.START_PRICES,
                     figure.MIDDLE_PRICES,
                     figure.END_PRICES,
                 )
    assert all(
        figure.subtitle_for_frame(index)
        for index in range(figure.TOTAL_FRAMES)
    )
