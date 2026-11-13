import random
from fractions import Fraction as Q
from pathlib import Path

from figures.fig14a_pivot import (
    CORNER_LABEL_ANCHORS,
    F_EDGE_LABEL_ANCHOR,
    HOLD_INDICES as PIVOT_HOLDS,
    MILL_A,
    MILL_B,
    MILL_C,
    POINTS,
    ROW_LABEL_ANCHORS as PIVOT_ROW_ANCHORS,
    T_EDGE_LABEL_ANCHOR,
    TITLE as PIVOT_TITLE,
    TOTAL_FRAMES as PIVOT_FRAMES,
    basis_text as pivot_basis_text,
    dictionary_text as pivot_dictionary_text,
    frame_state as pivot_frame_state,
    subtitle_for_frame as pivot_subtitle,
)
from figures.fig14b_ray import (
    A as RAY_A,
    BASE_POINT,
    COLUMN_T,
    RAY_DIRECTION,
    RAY_LABEL_ANCHOR,
    REDUCED_COST_T,
    RESULT as RAY_RESULT,
    dictionary_text as ray_dictionary_text,
)
from figures.fig14c_phase import (
    A as PHASE_A,
    B as PHASE_B,
    C as PHASE_C,
    CORNER_LABEL_ANCHORS as PHASE_CORNER_ANCHORS,
    HOLD_INDICES as PHASE_HOLDS,
    TITLE as PHASE_TITLE,
    ORDER_LABEL_ANCHOR,
    PRESS_LABEL_ANCHOR,
    TOTAL_FRAMES as PHASE_FRAMES,
    LATHE_LABEL_ANCHOR,
    _phase_data as phase_data,
    basis_text as phase_basis_text,
    dictionary_text as phase_dictionary_text,
    frame_state as phase_frame_state,
    phase_ratio_rows,
    ratio_value_text,
    subtitle_for_frame as phase_subtitle,
)
from linprog.corners import rank
from linprog.lp import LP, best_by_enumeration
from linprog.sensitivity import basis_inverse
from linprog.simplex import dictionary, pivot_step, simplex, two_phase

TOPIC = Path(__file__).resolve().parents[1]


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Q(0))


def matvec(A, x):
    return tuple(dot(row, x) for row in A)


def test_three_mill_dictionaries_and_ratio_tests_are_exact():
    initial = dictionary(MILL_A, MILL_B, MILL_C, (2, 3))
    assert initial.x_B == (Q(32), Q(20))
    assert initial.y == (Q(0), Q(0))
    assert initial.reduced_costs == (Q(3), Q(5), Q(0), Q(0))
    assert initial.rows == (
        (Q(1), Q(2), Q(1), Q(0)),
        (Q(1), Q(1), Q(0), Q(1)),
    )
    assert tuple(pivot_dictionary_text(simplex(
        MILL_A, MILL_B, MILL_C, (2, 3)
    ).steps[0]).splitlines()) == (
        "s₁ = 32 − t − 2f",
        "s₂ = 20 − t − f",
        "z = 0 + 3t + 5f",
    )
    first = pivot_step(MILL_A, MILL_B, MILL_C, (2, 3))
    assert first.status == "pivot"
    assert (first.entering, first.ratios, first.leaving, first.theta) == (
        1, (Q(16), Q(20)), 2, Q(16)
    )

    middle = dictionary(MILL_A, MILL_B, MILL_C, (1, 3))
    assert middle.x_B == (Q(16), Q(4))
    assert middle.y == (Q(5, 2), Q(0))
    assert middle.reduced_costs == (Q(1, 2), Q(0), Q(-5, 2), Q(0))
    assert middle.rows == (
        (Q(1, 2), Q(1), Q(1, 2), Q(0)),
        (Q(1, 2), Q(0), Q(-1, 2), Q(1)),
    )
    second = pivot_step(MILL_A, MILL_B, MILL_C, (1, 3))
    assert second.status == "pivot"
    assert (second.entering, second.ratios, second.leaving, second.theta) == (
        0, (Q(32), Q(8)), 3, Q(8)
    )

    final = dictionary(MILL_A, MILL_B, MILL_C, (1, 0))
    assert final.x_B == (Q(12), Q(8))
    assert final.y == (Q(2), Q(1))
    assert final.reduced_costs == (Q(0), Q(0), Q(-2), Q(-1))
    assert final.rows == (
        (Q(0), Q(1), Q(1), Q(-1)),
        (Q(1), Q(0), Q(-1), Q(2)),
    )
    assert pivot_step(MILL_A, MILL_B, MILL_C, (1, 0)).status == "optimal"
    assert pivot_dictionary_text(simplex(MILL_A, MILL_B, MILL_C, (2, 3))
                                 .steps[-1]).splitlines()[-1] \
        == "z = 84 − 2s₁ − s₂"


def test_mill_dictionaries_reconstruct_the_three_prose_tableaux():
    variables = ("t", "f", "s₁", "s₂")
    result = simplex(MILL_A, MILL_B, MILL_C, (2, 3))

    def tableau(iteration):
        state = iteration.dictionary
        rows = tuple(
            (
                variables[basic],
                state.rows[iteration.basis.index(basic)],
                state.x_B[iteration.basis.index(basic)],
            )
            for basic in sorted(iteration.basis)
        )
        return rows + (("z", state.reduced_costs, -iteration.value),)

    initial, first_pivot, final = tuple(map(tableau, result.steps))
    assert initial == (
        ("s₁", (Q(1), Q(2), Q(1), Q(0)), Q(32)),
        ("s₂", (Q(1), Q(1), Q(0), Q(1)), Q(20)),
        ("z", (Q(3), Q(5), Q(0), Q(0)), Q(0)),
    )
    assert first_pivot == (
        ("f", (Q(1, 2), Q(1), Q(1, 2), Q(0)), Q(16)),
        ("s₂", (Q(1, 2), Q(0), Q(-1, 2), Q(1)), Q(4)),
        ("z", (Q(1, 2), Q(0), Q(-5, 2), Q(0)), Q(-80)),
    )
    assert final == (
        ("t", (Q(1), Q(0), Q(-1), Q(2)), Q(8)),
        ("f", (Q(0), Q(1), Q(1), Q(-1)), Q(12)),
        ("z", (Q(0), Q(0), Q(-2), Q(-1)), Q(-84)),
    )

    first_rows = initial[:2]
    assert tuple(
        (row[2], row[1][1]) for row in first_rows
    ) == ((Q(32), Q(2)), (Q(20), Q(1)))
    assert tuple(row[2] / row[1][1] for row in first_rows) \
        == (Q(16), Q(20))
    assert tuple(row[1][1] for row in initial[1:]) == (Q(1), Q(5))

    second_rows = first_pivot[:2]
    assert tuple(
        (row[2], row[1][0]) for row in second_rows
    ) == ((Q(16), Q(1, 2)), (Q(4), Q(1, 2)))
    assert tuple(row[2] / row[1][0] for row in second_rows) \
        == (Q(32), Q(8))
    assert tuple(row[1][0] for row in (first_pivot[0], first_pivot[2])) \
        == (Q(1, 2), Q(1, 2))

    slack_columns = tuple(
        tuple(row[1][column] for column in (2, 3))
        for row in final[:2]
    )
    assert slack_columns == ((Q(-1), Q(2)), (Q(1), Q(-1)))
    assert slack_columns == basis_inverse(
        MILL_A, MILL_B, MILL_C, (0, 1)
    )
    assert tuple(-value for value in final[2][1][2:]) == (
        Q(2), Q(1)
    )


def test_figure_dictionary_format_and_phase_ratio_winners():
    steps = simplex(MILL_A, MILL_B, MILL_C, (2, 3)).steps
    assert tuple(pivot_dictionary_text(steps[1]).splitlines()) == (
        "f = 16 − t/2 − s₁/2",
        "s₂ = 4 − t/2 + s₁/2",
        "z = 80 + t/2 − (5/2)s₁",
    )
    assert pivot_basis_text(steps[1]) == "basis: f, s₂"
    assert pivot_basis_text(steps[-1]) == "basis: f, t"

    phase1, variables, objective, _ = phase_data(0)
    assert phase_basis_text(phase1, variables) == "basis: s₁, s₂, a"
    assert phase_dictionary_text(phase1, variables, objective).splitlines()[-1] \
        == "z = −14 + f − e"
    phase2, variables, objective, _ = phase_data(5)
    phase2_lines = phase_dictionary_text(phase2, variables, objective).splitlines()
    assert phase_basis_text(phase2, variables) == "basis: e, s₂, f"
    assert phase2_lines[0] == "e = 2 − t/2 − s₁/2"
    assert phase2_lines[-1] == "z = 80 + t/2 − (5/2)s₁"

    assert phase_ratio_rows(0) == (
        ("lathe", Q(16), False),
        ("press", Q(20), False),
        ("order", Q(14), True),
    )
    assert phase_ratio_rows(3) == (
        ("lathe", Q(2), True),
        ("press", Q(6), False),
    )
    assert phase_ratio_rows(5) == (
        ("order e", Q(4), True),
        ("press", Q(8), False),
        ("f", Q(32), False),
    )
    assert ratio_value_text(Q(14), True) == "14  ← leaves"
    assert ratio_value_text(Q(20), False) == "20"


def test_dantzig_and_bland_choose_their_declared_entering_columns():
    matrix = (
        (Q(1), Q(0), Q(1), Q(0)),
        (Q(0), Q(1), Q(0), Q(1)),
    )
    rhs = (Q(1), Q(1))
    objective = (Q(0), Q(0), Q(4), Q(5))
    dantzig = pivot_step(matrix, rhs, objective, (0, 1), "dantzig")
    bland = pivot_step(matrix, rhs, objective, (0, 1), "bland")
    assert dantzig.entering == 3
    assert bland.entering == 2
    tied = pivot_step(matrix, rhs, (0, 0, 5, 5), (0, 1), "dantzig")
    assert tied.entering == 2


def test_unbounded_ray_dictionary_and_extreme_ray_rank():
    result = RAY_RESULT
    assert result.status == "unbounded"
    assert BASE_POINT == (Q(0), Q(4))
    first = result.steps[0]
    assert first.x == (Q(0), Q(4), Q(0))
    assert first.dictionary.reduced_costs == (Q(8), Q(0), Q(-5))
    assert first.dictionary.x_B == (Q(4),)
    assert first.pivot.status == "unbounded"
    assert first.pivot.entering == 0
    assert first.pivot.ray == (Q(1), Q(1), Q(0))
    assert RAY_DIRECTION == (Q(1), Q(1))
    assert REDUCED_COST_T == 8 and COLUMN_T == -1
    assert ray_dictionary_text() == "f = 4 + t − s\nz = 20 + 8t − 5s"
    assert matvec(RAY_A, first.pivot.ray) == (Q(0),)
    assert all(value >= 0 for value in first.pivot.ray)
    assert dot((Q(3), Q(5), Q(0)), first.pivot.ray) == 8
    active = (RAY_A[0], (Q(0), Q(0), Q(-1)))
    assert rank(active) == 2


def test_two_phase_paths_dictionaries_and_phase_one_artificial():
    result = two_phase(PHASE_A, PHASE_B, PHASE_C)
    assert result.status == "optimal"
    assert result.artificial_rows == (2,)
    assert result.artificial_indices == (5,)
    assert result.phase1.status == "optimal"
    assert result.phase1.value == 0
    assert tuple(step.x[:2] for step in result.phase1.steps) == (
        (Q(0), Q(0)), (Q(0), Q(14))
    )
    assert result.phase1.steps[0].pivot.ratios == (
        Q(16), Q(20), Q(14)
    )
    assert result.phase1.steps[0].pivot.leaving == 5

    phase2 = result.phase2
    assert phase2 is not None and phase2.status == "optimal"
    assert tuple(step.x[:2] for step in phase2.steps) == (
        (Q(0), Q(14)), (Q(0), Q(16)), (Q(4), Q(14))
    )
    start = phase2.steps[0]
    assert set(start.basis) == {1, 2, 3}
    assert start.dictionary.x_B == (Q(4), Q(6), Q(14))
    assert start.dictionary.y == (Q(0), Q(0), Q(5))
    assert start.dictionary.reduced_costs == (
        Q(3), Q(0), Q(0), Q(0), Q(5)
    )
    assert start.pivot.entering == 4
    assert start.pivot.ratios == (Q(2), Q(6), None)
    assert phase2.steps[1].value == 80
    assert phase2.steps[1].pivot.entering == 0
    assert phase2.steps[1].pivot.ratios == (
        Q(4), Q(8), Q(32)
    )
    final = phase2.steps[-1]
    assert phase2.value == 82
    assert set(final.basis) == {0, 1, 3}
    assert final.dictionary.y == (Q(3), Q(0), Q(-1))
    assert final.dictionary.reduced_costs == (
        Q(0), Q(0), Q(-3), Q(0), Q(-1)
    )
    assert result.certificate == (Q(3), Q(0), Q(-1))

    order_15 = two_phase(PHASE_A, (Q(32), Q(20), Q(15)), PHASE_C)
    assert order_15.value == 81
    assert order_15.x[:2] == (Q(2), Q(15))

    t_first = simplex(PHASE_A, PHASE_B, PHASE_C, (2, 3, 1),
                      rule="bland")
    assert t_first.status == "optimal"
    assert len(t_first.steps) == 2
    assert t_first.steps[0].pivot.entering == 0
    assert t_first.x[:2] == (Q(4), Q(14))


def test_random_bounded_standard_form_lp_matches_enumeration_and_dual():
    rng = random.Random(1401)
    for _ in range(24):
        matrix = (
            (Q(1), Q(0), Q(rng.randint(1, 5)), Q(rng.randint(1, 5))),
            (Q(0), Q(1), Q(rng.randint(1, 5)), Q(rng.randint(1, 5))),
        )
        rhs = (Q(rng.randint(5, 24)), Q(rng.randint(5, 24)))
        objective = tuple(Q(rng.randint(-2, 9)) for _ in range(4))
        results = (
            simplex(matrix, rhs, objective, (0, 1), "dantzig"),
            simplex(matrix, rhs, objective, (0, 1), "bland"),
        )
        equality_lp = LP.build(
            objective,
            matrix + tuple(tuple(-value for value in row) for row in matrix),
            rhs + tuple(-value for value in rhs),
        )
        _, optimum = best_by_enumeration(equality_lp)
        assert all(result.status == "optimal" for result in results)
        assert all(result.value == optimum for result in results)
        assert results[0].value == results[1].value
        result = results[0]
        dual = result.certificate
        columns = tuple(
            tuple(matrix[row][column] for row in range(len(matrix)))
            for column in range(len(objective))
        )
        assert all(dot(dual, column) >= objective[index]
                   for index, column in enumerate(columns))
        assert dot(dual, rhs) == result.value


def test_random_unbounded_rays_and_infeasible_phase_one_optima():
    rng = random.Random(1402)
    for _ in range(18):
        row_count = rng.randint(1, 3)
        matrix = tuple(
            tuple(Q(int(row == column)) for column in range(row_count + 1))
            for row in range(row_count)
        )
        rhs = tuple(Q(rng.randint(1, 9)) for _ in range(row_count))
        objective = tuple(Q(rng.randint(-3, 3)) for _ in range(row_count)) \
            + (Q(rng.randint(1, 7)),)
        result = simplex(matrix, rhs, objective, tuple(range(row_count)))
        assert result.status == "unbounded"
        ray = result.certificate
        assert matvec(matrix, ray) == (Q(0),) * row_count
        assert all(value >= 0 for value in ray)
        assert dot(objective, ray) > 0

    for _ in range(18):
        row_count = rng.randint(1, 4)
        matrix = tuple(
            tuple(Q(int(row == column)) for column in range(row_count))
            for row in range(row_count)
        )
        rhs = [Q(rng.randint(1, 8)) for _ in range(row_count)]
        rhs[rng.randrange(row_count)] = Q(-rng.randint(1, 8))
        objective = tuple(Q(rng.randint(-2, 6)) for _ in range(row_count))
        result = two_phase(matrix, tuple(rhs), objective)
        assert result.status == "infeasible"
        assert result.phase1.value < 0


def test_chapter_numbers_figure_assets_and_all_frame_anchors():
    assets = (
        "chapters/14-simplex/pivot.gif",
        "chapters/14-simplex/ray.png",
        "chapters/14-simplex/phase.gif",
    )
    prose = (TOPIC / "lesson.md").read_text()
    for phrase in (
        "### The same pivots as a tableau",
        "Most textbooks and every exam write the dictionaries as a **tableau**.",
        "32/2 < 20/1",
        "s₂ row loses 1 copy and the z row loses 5",
        "Divide by 1/2, then clear t's column",
        "4 ÷ 1/2 = 8 < 16 ÷ 1/2 = 32",
        "the z row loses 1/2",
        "B⁻¹:** the slack columns s₁, s₂ of the final tableau",
        "s₁ = 32 − t − 2f",
        "f = 16 − t/2 − s₁/2",
        "z = 80 + t/2 − (5/2)s₁",
        "z = 84 − 2s₁ − s₂",
        "z = 20 + 8t − 5s",
        "f − e + a = 14",
        "z = 82 − 3s₁ − e",
    ):
        assert phrase in prose
    for asset in assets:
        assert asset in prose
        assert (TOPIC / asset).is_file()

    assert CORNER_LABEL_ANCHORS == POINTS == (
        (Q(0), Q(0)), (Q(0), Q(16)), (Q(8), Q(12))
    )
    assert PIVOT_ROW_ANCHORS[0][0] + 2 * PIVOT_ROW_ANCHORS[0][1] == 32
    assert sum(PIVOT_ROW_ANCHORS[1]) == 20
    assert F_EDGE_LABEL_ANCHOR[0] == 0
    assert T_EDGE_LABEL_ANCHOR[0] + 2 * T_EDGE_LABEL_ANCHOR[1] == 32
    assert RAY_LABEL_ANCHOR[1] - RAY_LABEL_ANCHOR[0] == 4
    assert ORDER_LABEL_ANCHOR[1] == 14
    assert LATHE_LABEL_ANCHOR[0] + 2 * LATHE_LABEL_ANCHOR[1] == 32
    assert sum(PRESS_LABEL_ANCHOR) == 20
    assert PHASE_CORNER_ANCHORS == (
        (Q(0), Q(0)), (Q(0), Q(14)),
        (Q(0), Q(16)), (Q(4), Q(14)),
    )
    assert all(pivot_subtitle(i) for i in range(PIVOT_FRAMES))
    assert all(phase_subtitle(i) for i in range(PHASE_FRAMES))
    assert PIVOT_TITLE and PHASE_TITLE
    assert tuple(pivot_frame_state(i)[0] for i in PIVOT_HOLDS) == (0, 2, 4)
    assert tuple(phase_frame_state(i)[0] for i in PHASE_HOLDS) == (
        0, 2, 3, 5, 7
    )
    assert len(PIVOT_HOLDS) == 3 and len(PHASE_HOLDS) == 5
