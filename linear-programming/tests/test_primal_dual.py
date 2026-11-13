import random
from fractions import Fraction as Q
from itertools import permutations
from pathlib import Path

import pytest

from figures import fig19a_hungarian as figure
from linprog.primal_dual import hungarian, primal_dual
from linprog.simplex import two_phase

TOPIC = Path(__file__).resolve().parents[1]
COSTS = (
    (Q(4), Q(2), Q(5)),
    (Q(3), Q(6), Q(4)),
    (Q(5), Q(4), Q(7)),
)


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Q(0))


def assignment_lp(costs):
    size = len(costs)
    matrix = []
    for row in range(size):
        matrix.append(tuple(
            Q(int(column_row == row))
            for column_row in range(size)
            for _ in range(size)
        ))
    for column in range(size):
        matrix.append(tuple(
            Q(int(column_order == column))
            for _ in range(size)
            for column_order in range(size)
        ))
    rhs = (Q(1),) * (2 * size)
    objective = tuple(value for row in costs for value in row)
    return tuple(matrix), rhs, objective


def test_hungarian_rounds_match_every_number_and_fairness_claim():
    result = hungarian(COSTS)
    assert result.assignment == {0: 1, 1: 2, 2: 0}
    assert result.cost == 11
    assert result.u == (Q(4), Q(4), Q(6))
    assert result.v == (Q(-1), Q(-2), Q(0))
    assert len(result.rounds) == 3

    first, second, final = result.rounds
    assert (
        first.u, first.v, first.bound, first.tight, first.matching,
        first.S, first.N, first.theta, first.theta_pair,
    ) == (
        (Q(2), Q(3), Q(4)), (Q(0),) * 3, Q(9),
        ((0, 1), (1, 0), (2, 1)), ((0, 1), (1, 0)),
        (0, 2), (1,), Q(1), (2, 0),
    )
    assert (
        second.u, second.v, second.bound, second.tight, second.matching,
        second.S, second.N, second.theta, second.theta_pair,
    ) == (
        (Q(3), Q(3), Q(5)), (Q(0), Q(-1), Q(0)), Q(10),
        ((0, 1), (1, 0), (2, 0), (2, 1)), ((0, 1), (1, 0)),
        (0, 1, 2), (0, 1), Q(1), (1, 2),
    )
    assert (
        final.u, final.v, final.bound, final.tight, final.matching,
        final.S, final.N, final.theta, final.theta_pair,
    ) == (
        (Q(4), Q(4), Q(6)), (Q(-1), Q(-2), Q(0)), Q(11),
        ((0, 1), (1, 0), (1, 2), (2, 0), (2, 1)),
        ((0, 1), (1, 2), (2, 0)), (), (), None, None,
    )

    for index, round_ in enumerate(result.rounds):
        assert sum(round_.u) + sum(round_.v) == round_.bound
        assert all(
            round_.u[row] + round_.v[column] <= COSTS[row][column]
            for row in range(3)
            for column in range(3)
        )
        assert all(
            (row, column) in round_.tight
            for row, column in round_.matching
        )
        assert len({row for row, _ in round_.matching}) \
            == len(round_.matching)
        assert len({column for _, column in round_.matching}) \
            == len(round_.matching)
        if round_.theta is not None:
            assert len(round_.S) - len(round_.N) >= 1
            assert all(
                column in round_.N
                for row, column in round_.tight
                if row in round_.S
            )
            row, column = round_.theta_pair
            assert COSTS[row][column] - round_.u[row] - round_.v[column] \
                == round_.theta
            assert result.rounds[index + 1].bound > round_.bound

    assert sum(final.u) + sum(final.v) == result.cost


def test_random_hungarian_instances_match_permutation_enumeration():
    rng = random.Random(1901)
    for _ in range(200):
        size = rng.randint(1, 5)
        costs = tuple(
            tuple(Q(rng.randint(-12, 25), rng.choice((1, 2, 3)))
                  for _ in range(size))
            for _ in range(size)
        )
        result = hungarian(costs)
        brute = min(
            sum((costs[row][column] for row, column in enumerate(order)),
                Q(0))
            for order in permutations(range(size))
        )
        assert result.cost == brute
        assert sum(result.u) + sum(result.v) == result.cost


def test_primal_dual_raises_prices_until_the_restricted_plan_is_feasible():
    matrix = ((Q(1), Q(0)), (Q(0), Q(1)))
    rhs = (Q(1), Q(1))
    costs = (Q(2), Q(3))
    result = primal_dual(matrix, rhs, costs, (Q(0), Q(0)))

    assert result.status == "optimal"
    assert result.x == (Q(1), Q(1))
    assert result.pi == (Q(2), Q(3))
    assert result.value == Q(5) == dot(rhs, result.pi)
    assert tuple(
        (round_.pi, round_.tight, round_.lambda_, round_.theta,
         round_.bound, round_.limiting_column)
        for round_ in result.rounds
    ) == (
        ((Q(0), Q(0)), (), (Q(1), Q(1)), Q(2), Q(0), 0),
        ((Q(2), Q(2)), (0,), (Q(0), Q(1)), Q(1), Q(4), 1),
        ((Q(2), Q(3)), (0, 1), None, None, Q(5), None),
    )


def test_random_feasible_primal_dual_instances_match_two_phase():
    rng = random.Random(1902)
    for case in range(60):
        row_count = rng.randint(1, 3)
        variable_count = rng.randint(2, 4)
        matrix = tuple(
            tuple(Q(rng.randint(1, 6), rng.choice((1, 2, 3)))
                  for _ in range(variable_count))
            for _ in range(row_count)
        )
        witness = tuple(Q(rng.randint(1, 4)) for _ in range(variable_count))
        rhs = tuple(
            dot(row, witness) for row in matrix
        )
        pi = tuple(
            Q(rng.randint(-3, 4), rng.choice((1, 2)))
            for _ in range(row_count)
        )
        slacks = tuple(
            Q(0) if (case + column) % 4 == 0
            else Q(rng.randint(1, 8), rng.choice((1, 2, 3)))
            for column in range(variable_count)
        )
        columns = tuple(
            tuple(matrix[row][column] for row in range(row_count))
            for column in range(variable_count)
        )
        costs = tuple(
            dot(columns[column], pi) + slacks[column]
            for column in range(variable_count)
        )

        result = primal_dual(matrix, rhs, costs, pi)
        fresh = two_phase(
            matrix, rhs, tuple(-value for value in costs), rule="bland"
        )
        assert result.status == fresh.status == "optimal"
        assert result.value == -fresh.value
        assert result.value == dot(rhs, result.pi)
        assert all(value >= 0 for value in result.x)
        assert tuple(dot(row, result.x) for row in matrix) == rhs
        assert all(
            dot(columns[column], result.pi) <= costs[column]
            for column in range(variable_count)
        )
        for round_ in result.rounds:
            assert round_.bound == dot(rhs, round_.pi)
            assert all(
                dot(columns[column], round_.pi) <= costs[column]
                for column in range(variable_count)
            )
            assert round_.tight == tuple(
                column for column in range(variable_count)
                if dot(columns[column], round_.pi) == costs[column]
            )
            if round_.theta is not None:
                assert dot(round_.lambda_, rhs) > 0
                assert all(
                    dot(columns[column], round_.lambda_) <= 0
                    for column in round_.tight
                )
        assert all(
            result.rounds[index + 1].bound > round_.bound
            for index, round_ in enumerate(result.rounds)
            if round_.theta is not None
        )


def test_random_infeasible_primal_dual_instances_return_farkas_certificates():
    rng = random.Random(1903)
    for _ in range(30):
        variable_count = rng.randint(1, 4)
        row = tuple(
            Q(rng.randint(1, 5), rng.choice((1, 2, 3)))
            for _ in range(variable_count)
        )
        matrix = (row, row)
        first_rhs = Q(rng.randint(1, 8))
        second_rhs = first_rhs + Q(rng.randint(1, 5))
        rhs = (first_rhs, second_rhs)
        costs = (Q(0),) + tuple(
            Q(rng.randint(1, 8)) for _ in range(variable_count - 1)
        )
        result = primal_dual(matrix, rhs, costs, (Q(0), Q(0)))
        fresh = two_phase(
            matrix, rhs, tuple(-value for value in costs), rule="bland"
        )

        assert result.status == fresh.status == "infeasible"
        assert result.x is None and result.value is None
        assert dot(result.certificate, rhs) > 0
        assert all(
            dot(
                tuple(matrix[row_index][column]
                      for row_index in range(len(matrix))),
                result.certificate,
            ) <= 0
            for column in range(variable_count)
        )
        assert all(round_.bound == dot(rhs, round_.pi)
                   for round_ in result.rounds)


def test_assignment_lp_and_hungarian_dual_prices_agree():
    result = hungarian(COSTS)
    matrix, rhs, costs = assignment_lp(COSTS)
    prices = result.u + result.v
    solution = primal_dual(matrix, rhs, costs, prices)

    assert solution.status == "optimal"
    assert solution.value == result.cost == 11
    assert dot(rhs, solution.pi) == 11
    assert solution.x == tuple(
        Q(int(result.assignment[row] == column))
        for row in range(3)
        for column in range(3)
    )
    assert len(solution.rounds) == 1


def test_primal_dual_rejects_prices_that_are_not_dual_feasible():
    with pytest.raises(ValueError, match="dual-feasible"):
        primal_dual(((Q(1),),), (Q(1),), (Q(0),), (Q(1),))


def test_zero_rhs_has_the_zero_plan_as_a_primal_dual_optimum():
    result = primal_dual(
        ((Q(1), Q(2)), (Q(2), Q(4))),
        (Q(0), Q(0)),
        (Q(1), Q(2)),
        (Q(0), Q(0)),
    )
    assert result.status == "optimal"
    assert result.x == (Q(0), Q(0))
    assert result.value == dot((Q(0), Q(0)), result.pi) == Q(0)


def test_chapter_19_prose_figure_and_frame_anchors():
    prose = (TOPIC / "lesson.md").read_text()
    asset = "chapters/19-primal-dual/hungarian.gif"
    for phrase in (
        "u = (2, 3, 4), v = (0, 0, 0)",
        "The bound is 9.",
        "θ = 1, and lathe 3–birch goes tight",
        "u = (3, 3, 5), v = (0, −1, 0)",
        "θ = 1, and lathe 2–alder goes tight",
        "u = (4, 4, 6), v = (−1, −2, 0)",
        "cost is 2 + 4 + 5 = 11 = Σu + Σv",
        "λ = +1 on the u of S and −1 on the v of N(S)",
        "bound Σu + Σv = 9 → 10 → 11",
    ):
        assert phrase in prose
    assert asset in prose
    assert (TOPIC / asset).is_file()
    assert figure.RESULT.assignment == {0: 1, 1: 2, 2: 0}
    assert figure.RESULT.cost == 11
    assert figure.ROUND_BOUNDS == (Q(9), Q(10), Q(11))
    assert figure.ASSIGNMENT_CELLS == ((0, 1), (1, 2), (2, 0))
    assert figure.TITLE
    assert len(figure.HOLD_INDICES) == 3
    assert tuple(figure.frame_state(index)[0]
                 for index in figure.HOLD_INDICES) == (0, 1, 2)
    assert all(
        figure.subtitle_for_frame(index)
        for index in range(figure.TOTAL_FRAMES)
    )
