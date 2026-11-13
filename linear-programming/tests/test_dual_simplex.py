import random
from fractions import Fraction as Q
from pathlib import Path

from figures import fig16a_repair as repair
from figures.fig12a_kink import chapter_lp
from linprog.lp import LP, best_by_enumeration
from linprog.simplex import (
    add_row, dictionary, dual_pivot_step, dual_simplex, simplex, two_phase,
)

ROOT = Path(__file__).resolve().parents[1]
BASE_A = (
    (Q(1), Q(2), Q(1), Q(0)),
    (Q(1), Q(1), Q(0), Q(1)),
)
BASE_B = (Q(32), Q(20))
BASE_C = (Q(3), Q(5), Q(0), Q(0))
START_BASIS = (0, 1)
GLUE_ROW = (Q(2), Q(3), Q(0), Q(0))
ADDED_A, ADDED_B, ADDED_C, ADDED_BASIS = add_row(
    BASE_A, BASE_B, BASE_C, START_BASIS, GLUE_ROW, Q(50)
)


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Q(0))


def matvec(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def assert_optimal_certificate(matrix, rhs, objective, result):
    assert result.status == "optimal"
    assert matvec(matrix, result.x) == tuple(rhs)
    assert all(value >= 0 for value in result.x)
    prices = result.certificate
    columns = tuple(
        tuple(matrix[row][column] for row in range(len(matrix)))
        for column in range(len(objective))
    )
    assert len(prices) == len(matrix)
    assert all(dot(prices, column) >= objective[index]
               for index, column in enumerate(columns))
    assert dot(prices, rhs) == dot(objective, result.x) == result.value


def assert_dual_steps(result):
    for index, step in enumerate(result.steps):
        pivot = step.pivot
        if pivot.status != "pivot":
            continue
        assert index + 1 < len(result.steps)
        following = result.steps[index + 1]
        assert pivot.leaving_row is not None
        assert following.x[pivot.entering] > 0
        row = pivot.leaving_row
        b_bar = step.dictionary.x_B[row]
        a_bar = step.dictionary.rows[row][pivot.entering]
        assert b_bar < 0 and a_bar < 0
        change = step.dictionary.reduced_costs[pivot.entering] * (
            b_bar / a_bar
        )
        assert change <= 0
        assert following.value - step.value == change


def random_base_system(rng):
    decision_rows = (
        (Q(1), Q(0)),
        (Q(0), Q(1)),
        (Q(rng.randint(1, 4)), Q(rng.randint(1, 4))),
        (Q(rng.randint(1, 4)), Q(rng.randint(1, 4))),
    )
    rhs = (
        Q(rng.randint(8, 18)),
        Q(rng.randint(8, 18)),
        Q(rng.randint(30, 60)),
        Q(rng.randint(30, 60)),
    )
    row_count = len(decision_rows)
    matrix = tuple(
        tuple(row) + tuple(Q(int(row_index == slack_index))
                           for slack_index in range(row_count))
        for row_index, row in enumerate(decision_rows)
    )
    objective = (Q(rng.randint(1, 9)), Q(rng.randint(1, 9))) \
        + (Q(0),) * row_count
    basis = tuple(range(2, 2 + row_count))
    optimum = simplex(
        matrix, rhs, objective, basis, rule="bland", max_pivots=100
    )
    assert optimum.status == "optimal"
    return decision_rows, rhs, matrix, objective, optimum


def test_add_row_and_the_broken_mill_dictionary_are_exact():
    assert ADDED_A == (
        (Q(1), Q(2), Q(1), Q(0), Q(0)),
        (Q(1), Q(1), Q(0), Q(1), Q(0)),
        (Q(2), Q(3), Q(0), Q(0), Q(1)),
    )
    assert ADDED_B == (Q(32), Q(20), Q(50))
    assert ADDED_C == (Q(3), Q(5), Q(0), Q(0), Q(0))
    assert ADDED_BASIS == (0, 1, 4)

    start = dictionary(ADDED_A, ADDED_B, ADDED_C, ADDED_BASIS)
    assert start.x_B == (Q(8), Q(12), Q(-2))
    assert start.y == (Q(2), Q(1), Q(0))
    assert start.reduced_costs == (
        Q(0), Q(0), Q(-2), Q(-1), Q(0)
    )
    assert start.rows == (
        (Q(1), Q(0), Q(-1), Q(2), Q(0)),
        (Q(0), Q(1), Q(1), Q(-1), Q(0)),
        (Q(0), Q(0), Q(-1), Q(-1), Q(1)),
    )
    assert repair.basis_text(repair.START_DICTIONARY) == "basis: t, f, s₃"
    assert repair.dictionary_text(repair.START_DICTIONARY).splitlines() == [
        "t = 8 + s₁ − 2s₂",
        "f = 12 − s₁ + s₂",
        "s₃ = −2 + s₁ + s₂",
        "z = 84 − 2s₁ − s₂",
    ]

    final = dictionary(ADDED_A, ADDED_B, ADDED_C, (0, 1, 3))
    assert final.x_B == (Q(4), Q(14), Q(2))
    assert final.y == (Q(1), Q(0), Q(1))
    assert final.reduced_costs == (
        Q(0), Q(0), Q(-1), Q(0), Q(-1)
    )
    assert final.rows == (
        (Q(1), Q(0), Q(-3), Q(0), Q(2)),
        (Q(0), Q(1), Q(2), Q(0), Q(-1)),
        (Q(0), Q(0), Q(1), Q(1), Q(-1)),
    )
    assert repair.dictionary_text(repair.FINAL_DICTIONARY).splitlines() == [
        "t = 4 + 3s₁ − 2s₃",
        "f = 14 − 2s₁ + s₃",
        "s₂ = 2 − s₁ + s₃",
        "z = 82 − s₁ − s₃",
    ]


def test_dual_ratio_test_and_mill_repair_match_every_number():
    pivot = dual_pivot_step(
        ADDED_A, ADDED_B, ADDED_C, ADDED_BASIS, rule="dantzig"
    )
    assert pivot.status == "pivot"
    assert pivot.ratios == (None, None, Q(2), Q(1), None)
    assert (pivot.entering, pivot.leaving, pivot.leaving_row, pivot.ratio) \
        == (3, 4, 2, Q(1))

    result = dual_simplex(
        ADDED_A, ADDED_B, ADDED_C, ADDED_BASIS, max_pivots=10
    )
    assert result.status == "optimal"
    assert len(result.steps) == 2
    assert result.steps[0].pivot.ratios == pivot.ratios
    assert result.steps[0].pivot.entering == 3
    assert result.steps[0].pivot.leaving == 4
    assert result.steps[0].value == 84
    assert result.steps[1].value == 82
    assert result.x == (Q(4), Q(14), Q(0), Q(2), Q(0))
    assert result.certificate == (Q(1), Q(0), Q(1))
    assert_dual_steps(result)
    assert_optimal_certificate(ADDED_A, ADDED_B, ADDED_C, result)

    chapter12_point, chapter12_value = best_by_enumeration(
        chapter_lp(glue_stock=Q(50))
    )
    assert chapter12_point == result.x[:2] == (Q(4), Q(14))
    assert chapter12_value == result.value == 82


def test_dual_feasibility_and_leaving_rules():
    try:
        dual_pivot_step(BASE_A, BASE_B, BASE_C, (2, 3))
    except ValueError as exc:
        assert "dual-feasible" in str(exc)
    else:
        raise AssertionError("a dual-infeasible basis must be rejected")

    try:
        dual_simplex(BASE_A, BASE_B, BASE_C, (2, 3))
    except ValueError as exc:
        assert "dual-feasible" in str(exc)
    else:
        raise AssertionError("dual_simplex must reject a dual-infeasible start")

    matrix = ((Q(1), Q(0)), (Q(0), Q(1)))
    rhs = (Q(-1), Q(-2))
    objective = (Q(0), Q(0))
    dantzig = dual_pivot_step(matrix, rhs, objective, (0, 1), "dantzig")
    bland = dual_pivot_step(matrix, rhs, objective, (0, 1), "bland")
    assert dantzig.status == bland.status == "infeasible"
    assert dantzig.leaving == 1
    assert bland.leaving == 0
    assert dantzig.certificate == (Q(0), Q(1))
    assert bland.certificate == (Q(1), Q(0))

    tied_matrix = (
        (Q(1), Q(0), Q(-1), Q(-2)),
        (Q(0), Q(1), Q(0), Q(0)),
    )
    tied = dual_pivot_step(
        tied_matrix, (Q(-1), Q(0)), (Q(0), Q(0), Q(-2), Q(-4)),
        (0, 1), "bland",
    )
    assert tied.ratios == (None, None, Q(2), Q(2))
    assert tied.entering == 2


def test_random_added_rows_reoptimize_with_dual_simplex():
    rng = random.Random(1601)
    for _ in range(20):
        decision_rows, rhs, matrix, objective, optimum = \
            random_base_system(rng)
        row_decision = (Q(rng.randint(1, 4)), Q(rng.randint(1, 4)))
        old_usage = dot(row_decision, optimum.x[:2])
        assert old_usage > 0
        new_rhs = old_usage * Q(rng.randint(1, 3), 4)
        added_row = row_decision + (Q(0),) * len(decision_rows)
        new_A, new_b, new_c, new_basis = add_row(
            matrix, rhs, objective, optimum.basis, added_row, new_rhs
        )
        result = dual_simplex(
            new_A, new_b, new_c, new_basis, rule="bland", max_pivots=100
        )
        fresh = two_phase(
            new_A, new_b, new_c, rule="bland", max_pivots=100
        )
        assert result.status == fresh.status == "optimal"
        assert result.value == fresh.value
        assert_dual_steps(result)
        assert_optimal_certificate(new_A, new_b, new_c, result)


def test_random_infeasible_rows_return_farkas_certificates():
    rng = random.Random(1602)
    for _ in range(12):
        decision_rows, rhs, matrix, objective, optimum = \
            random_base_system(rng)
        positive_row = (Q(rng.randint(1, 4)), Q(rng.randint(1, 4)))
        _, maximum = best_by_enumeration(
            LP.build(positive_row, decision_rows, rhs)
        )
        added_row = tuple(-value for value in positive_row) \
            + (Q(0),) * len(decision_rows)
        new_A, new_b, new_c, new_basis = add_row(
            matrix, rhs, objective, optimum.basis, added_row, -(maximum + 1)
        )
        result = dual_simplex(
            new_A, new_b, new_c, new_basis, rule="bland", max_pivots=100
        )
        fresh = two_phase(
            new_A, new_b, new_c, rule="bland", max_pivots=100
        )
        assert result.status == fresh.status == "infeasible"
        assert_dual_steps(result)
        witness = result.certificate
        assert len(witness) == len(new_A)
        assert all(value >= 0 for value in matvec(
            tuple(zip(*new_A)), witness
        ))
        assert dot(witness, new_b) < 0


def test_dual_simplex_guard_and_chapter_16_figure_anchors():
    limited = dual_simplex(
        ADDED_A, ADDED_B, ADDED_C, ADDED_BASIS, max_pivots=0
    )
    assert limited.status == "limit"
    assert limited.steps[0].pivot.status == "pivot"

    assert repair.A == ADDED_A
    assert repair.B == ADDED_B
    assert repair.C == ADDED_C
    assert repair.RESULT.status == "optimal"
    assert repair.START == (Q(8), Q(12))
    assert repair.FINAL == (Q(4), Q(14))
    assert repair.START_GLUE == 52 and repair.FINAL_GLUE == 50
    assert repair.START_VALUE == 84 and repair.FINAL_VALUE == 82
    assert repair.START_EXCESS == 2
    assert repair.RATIO_VALUES == (Q(2), Q(1))
    assert repair.PRICE_VECTOR == (Q(1), Q(0), Q(1))
    assert repair.PRICE_BILL_TEXT == \
        "prices y = (1, 0, 1)    bill 32 + 50 = 82"
    assert repair.point_at(0) == repair.START
    assert repair.point_at(1) == repair.FINAL
    assert repair.point_at(Q(1, 2)) == (Q(6), Q(13))
    assert dot(repair.GLUE_ROW[:2], repair.GLUE_WALL_ANCHOR) == 50
    assert dot(repair.LATHE_ROW, repair.LATHE_WALL_ANCHOR) == 32
    assert dot(repair.PRESS_ROW, repair.PRESS_WALL_ANCHOR) == 20
    assert repair.START_LABEL_ANCHOR == repair.START
    assert repair.FINAL_LABEL_ANCHOR == repair.FINAL
    assert repair.RATIO_ROW_ANCHORS == (
        (Q(1, 2), Q(1)), (Q(1, 2), Q(0))
    )
    assert repair.RATIO_LABEL_ANCHORS == (
        (Q(9, 20), Q(1)), (Q(1, 4), Q(0))
    )
    assert repair.TITLE
    assert tuple(repair.frame_state(index)[0]
                 for index in repair.HOLD_INDICES) == (0, 1, 2, 3)
    assert all(repair.subtitle_for_frame(index).strip()
               for index in range(repair.TOTAL_FRAMES))


def test_chapter_16_prose_numbers_and_figure_file():
    prose = (ROOT / "lesson.md").read_text()
    flat = " ".join(prose.split())
    for phrase in (
        "s₃ = −2 + s₁ + s₂",
        "z = 84 − 2s₁ − s₂",
        "2·8 + 3·12 = 52",
        "lathe 2/1 = 2, press 1/1 = 1",
        "t = 4 + 3s₁ − 2s₃",
        "f = 14 − 2s₁ + s₃",
        "s₂ = 2 − s₁ + s₃",
        "z = 82 − s₁ − s₃",
        "The new prices are lathe 1, press 0 and glue 1",
        "bill is 32·1 + 50·1 = 82",
        "At the glue pivot, s₂ entered at 2 > 0.",
        "Here it was −1 · 2 = −2, from 84 to 82.",
        "chapters/16-dual-simplex/repair.gif",
    ):
        assert phrase in flat
    assert (ROOT / "chapters/16-dual-simplex/repair.gif").is_file()
