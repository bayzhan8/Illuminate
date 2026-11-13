import random
import re
from fractions import Fraction as Q
from pathlib import Path

from figures.fig10a_cone import (
    CERTIFICATE_NORMAL,
    COLUMN_F,
    COLUMN_LABEL_ANCHORS,
    COLUMN_T,
    FRAME_COUNT,
    HOLD_FRAMES,
    NORMAL_ARROW_ANCHOR,
    OUTSIDE_HOLD_START,
    TARGET_END,
    TARGET_START,
    WALL_LABEL_ANCHOR,
    decomposition_at,
    parallelogram_vertices,
    target_at,
    target_is_in_cone,
    target_label_anchor,
)
from figures.fig10b_gordan import (
    CHAIN_LABEL_ANCHORS,
    CHAIN_LABELS,
    CHAIN_POINTS,
    DIRECTION,
    DIRECTION_LABEL_ANCHOR,
    HALF_PLANE_LABEL_ANCHOR,
    HALF_PLANE_POLYGON,
    ROW_LABEL_ANCHORS,
    ROW_ORIGIN,
    ROW_ORIGIN_LABEL_ANCHOR,
    ROWS,
    WEIGHTS,
    cross,
    dot,
)
from linprog import mill
from linprog.alternatives import cone_farkas, farkas, gordan
from linprog.lp import LP, solve_square, vertices

TOPIC = Path(__file__).resolve().parents[1]


def dot_product(left, right):
    return sum((a * b for a, b in zip(left, right)), Q(0))


def sum_rows(weights, rows):
    return tuple(
        sum((weight * row[j] for weight, row in zip(weights, rows)), Q(0))
        for j in range(len(rows[0]))
    )


def sum_rhs(weights, rhs):
    return dot_product(weights, rhs)


def free_system_feasible(A, b):
    dimension = len(A[0])
    split_rows = tuple(
        tuple(row) + tuple(-value for value in row) for row in A
    )
    lp = LP.build(c=(Q(0),) * (2 * dimension), A=split_rows, b=b)
    return bool(vertices(lp))


def cone_system_feasible(A, b):
    rows = tuple(A) + tuple(tuple(-value for value in row) for row in A)
    rhs = tuple(b) + tuple(-value for value in b)
    lp = LP.build(c=(Q(0),) * len(A[0]), A=rows, b=rhs)
    return bool(vertices(lp))


def assert_farkas_result(A, b, result):
    status, witness = result
    assert status in {"solution", "certificate"}
    if status == "solution":
        assert len(witness) == len(A[0])
        assert all(dot_product(row, witness) <= bound
                   for row, bound in zip(A, b))
    else:
        assert len(witness) == len(A)
        assert all(value >= 0 for value in witness)
        assert sum_rows(witness, A) == (Q(0),) * len(A[0])
        assert sum_rhs(witness, b) < 0
    return status


def assert_cone_result(A, b, result):
    status, witness = result
    assert status in {"solution", "certificate"}
    if status == "solution":
        assert len(witness) == len(A[0])
        assert all(value >= 0 for value in witness)
        assert tuple(dot_product(row, witness) for row in A) == tuple(b)
    else:
        assert len(witness) == len(A)
        columns = tuple(
            tuple(A[i][j] for i in range(len(A)))
            for j in range(len(A[0]))
        )
        assert all(dot_product(witness, column) >= 0
                   for column in columns)
        assert dot_product(witness, b) < 0
    return status


def assert_gordan_result(A, result):
    status, witness = result
    assert status in {"solution", "certificate"}
    if status == "solution":
        assert len(witness) == len(A[0])
        assert all(dot_product(row, witness) < 0 for row in A)
    else:
        assert len(witness) == len(A)
        assert all(value >= 0 for value in witness)
        assert sum(witness) > 0
        assert sum_rows(witness, A) == (Q(0),) * len(A[0])
    return status


def random_farkas_system(rng, case):
    dimension = rng.randint(1, 3)
    row_count = rng.randint(2, 5)
    rows = [
        tuple(rng.randint(-3, 3) for _ in range(dimension))
        for _ in range(row_count)
    ]
    if case % 2 == 0:
        point = tuple(rng.randint(-4, 4) for _ in range(dimension))
        rhs = tuple(dot_product(row, point) + rng.randint(0, 4)
                    for row in rows)
        return tuple(rows), rhs

    rows = rows[:-2]
    rhs = [rng.randint(-6, 6) for _ in rows]
    coordinate = rng.randrange(dimension)
    bound = rng.randint(-3, 3)
    positive = tuple(Q(int(j == coordinate)) for j in range(dimension))
    negative = tuple(-value for value in positive)
    rows.extend((positive, negative))
    rhs.extend((bound, -bound - 1))
    return tuple(rows), tuple(rhs)


def random_cone_system(rng, case):
    row_count = rng.randint(2, 4)
    dimension = rng.randint(1, 3)
    rows = [
        tuple(rng.randint(-3, 3) for _ in range(dimension))
        for _ in range(row_count)
    ]
    if case % 2 == 0:
        point = tuple(rng.randint(0, 4) for _ in range(dimension))
        rhs = tuple(dot_product(row, point) for row in rows)
    else:
        rows[0] = tuple(rng.randint(1, 3) for _ in range(dimension))
        rhs = (Q(-1),) + tuple(rng.randint(-4, 4)
                                for _ in range(row_count - 1))
    return tuple(rows), tuple(rhs)


def random_gordan_matrix(rng, case):
    row_count = rng.randint(2, 5)
    dimension = rng.randint(1, 3)
    rows = [
        tuple(rng.randint(-3, 3) for _ in range(dimension))
        for _ in range(row_count)
    ]
    if case % 2 == 0:
        rows = [
            (Q(rng.randint(1, 3)),) + row[1:]
            for row in rows
        ]
    else:
        positive = tuple(Q(int(j == 0)) for j in range(dimension))
        rows[0] = positive
        rows[1] = tuple(-value for value in positive)
    return tuple(rows)


def test_order_and_value_requests_have_exact_multiplier_certificates():
    lathe = tuple(mill.MILL.A[0])
    press = tuple(mill.MILL.A[1])
    not_t = (Q(-1), Q(0))
    not_f = (Q(0), Q(-1))

    lathe_order = (lathe, not_t, not_f)
    lathe_rhs = (mill.MILL.b[0], Q(-10), Q(-14))
    lathe_weights = (Q(1), Q(1), Q(2))
    assert sum_rows(lathe_weights, lathe_order) == (0, 0)
    assert sum_rhs(lathe_weights, lathe_rhs) == -6

    press_order = (press, not_t, not_f)
    press_rhs = (mill.MILL.b[1], Q(-10), Q(-14))
    press_weights = (Q(1), Q(1), Q(1))
    assert sum_rows(press_weights, press_order) == (0, 0)
    assert sum_rhs(press_weights, press_rhs) == -4

    order_A = (lathe, press, not_t, not_f)
    order_b = (mill.MILL.b[0], mill.MILL.b[1], Q(-10), Q(-14))
    order_result = farkas(order_A, order_b)
    assert assert_farkas_result(order_A, order_b, order_result) == \
        "certificate"

    value_row = (Q(-mill.MILL.c[0]), Q(-mill.MILL.c[1]))
    value_A = (lathe, press, value_row, not_t, not_f)
    value_b = (mill.MILL.b[0], mill.MILL.b[1], Q(-85), Q(0), Q(0))
    value_weights = (Q(2), Q(1), Q(1), Q(0), Q(0))
    assert sum_rows(value_weights, value_A) == (0, 0)
    assert sum_rhs(value_weights, value_b) == -1
    value_result = farkas(value_A, value_b)
    assert assert_farkas_result(value_A, value_b, value_result) == \
        "certificate"

    feasible_value_b = value_b[:2] + (Q(-84),) + value_b[3:]
    status, point = farkas(value_A, feasible_value_b)
    assert status == "solution"
    assert_farkas_result(value_A, feasible_value_b, (status, point))
    assert mill.MILL.value(point) == 84
    assert dot_product(value_row, point) <= -84


def test_cone_form_and_unrestricted_solution_examples():
    A = tuple(tuple(row) for row in mill.MILL.A)
    inside = (Q(32), Q(20))
    status, point = cone_farkas(A, inside)
    assert status == "solution"
    assert point == (Q(8), Q(12))
    assert_cone_result(A, inside, (status, point))

    outside = (Q(32), Q(10))
    unrestricted = solve_square(A, outside)
    assert unrestricted == (Q(-12), Q(22))
    status, certificate = cone_farkas(A, outside)
    assert status == "certificate"
    assert_cone_result(A, outside, (status, certificate))

    y = (Q(-1), Q(2))
    columns = tuple(
        tuple(A[i][j] for i in range(len(A)))
        for j in range(len(A[0]))
    )
    assert tuple(dot_product(y, column) for column in columns) == (1, 0)
    assert dot_product(y, outside) == -12


def test_gordan_examples_are_strict_and_cancel_exactly():
    A = ROWS
    status, certificate = gordan(A)
    assert status == "certificate"
    assert_gordan_result(A, (status, certificate))
    assert tuple(value * 2 / certificate[0] for value in certificate) == (
        Q(2), Q(1), Q(1)
    )

    two_rows = ROWS[:2]
    direction = (Q(-1), Q(-1))
    assert all(dot_product(row, direction) < 0 for row in two_rows)
    status, witness = gordan(two_rows)
    assert status == "solution"
    assert_gordan_result(two_rows, (status, witness))


def test_two_hundred_random_farkas_systems_match_split_variable_enumeration():
    rng = random.Random(1010)
    statuses = set()
    for case in range(200):
        A, b = random_farkas_system(rng, case)
        result = farkas(A, b)
        status = assert_farkas_result(A, b, result)
        statuses.add(status)
        assert free_system_feasible(A, b) == (status == "solution")
    assert statuses == {"solution", "certificate"}


def test_two_hundred_random_cones_match_independent_vertex_enumeration():
    rng = random.Random(1011)
    statuses = set()
    for case in range(200):
        A, b = random_cone_system(rng, case)
        result = cone_farkas(A, b)
        status = assert_cone_result(A, b, result)
        statuses.add(status)
        assert cone_system_feasible(A, b) == (status == "solution")
    assert statuses == {"solution", "certificate"}


def test_two_hundred_random_gordan_systems_match_split_variable_enumeration():
    rng = random.Random(1012)
    statuses = set()
    for case in range(200):
        A = random_gordan_matrix(rng, case)
        result = gordan(A)
        status = assert_gordan_result(A, result)
        statuses.add(status)
        assert free_system_feasible(A, (Q(-1),) * len(A)) == \
            (status == "solution")
    assert statuses == {"solution", "certificate"}


def test_cone_animation_holds_and_all_figure_labels_are_anchored():
    assert target_at(0) == TARGET_START == (Q(32), Q(20))
    assert target_at(FRAME_COUNT - 1) == TARGET_END == (Q(32), Q(10))
    assert decomposition_at(0) == (Q(8), Q(12))
    assert decomposition_at(FRAME_COUNT - 1) == (Q(-12), Q(22))
    assert all(target_at(frame) == TARGET_START
               for frame in range(HOLD_FRAMES))
    assert all(target_at(frame) == TARGET_END
               for frame in range(OUTSIDE_HOLD_START, FRAME_COUNT))

    for anchor, column in zip(COLUMN_LABEL_ANCHORS, (COLUMN_T, COLUMN_F)):
        assert cross(anchor, column) == 0
        assert dot_product(anchor, column) > 0
    assert cross(WALL_LABEL_ANCHOR, COLUMN_F) == 0
    assert dot_product(CERTIFICATE_NORMAL, WALL_LABEL_ANCHOR) == 0
    assert cross(CERTIFICATE_NORMAL, NORMAL_ARROW_ANCHOR) == 0
    assert dot_product(CERTIFICATE_NORMAL, COLUMN_T) == 1
    assert dot_product(CERTIFICATE_NORMAL, COLUMN_F) == 0

    for frame in range(FRAME_COUNT):
        b = target_at(frame)
        t, f = decomposition_at(frame)
        assert target_label_anchor(frame) == b
        assert (
            t * COLUMN_T[0] + f * COLUMN_F[0],
            t * COLUMN_T[1] + f * COLUMN_F[1],
        ) == b
        assert target_is_in_cone(frame) == (t >= 0 and f >= 0)
        vertices_at_frame = parallelogram_vertices(frame)
        assert vertices_at_frame[2] == b


def test_gordan_figure_labels_and_half_plane_match_their_objects():
    assert CHAIN_POINTS[0] == CHAIN_POINTS[-1] == (Q(0), Q(0))
    assert CHAIN_LABELS == tuple(str(weight) for weight in WEIGHTS)
    assert sum_rows(WEIGHTS, ROWS) == (Q(0), Q(0))

    for row, anchor in zip(ROWS, ROW_LABEL_ANCHORS):
        vector = tuple(anchor[j] - ROW_ORIGIN[j] for j in range(2))
        assert vector == row
        assert cross(vector, row) == 0
    assert ROW_ORIGIN_LABEL_ANCHOR == ROW_ORIGIN

    for i, (row, weight) in enumerate(zip(ROWS, WEIGHTS)):
        start, end = CHAIN_POINTS[i:i + 2]
        segment = tuple(end[j] - start[j] for j in range(2))
        assert segment == tuple(weight * value for value in row)
        anchor = CHAIN_LABEL_ANCHORS[i]
        offset = tuple(anchor[j] - start[j] for j in range(2))
        assert cross(segment, offset) == 0

    assert DIRECTION_LABEL_ANCHOR == DIRECTION
    assert all(dot(row, DIRECTION) < 0 for row in ROWS[:2])
    assert dot(HALF_PLANE_LABEL_ANCHOR, DIRECTION) < 0
    assert all(dot(point, DIRECTION) <= 0 for point in HALF_PLANE_POLYGON)


def test_chapter_ten_prose_numbers_and_figure_paths_match_the_code():
    lesson = (TOPIC / "lesson.md").read_text()
    flat = re.sub(r"\s+", " ", lesson)
    lathe = tuple(mill.MILL.A[0])
    press = tuple(mill.MILL.A[1])
    not_t, not_f = (Q(-1), Q(0)), (Q(0), Q(-1))

    order = (Q(10), Q(14))
    lathe_rows = (lathe, not_t, not_f)
    press_rows = (press, not_t, not_f)
    lathe_weights = (Q(1), Q(1), Q(2))
    press_weights = (Q(1), Q(1), Q(1))
    lathe_shortfall = sum_rhs(
        lathe_weights, (mill.MILL.b[0], -order[0], -order[1])
    )
    press_shortfall = sum_rhs(
        press_weights, (mill.MILL.b[1], -order[0], -order[1])
    )
    assert sum_rows(lathe_weights, lathe_rows) == (0, 0)
    assert sum_rows(press_weights, press_rows) == (0, 0)
    assert lathe_shortfall == -6
    assert press_shortfall == -4

    value_row = tuple(-value for value in mill.MILL.c)
    value_rows = (lathe, press, value_row)
    value_weights = (Q(2), Q(1), Q(1))
    value_target = Q(85)
    value_bound = sum_rhs(
        value_weights,
        (mill.MILL.b[0], mill.MILL.b[1], -value_target),
    )
    assert sum_rows(value_weights, value_rows) == (0, 0)
    assert value_bound == -1
    best_value = max(mill.MILL.value(point) for point in vertices(mill.MILL))
    assert best_value == 84

    A = tuple(tuple(row) for row in mill.MILL.A)
    inside = (Q(32), Q(20))
    inside_plan = (Q(8), Q(12))
    outside = (Q(32), Q(10))
    unrestricted = solve_square(A, outside)
    y = (Q(-1), Q(2))
    columns = tuple(
        tuple(A[i][j] for i in range(len(A)))
        for j in range(len(A[0]))
    )
    products = tuple(dot_product(y, column) for column in columns)
    outside_value = dot_product(y, outside)
    assert tuple(dot_product(row, inside_plan) for row in A) == inside
    assert unrestricted == (Q(-12), Q(22))
    assert products == (Q(1), Q(0))
    assert outside_value == -12

    expected = (
        f"sum: 0 ≤ −{abs(lathe_shortfall)}",
        f"0 ≤ −{abs(press_shortfall)}",
        f"sum: 0 ≤ −{abs(value_bound)}",
        f"needs {dot_product(lathe, order)} lathe hours and the mill has "
        f"{mill.MILL.b[0]}",
        f"needs {dot_product(press, order)} press hours and there are "
        f"{mill.MILL.b[1]}",
        f"at least {value_target},000 roubles",
        f"proof that {value_target} is impossible is the proof that "
        f"{best_value} is best",
        f"{inside_plan[0]}(1, 1) + {inside_plan[1]}(2, 1) = "
        f"({inside[0]}, {inside[1]})",
        f"t = −{abs(unrestricted[0])}, f = {unrestricted[1]}",
        f"y·(1, 1) = {products[0]} ≥ 0",
        f"y·(2, 1) = {products[1]} ≥ 0",
        f"y·(32, 10) = −{abs(outside_value)} < 0",
        "π = (2, 1, 1): 2(1, 2) + 1(1, 1) + 1(−3, −5) = (0, 0)",
        "d = (−1, −1) saves both",
    )
    assert all(phrase in flat for phrase in expected)

    for relative in (
        "chapters/10-plan-or-proof/cone.gif",
        "chapters/10-plan-or-proof/gordan.png",
    ):
        assert f"({relative})" in lesson
        assert (TOPIC / relative).is_file()
