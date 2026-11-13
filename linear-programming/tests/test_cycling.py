import math
import random
from fractions import Fraction as Q
from pathlib import Path

from figures import fig15a_cycle as cycle_figure
from linprog.corners import rank, tight
from linprog.lp import LP, best_by_enumeration
from linprog.simplex import simplex, two_phase

ROOT = Path(__file__).resolve().parents[1]
CYCLE_A = (
    (Q(1, 2), Q(-11, 2), Q(-5, 2), Q(9), Q(1), Q(0), Q(0)),
    (Q(1, 2), Q(-3, 2), Q(-1, 2), Q(1), Q(0), Q(1), Q(0)),
    (Q(1), Q(0), Q(0), Q(0), Q(0), Q(0), Q(1)),
)
CYCLE_B = (Q(0), Q(0), Q(1))
CYCLE_C = (Q(10), Q(-57), Q(-9), Q(-24), Q(0), Q(0), Q(0))
START_BASIS = (4, 5, 6)


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Q(0))


def matvec(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def assert_strong_duality(matrix, rhs, objective, result):
    assert result.status == "optimal"
    assert len(result.x) == len(objective)
    assert all(value >= 0 for value in result.x)
    assert matvec(matrix, result.x) == tuple(rhs)
    prices = result.certificate
    assert len(prices) == len(matrix)
    columns = tuple(
        tuple(matrix[row][column] for row in range(len(matrix)))
        for column in range(len(objective))
    )
    assert all(dot(prices, column) >= objective[index]
               for index, column in enumerate(columns))
    assert dot(prices, rhs) == dot(objective, result.x) == result.value


def test_dantzig_runs_the_exact_six_pivot_cycle_at_the_origin():
    result = simplex(CYCLE_A, CYCLE_B, CYCLE_C, START_BASIS, "dantzig")
    expected = (
        ((4, 5, 6), 0, 4),
        ((0, 5, 6), 1, 5),
        ((0, 1, 6), 2, 0),
        ((2, 1, 6), 3, 1),
        ((2, 3, 6), 4, 2),
        ((4, 3, 6), 5, 3),
    )
    assert result.status == "cycle"
    assert result.cycle_start == 0
    assert result.steps == result.cycle
    assert len(result.cycle) == 6
    assert tuple((step.basis, step.pivot.entering, step.pivot.leaving)
                 for step in result.cycle) == expected
    point = (Q(0), Q(0), Q(0), Q(0), Q(0), Q(0), Q(1))
    assert all(step.x == point and step.value == 0
               for step in result.cycle)
    assert all(step.pivot.theta == 0 for step in result.cycle)
    assert result.cycle[0].pivot.ratios[:2] == (Q(0), Q(0))
    assert result.cycle[0].pivot.leaving == 4
    assert set(result.basis) == set(START_BASIS)
    assert result.x == point and result.value == 0

    last = result.cycle[-1]
    repeated = tuple(
        last.pivot.entering if basic == last.pivot.leaving else basic
        for basic in last.basis
    )
    assert set(repeated) == set(START_BASIS)


def test_six_of_seven_rows_are_tight_at_the_origin():
    decision_rows = tuple(row[:4] for row in CYCLE_A)
    nonnegative_rows = tuple(
        tuple(Q(-int(column == index)) for column in range(4))
        for index in range(4)
    )
    rows = decision_rows + nonnegative_rows
    rhs = CYCLE_B + (Q(0),) * 4
    assert tight(rows, rhs, (0, 0, 0, 0)) == (0, 1, 3, 4, 5, 6)
    assert rank(rows[index] for index in (0, 1, 3, 4, 5, 6)) == 4


def test_bland_matches_five_pivots_then_reaches_the_optimum_in_seven():
    dantzig = simplex(CYCLE_A, CYCLE_B, CYCLE_C, START_BASIS, "dantzig")
    bland = simplex(CYCLE_A, CYCLE_B, CYCLE_C, START_BASIS, "bland",
                    max_pivots=20)
    pairs = tuple((step.pivot.entering, step.pivot.leaving)
                  for step in bland.steps
                  if step.pivot.status == "pivot")
    assert pairs[:5] == tuple(
        (step.pivot.entering, step.pivot.leaving)
        for step in dantzig.cycle[:5]
    )
    assert pairs == (
        (0, 4), (1, 5), (2, 0), (3, 1), (4, 2), (0, 3), (2, 6)
    )
    sixth = bland.steps[5]
    assert sixth.dictionary.reduced_costs[0] > 0
    assert sixth.dictionary.reduced_costs[5] > 0
    assert sixth.pivot.entering == 0
    assert bland.status == "optimal"
    assert len(pairs) == 7
    assert bland.x[:4] == (Q(1), Q(0), Q(1), Q(0))
    assert bland.value == 1


def test_max_pivots_guard_stops_before_taking_the_next_pivot():
    result = simplex(CYCLE_A, CYCLE_B, CYCLE_C, START_BASIS, "dantzig",
                     max_pivots=5)
    assert result.status == "limit"
    assert result.steps[-1].basis == (4, 3, 6)
    assert result.steps[-1].pivot.entering == 5


def test_random_degenerate_bland_runs_match_independent_enumeration():
    rng = random.Random(1501)
    for _ in range(24):
        bounds = (Q(rng.randint(2, 8)), Q(rng.randint(2, 8)))
        homogeneous = (
            (Q(1), Q(-1)),
            (Q(-1), Q(1)),
            (Q(-rng.randint(1, 4)), Q(-rng.randint(1, 4))),
            (Q(-rng.randint(1, 4)), Q(-rng.randint(1, 4))),
        )
        rows = ((Q(1), Q(0)), (Q(0), Q(1))) + homogeneous
        rhs = bounds + (Q(0),) * len(homogeneous)
        objective = (Q(rng.randint(1, 8)), Q(rng.randint(1, 8)))
        row_count = len(rows)
        standard_rows = tuple(
            tuple(row) + tuple(Q(int(row_index == slack_index))
                               for slack_index in range(row_count))
            for row_index, row in enumerate(rows)
        )
        standard_objective = objective + (Q(0),) * row_count
        result = simplex(
            standard_rows, rhs, standard_objective,
            tuple(range(2, 2 + row_count)), "bland", max_pivots=50,
        )
        enumerated = best_by_enumeration(
            LP.build(objective, rows, rhs)
        )[1]
        assert sum(bound == 0 for bound in rhs) >= 4
        assert result.status == "optimal"
        assert result.value == enumerated
        assert sum(step.pivot.status == "pivot"
                   for step in result.steps) <= 50


def test_two_phase_bland_proves_strong_duality_on_random_bounded_lps():
    rng = random.Random(1502)
    for _ in range(18):
        inequalities = tuple(
            (Q(rng.randint(1, 6)), Q(rng.randint(1, 6)))
            for _ in range(3)
        )
        rhs = tuple(Q(rng.randint(3, 24)) for _ in inequalities)
        row_count = len(inequalities)
        matrix = tuple(
            tuple(row) + tuple(Q(int(row_index == slack_index))
                               for slack_index in range(row_count))
            for row_index, row in enumerate(inequalities)
        )
        objective = tuple(Q(rng.randint(0, 9)) for _ in range(2)) \
            + (Q(0),) * row_count
        result = two_phase(
            matrix, rhs, objective, rule="bland", max_pivots=50
        )
        optimum = best_by_enumeration(
            LP.build(objective[:2], inequalities, rhs)
        )[1]
        assert_strong_duality(matrix, rhs, objective, result)
        assert result.value == optimum


def test_two_phase_pivots_out_and_drops_the_redundant_mill_glue_row():
    matrix = ((Q(1), Q(2)), (Q(1), Q(1)), (Q(2), Q(3)))
    rhs = (Q(32), Q(20), Q(52))
    objective = (Q(3), Q(5))
    result = two_phase(matrix, rhs, objective, rule="bland", max_pivots=50)
    assert result.status == "optimal"
    assert result.artificial_rows == (0, 1, 2)
    assert result.phase1.value == 0
    assert any(column in result.artificial_indices
               for column in result.phase1.basis)
    assert any(result.phase1.x[column] == 0
               for column in result.artificial_indices
               if column in result.phase1.basis)
    assert len(result.basis) == 2
    assert result.phase2 is not None
    assert len(result.phase2.steps[0].basis) == 2
    assert result.x == (Q(8), Q(12))
    assert result.value == 84
    assert_strong_duality(matrix, rhs, objective, result)


def test_cycle_figure_uses_exact_pivots_and_keeps_all_labels_anchored():
    assert cycle_figure.A == CYCLE_A
    assert cycle_figure.B == CYCLE_B
    assert cycle_figure.C == CYCLE_C
    assert cycle_figure.CYCLE_RESULT.status == "cycle"
    assert cycle_figure.CYCLE_ARROW_LABELS == (
        "x₁ in, x₅ out", "x₂ in, x₆ out", "x₃ in, x₁ out",
        "x₄ in, x₂ out", "x₅ in, x₃ out", "x₆ in, x₄ out",
    )
    assert cycle_figure.BLAND_ARROW_LABELS == (
        "x₁ in\nx₄ out", "x₃ in\nx₇ out"
    )
    assert cycle_figure.FINAL_POINT == (Q(1), Q(0), Q(1), Q(0))
    assert cycle_figure.FINAL_VALUE == 1
    for point in cycle_figure.NODE_POSITIONS:
        assert math.isclose(
            math.dist(point, cycle_figure.CENTER), cycle_figure.RADIUS
        )
    for index, anchor in enumerate(cycle_figure.CYCLE_ARROW_ANCHORS):
        start = cycle_figure.NODE_POSITIONS[index]
        end = cycle_figure.NODE_POSITIONS[
            (index + 1) % len(cycle_figure.NODE_POSITIONS)
        ]
        assert anchor == ((start[0] + end[0]) / 2,
                          (start[1] + end[1]) / 2)
    assert cycle_figure.BLAND_ARROW_ANCHORS == (
        ((cycle_figure.NODE_POSITIONS[5][0]
          + cycle_figure.BRANCH_NODE_POSITION[0]) / 2,
         cycle_figure.NODE_POSITIONS[5][1]),
        ((cycle_figure.BRANCH_NODE_POSITION[0]
          + cycle_figure.FINAL_NODE_POSITION[0]) / 2,
         cycle_figure.FINAL_NODE_POSITION[1]),
    )
    assert cycle_figure.TITLE
    assert len(cycle_figure.HOLD_INDICES) == len(cycle_figure.SUBTITLES)
    assert all(cycle_figure.subtitle_for_frame(index).strip()
               for index in range(cycle_figure.TOTAL_FRAMES))
    assert tuple(cycle_figure.frame_stage(index)
                 for index in cycle_figure.HOLD_INDICES) == tuple(
                     range(len(cycle_figure.SUBTITLES))
                 )


def test_chapter_fifteen_prose_numbers_and_cycle_figure_file():
    prose = (ROOT / "lesson.md").read_text()
    flat = " ".join(prose.split())
    for phrase in (
        "max 10x₁ − 57x₂ − 9x₃ − 24x₄",
        "After six pivots the basis is {x₅, x₆, x₇} again",
        "Every ratio test returned θ = 0",
        "x₁ and x₆ both have positive reduced cost",
        "z = 1, at x = (1, 0, 1, 0)",
        "chapters/15-cycling/cycle.gif",
    ):
        assert phrase in flat
    assert (ROOT / "chapters/15-cycling/cycle.gif").is_file()
