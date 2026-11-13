import random
from dataclasses import FrozenInstanceError, is_dataclass
from fractions import Fraction as Q
from pathlib import Path

import pytest

from figures import fig18a_flip as flip
from linprog.simplex import (
    BoundedSimplexResult,
    BoundedStep,
    bounded_simplex,
    dictionary,
    two_phase,
)

TOPIC = Path(__file__).resolve().parents[1]
MILL_A = (
    (Q(1), Q(2), Q(1), Q(0)),
    (Q(1), Q(1), Q(0), Q(1)),
)
MILL_B = (Q(32), Q(20))
MILL_C = (Q(3), Q(5), Q(0), Q(0))
MILL_LOWER = (Q(0),) * 4
MILL_UPPER = (None, Q(10), None, None)


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Q(0))


def explicit_upper_rows(matrix, rhs, objective, lower, upper):
    row_count = len(matrix)
    variable_count = len(objective)
    bounded = tuple(
        column for column, high in enumerate(upper) if high is not None
    )
    shifted_rhs = tuple(
        rhs[row] - dot(matrix[row], lower) for row in range(row_count)
    )
    extended_matrix = tuple(
        tuple(row) + (Q(0),) * len(bounded) for row in matrix
    )
    extended_rhs = list(shifted_rhs)
    for bound_row, column in enumerate(bounded):
        row = [Q(0)] * (variable_count + len(bounded))
        row[column] = Q(1)
        row[variable_count + bound_row] = Q(1)
        extended_matrix += (tuple(row),)
        extended_rhs.append(upper[column] - lower[column])
    extended_objective = tuple(objective) + (Q(0),) * len(bounded)
    return extended_matrix, tuple(extended_rhs), extended_objective


def random_bounded_case(rng, case):
    decision_count = rng.randint(1, 3)
    row_count = rng.randint(1, 2)
    decision_matrix = tuple(
        tuple(Q(rng.randint(1, 6), rng.choice((1, 2, 3)))
              for _ in range(decision_count))
        for _ in range(row_count)
    )
    decision_lower = tuple(
        Q(rng.randint(0, 3), rng.choice((1, 2, 3)))
        for _ in range(decision_count)
    )
    decision_upper = []
    for column, low in enumerate(decision_lower):
        if case % 7 == 0 and column == 0:
            high = low
        elif (case + column) % 4 == 0:
            high = None
        else:
            high = low + Q(rng.randint(1, 8), rng.choice((1, 2, 3)))
        decision_upper.append(high)
    if all(high is None for high in decision_upper):
        decision_upper[-1] = decision_lower[-1] + Q(1)

    slack_values = tuple(
        Q(rng.randint(1, 8), rng.choice((1, 2, 3)))
        for _ in range(row_count)
    )
    matrix = tuple(
        decision_matrix[row] + tuple(
            Q(int(row == column)) for column in range(row_count)
        )
        for row in range(row_count)
    )
    rhs = tuple(
        dot(decision_matrix[row], decision_lower) + slack_values[row]
        for row in range(row_count)
    )
    objective = tuple(
        Q(rng.randint(-4, 9), rng.choice((1, 2, 3)))
        for _ in range(decision_count)
    ) + (Q(0),) * row_count
    lower = decision_lower + (Q(0),) * row_count
    upper = tuple(decision_upper) + (None,) * row_count
    basis = tuple(decision_count + row for row in range(row_count))
    return matrix, rhs, objective, lower, upper, basis


def test_mill_flips_then_pivots_with_the_prose_values():
    result = bounded_simplex(
        MILL_A, MILL_B, MILL_C, MILL_LOWER, MILL_UPPER, (2, 3)
    )
    assert is_dataclass(result) and isinstance(result, BoundedSimplexResult)
    assert result.status == "optimal"
    assert len(result.steps) == 2

    flip_step, pivot_step = result.steps
    assert isinstance(flip_step, BoundedStep)
    assert (
        flip_step.basis, flip_step.at_upper, flip_step.x, flip_step.value,
        flip_step.entering, flip_step.direction, flip_step.kind,
    ) == (
        (2, 3), (), (Q(0), Q(0), Q(32), Q(20)), Q(0), 1, 1, "flip",
    )
    assert flip_step.limits == {
        "basic x_2 lower": Q(16),
        "basic x_3 lower": Q(20),
        "entering x_1 own bound": Q(10),
    }
    assert (
        pivot_step.basis, pivot_step.at_upper, pivot_step.x,
        pivot_step.value, pivot_step.entering, pivot_step.direction,
        pivot_step.kind,
    ) == (
        (2, 3), (1,), (Q(0), Q(10), Q(12), Q(10)), Q(50), 0, 1, "pivot",
    )
    assert pivot_step.limits == {
        "basic x_2 lower": Q(12),
        "basic x_3 lower": Q(10),
    }
    assert (
        result.basis, result.at_upper, result.x, result.value, result.y,
    ) == (
        (2, 0), (1,), (Q(10), Q(10), Q(2), Q(0)), Q(80),
        (Q(0), Q(3)),
    )

    initial = dictionary(MILL_A, MILL_B, MILL_C, (2, 3))
    assert initial.reduced_costs == (Q(3), Q(5), Q(0), Q(0))
    fbar_dictionary = (
        initial.x_B[0] - initial.rows[0][1] * Q(10),
        -initial.rows[0][0],
        initial.rows[0][1],
        initial.x_B[1] - initial.rows[1][1] * Q(10),
        -initial.rows[1][0],
        initial.rows[1][1],
        dot((MILL_C[2], MILL_C[3]), initial.x_B)
        + initial.reduced_costs[1] * Q(10),
        initial.reduced_costs[0],
        -initial.reduced_costs[1],
    )
    assert fbar_dictionary == (
        Q(12), Q(-1), Q(2), Q(10), Q(-1), Q(1),
        Q(50), Q(3), Q(-5),
    )

    final = dictionary(MILL_A, MILL_B, MILL_C, result.basis)
    assert final.x_B == (Q(12), Q(20))
    assert final.y == (Q(0), Q(3))
    assert final.reduced_costs == (Q(0), Q(2), Q(0), Q(-3))
    assert (
        final.x_B[0] - final.rows[0][1] * Q(10),
        -final.rows[0][3],
        final.rows[0][1],
        final.x_B[1] - final.rows[1][1] * Q(10),
        -final.rows[1][3],
        final.rows[1][1],
        dot((MILL_C[result.basis[0]], MILL_C[result.basis[1]]),
            final.x_B)
        + final.reduced_costs[1] * Q(10),
        final.reduced_costs[3],
        -final.reduced_costs[1],
    ) == (
        Q(2), Q(1), Q(1), Q(10), Q(-1), Q(1),
        Q(80), Q(-3), Q(-2),
    )
    assert Q(32) - result.x[0] - 2 * result.x[1] == 2
    assert Q(20) * result.y[1] + Q(10) * final.reduced_costs[1] == 80
    assert final.reduced_costs[1] == Q(5) - result.y[1] == 2
    assert flip.CAP_PRICE == Q(5) - Q(3)

    capped_a = tuple(row + (Q(0),) for row in MILL_A) + (
        (Q(0), Q(1), Q(0), Q(0), Q(1)),
    )
    capped = two_phase(
        capped_a,
        MILL_B + (Q(10),),
        MILL_C + (Q(0),),
        rule="bland",
    )
    assert capped.status == "optimal"
    assert len(capped.basis) == 3
    assert capped.x == (Q(10), Q(10), Q(2), Q(0), Q(0))
    assert capped.value == result.value == 80


def test_bound_ties_pivot_before_flip_and_choose_lowest_basic_index():
    tied_own = bounded_simplex(
        MILL_A, MILL_B, MILL_C, MILL_LOWER,
        (None, Q(16), None, None), (2, 3), max_pivots=1,
    )
    assert tied_own.status == "limit"
    assert tied_own.steps[0].limits["entering x_1 own bound"] == Q(16)
    assert tied_own.steps[0].kind == "pivot"
    assert tied_own.basis == (1, 3)

    matrix = (
        (Q(1), Q(0), Q(1)),
        (Q(0), Q(1), Q(1)),
    )
    lowest_basic = bounded_simplex(
        matrix, (Q(1), Q(1)), (Q(0), Q(0), Q(5)),
        (Q(0),) * 3, (None,) * 3, (1, 0), max_pivots=1,
    )
    assert lowest_basic.steps[0].kind == "pivot"
    assert lowest_basic.basis == (1, 2)


def test_entering_from_an_upper_bound_can_pivot_to_a_basic_upper_bound():
    result = bounded_simplex(
        ((Q(1), Q(1)),), (Q(2),), (Q(0), Q(-1)),
        (Q(0), Q(0)), (Q(3, 2), Q(1)), (0,), at_upper=(1,),
    )
    assert result.status == "optimal"
    assert len(result.steps) == 1
    step = result.steps[0]
    assert (step.entering, step.direction, step.kind) == (1, -1, "pivot")
    assert step.limits == {"basic x_0 upper": Q(1, 2),
                           "entering x_1 own bound": Q(1)}
    assert result.basis == (1,)
    assert result.at_upper == (0,)
    assert result.x == (Q(3, 2), Q(1, 2))
    assert result.value == Q(-1, 2)


def test_dantzig_and_bland_selection_and_unbounded_status():
    matrix = (
        (Q(1), Q(0), Q(1), Q(0)),
        (Q(0), Q(1), Q(0), Q(1)),
    )
    rhs = (Q(1), Q(1))
    objective = (Q(0), Q(0), Q(4), Q(5))
    upper = (None,) * 4
    dantzig = bounded_simplex(
        matrix, rhs, objective, (Q(0),) * 4, upper, (0, 1),
        max_pivots=1,
    )
    bland = bounded_simplex(
        matrix, rhs, objective, (Q(0),) * 4, upper, (0, 1),
        rule="bland", max_pivots=1,
    )
    assert dantzig.steps[0].entering == 3
    assert bland.steps[0].entering == 2
    assert dantzig.status == bland.status == "limit"
    guarded = bounded_simplex(
        matrix, rhs, objective, (Q(0),) * 4, upper, (0, 1),
        max_pivots=0,
    )
    assert guarded.status == "limit" and guarded.steps == ()

    for amount in range(1, 8):
        result = bounded_simplex(
            ((Q(1), Q(0)),), (Q(amount),), (Q(0), Q(amount + 1)),
            (Q(0), Q(0)), (None, None), (0,),
        )
        assert result.status == "unbounded"
        assert result.x == (Q(amount), Q(0))


def test_invalid_start_and_frozen_result_types():
    with pytest.raises(ValueError, match="feasible starting point"):
        bounded_simplex(
            ((Q(1), Q(0)),), (Q(2),), (Q(1), Q(0)),
            (Q(0), Q(0)), (Q(1), None), (0,),
        )
    result = bounded_simplex(
        MILL_A, MILL_B, MILL_C, MILL_LOWER, MILL_UPPER, (2, 3)
    )
    with pytest.raises(FrozenInstanceError):
        result.status = "changed"


def test_two_hundred_random_bounded_lps_match_explicit_upper_rows():
    rng = random.Random(1801)
    for case in range(200):
        matrix, rhs, objective, lower, upper, basis = random_bounded_case(
            rng, case
        )
        result = bounded_simplex(
            matrix, rhs, objective, lower, upper, basis, rule="bland",
            max_pivots=200,
        )
        assert result.status == "optimal", case
        extended = explicit_upper_rows(matrix, rhs, objective, lower, upper)
        comparison = two_phase(*extended, rule="bland", max_pivots=200)
        assert comparison.status == "optimal", case
        assert result.value == comparison.value + dot(objective, lower), case
        assert all(low <= value and (high is None or value <= high)
                   for value, low, high in zip(result.x, lower, upper)), case


def test_chapter_18_prose_numbers_figure_and_frame_anchors():
    prose = (TOPIC / "lesson.md").read_text()
    asset = "chapters/18-bounds/flip.gif"
    assert asset in prose
    assert (TOPIC / asset).is_file()
    for phrase in (
        "f = 10 − f̄",
        "s₁ = 12 − t + 2f̄",
        "s₂ = 10 − t + f̄",
        "z = 50 + 3t − 5f̄",
        "t = 10 − s₂ + f̄",
        "s₁ = 2 + s₂ + f̄",
        "z = 80 − 3s₂ − 2f̄",
        "press hour: 3",
        "cap: 2 per batch",
        "20·3 + 10·2 = 80",
    ):
        assert phrase in prose

    assert flip.TITLE
    assert flip.START_POINT == (Q(0), Q(0))
    assert flip.FLIP_POINT == (Q(0), Q(10))
    assert flip.FINAL_POINT == (Q(10), Q(10))
    assert flip.LIMITS == (Q(16), Q(20), Q(10))
    assert flip.RESULT.status == "optimal"
    assert flip.RESULT.value == 80
    assert tuple(flip.dictionary_text("flip").splitlines()) == (
        "s₁ = 12 − t + 2f̄",
        "s₂ = 10 − t + f̄",
        "z = 50 + 3t − 5f̄",
    )
    assert tuple(flip.dictionary_text("final").splitlines()) == (
        "t = 10 − s₂ + f̄",
        "s₁ = 2 + s₂ + f̄",
        "z = 80 − 3s₂ − 2f̄",
    )
    assert flip.FINAL_PRICE_TEXT == "press 3, cap 2, bill 80"
    assert flip.START_LABEL_ANCHOR == (Q(0), Q(0))
    assert flip.FLIP_LABEL_ANCHOR == (Q(0), Q(10))
    assert flip.FINAL_LABEL_ANCHOR == (Q(10), Q(10))
    assert sum(flip.LATHE_WALL_ANCHOR[i] * (1, 2)[i]
               for i in range(2)) == 32
    assert sum(flip.PRESS_WALL_ANCHOR) == 20
    assert flip.CAP_LINE_ANCHOR[1] == 10
    assert flip.LIMIT_LABELS == ("lathe", "press", "own ceiling")
    assert flip.HOLD_INDICES
    assert all(flip.subtitle_for_frame(i) for i in range(flip.TOTAL_FRAMES))
    assert all(flip.frame_state(i)[0] in range(5)
               for i in range(flip.TOTAL_FRAMES))
    assert flip.subtitle_for_frame(flip.HOLD_INDICES[1]) == \
        "bound flip: no basis change, basis still s₁, s₂"
