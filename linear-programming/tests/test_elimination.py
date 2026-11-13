import random
import re
from fractions import Fraction as Q
from itertools import product
from pathlib import Path

from figures.fig09a_shadow import (SHADOW_BOUNDARY_LABELS, SHADOW_CORNERS,
                                   SHADOW_ROWS, PLAN_POINT, PLAN_VALUE,
                                   ROOF_LABEL_ANCHOR, SHADOW_TOP)
from figures.fig09b_pairs import (HOLD_VALUES, V_FIXED, bounds_for_f,
                                  pair_marker_anchors, shadow_point_anchor,
                                  STAGES, END_F, f_at, _is_in_shadow)
from linprog import mill
from linprog.elimination import Row, eliminate, project
from linprog.lp import LP, best_by_enumeration, vertices

TOPIC = Path(__file__).resolve().parents[1]


def mill_rows(equality=False):
    source = [
        (tuple(mill.MILL.A[0]) + (Q(0),), mill.MILL.b[0]),
        (tuple(mill.MILL.A[1]) + (Q(0),), mill.MILL.b[1]),
        ((Q(-1), Q(0), Q(0)), Q(0)),
        ((Q(0), Q(-1), Q(0)), Q(0)),
        ((-mill.MILL.c[0], -mill.MILL.c[1], Q(1)), Q(0)),
    ]
    if equality:
        source.append(((mill.MILL.c[0], mill.MILL.c[1], Q(-1)), Q(0)))
    return [
        Row(coeffs, rhs, tuple(Q(int(i == j)) for j in range(len(source))))
        for i, (coeffs, rhs) in enumerate(source)
    ]


def assert_multiplier_invariant(rows, original, retained):
    for row in rows:
        assert len(row.mult) == len(original)
        assert all(value >= 0 for value in row.mult)
        full_coeffs = tuple(
            sum((row.mult[i] * original[i].coeffs[j]
                 for i in range(len(original))), Q(0))
            for j in range(len(original[0].coeffs))
        )
        assert tuple(full_coeffs[j] for j in retained) == row.coeffs
        assert sum((row.mult[i] * original[i].rhs
                    for i in range(len(original))), Q(0)) == row.rhs


def dot(coeffs, point):
    return sum((a * x for a, x in zip(coeffs, point)), Q(0))


def t_interval(f, value=V_FIXED):
    lower = max(Q(0), (value - mill.MILL.c[1] * f) / mill.MILL.c[0])
    upper = min(
        (mill.MILL.b[i] - mill.MILL.A[i][1] * f) / mill.MILL.A[i][0]
        for i in range(len(mill.MILL.b))
    )
    return lower, upper


def projected_f_interval(value):
    lower, upper = None, None
    for row in SHADOW_ROWS:
        coefficient = row.coeffs[0]
        rhs = row.rhs - row.coeffs[1] * value
        if coefficient > 0:
            bound = rhs / coefficient
            upper = bound if upper is None else min(upper, bound)
        elif coefficient < 0:
            bound = rhs / coefficient
            lower = bound if lower is None else max(lower, bound)
        elif rhs < 0:
            return None
    return lower, upper


def projected_by_interval(original, point, eliminated):
    lower, upper = None, None
    retained = [i for i in range(len(original[0].coeffs))
                if i != eliminated]
    for row in original:
        rest = sum((row.coeffs[j] * point[k]
                    for k, j in enumerate(retained)), Q(0))
        rhs = row.rhs - rest
        coefficient = row.coeffs[eliminated]
        if coefficient > 0:
            bound = rhs / coefficient
            upper = bound if upper is None else min(upper, bound)
        elif coefficient < 0:
            bound = rhs / coefficient
            lower = bound if lower is None else max(lower, bound)
        elif rhs < 0:
            return False
    return lower is None or upper is None or lower <= upper


def test_eliminating_t_keeps_zero_rows_then_pairs_with_certificates():
    original = mill_rows()
    upper_count = sum(row.coeffs[0] > 0 for row in original)
    lower_count = sum(row.coeffs[0] < 0 for row in original)
    zero_count = sum(row.coeffs[0] == 0 for row in original)
    assert (upper_count, lower_count, zero_count) == (2, 2, 1)

    rows = eliminate(original, 0)
    basis = lambda i: tuple(Q(int(i == j)) for j in range(len(original)))
    expected = [
        Row((-1, 0), 0, basis(3)),
        Row((2, 0), 32, tuple(a + b for a, b in
                              zip(basis(0), basis(2)))),
        Row((1, 1), 96, tuple(3 * a + b for a, b in
                              zip(basis(0), basis(4)))),
        Row((1, 0), 20, tuple(a + b for a, b in
                              zip(basis(1), basis(2)))),
        Row((-2, 1), 60, tuple(3 * a + b for a, b in
                               zip(basis(1), basis(4)))),
    ]
    assert rows == expected
    assert len(rows) == zero_count + upper_count * lower_count == 5
    assert_multiplier_invariant(rows, original, (1, 2))
    assert project(original, (1, 2)) == rows


def test_projecting_to_value_gives_six_rows_and_the_84_certificate():
    original = mill_rows()
    rows = project(original, (2,))
    assert len(rows) == 6
    assert_multiplier_invariant(rows, original, (2,))

    value_bounds = {
        row.rhs / row.coeffs[0]
        for row in rows if row.coeffs[0] > 0
    }
    assert value_bounds == {Q(96), Q(92), Q(100), Q(84)}
    assert min(value_bounds) == 84

    best_row = next(row for row in rows
                    if row.coeffs[0] > 0
                    and row.rhs / row.coeffs[0] == 84)
    scale = Q(1) / best_row.coeffs[0]
    assert tuple(scale * value for value in best_row.mult) == (
        Q(2), Q(1), Q(0), Q(0), Q(1)
    )
    assert scale * best_row.rhs == 84


def test_shadow_corners_match_exact_bounds_and_fixed_f_enumeration():
    expected_top = {
        (Q(0), Q(60)), (Q(12), Q(84)), (Q(16), Q(80)),
    }
    assert expected_top.issubset(set(SHADOW_CORNERS))
    assert {point for point in SHADOW_CORNERS if point[1] > 0} == expected_top

    for _, row, anchor in SHADOW_BOUNDARY_LABELS:
        assert dot(row.coeffs, anchor) == row.rhs
    assert ROOF_LABEL_ANCHOR[2] == mill.MILL.value(ROOF_LABEL_ANCHOR[:2])
    assert mill.MILL.feasible(PLAN_POINT)
    assert mill.MILL.value(PLAN_POINT) == PLAN_VALUE
    assert SHADOW_TOP == (PLAN_POINT[1], PLAN_VALUE)
    assert SHADOW_TOP in SHADOW_CORNERS

    for half_f in range(-4, 37):
        f = Q(half_f, 2)
        fixed_lp = LP.build(
            c=(mill.MILL.c[0],),
            A=tuple((mill.MILL.A[i][0],) for i in range(len(mill.MILL.b))),
            b=tuple(
                mill.MILL.b[i] - mill.MILL.A[i][1] * f
                for i in range(len(mill.MILL.b))
            ),
        )
        points = vertices(fixed_lp) if f >= 0 else []
        best_value = None
        if points:
            _, three_t = best_by_enumeration(fixed_lp)
            best_value = 5 * f + three_t

        for value in range(-20, 101, 2):
            value = Q(value)
            point = (f, value)
            row_membership = all(
                dot(row.coeffs, point) <= row.rhs for row in SHADOW_ROWS
            )
            interval_membership = f >= 0 and t_interval(f, value)[0] <= \
                t_interval(f, value)[1]
            enumeration_membership = (
                best_value is not None and best_value >= value
            )
            assert row_membership == interval_membership
            assert row_membership == enumeration_membership


def test_v78_intervals_equality_image_and_figure_anchors():
    assert V_FIXED == 78
    assert f_at(0) == 0
    assert f_at(STAGES.total - 1) == END_F == 18
    assert projected_f_interval(V_FIXED) == (Q(9), Q(16))
    expected = {
        Q(9): (Q(11), Q(11)),
        Q(12): (Q(6), Q(8)),
        Q(16): (Q(0), Q(0)),
        Q(17): (Q(0), Q(-2)),
    }
    assert HOLD_VALUES == tuple(expected)
    for f, interval in expected.items():
        assert bounds_for_f(f) == interval
        marker_anchors = pair_marker_anchors(f)
        assert marker_anchors == (
            Q(0),
            (V_FIXED - mill.MILL.c[1] * f) / mill.MILL.c[0],
            (mill.MILL.b[0] - mill.MILL.A[0][1] * f)
            / mill.MILL.A[0][0],
            (mill.MILL.b[1] - mill.MILL.A[1][1] * f)
            / mill.MILL.A[1][0],
        )
        point = shadow_point_anchor(f)
        assert point == (f, V_FIXED)
        assert _is_in_shadow(point) == (interval[0] <= interval[1])
        if f == 17:
            assert interval[0] > interval[1]
        else:
            assert interval[0] <= interval[1]

    for stage, value in zip((1, 3, 5, 7), HOLD_VALUES):
        start = sum(move + pause for move, pause in STAGES.spec[:stage])
        duration = STAGES.spec[stage][1]
        assert duration > 0
        assert all(f_at(frame) == value
                   for frame in range(start, start + duration))

    rows = project(mill_rows(equality=True), (2,))
    lower_bounds = [
        row.rhs / row.coeffs[0] for row in rows if row.coeffs[0] < 0
    ]
    upper_bounds = [
        row.rhs / row.coeffs[0] for row in rows if row.coeffs[0] > 0
    ]
    assert max(lower_bounds) == 0
    assert min(upper_bounds) == 84
    assert all(row.rhs >= 0 for row in rows if row.coeffs[0] == 0)


def test_cross_polytope_growth_and_final_interval():
    signs = tuple(product((-1, 1), repeat=4))
    original = [
        Row(pattern, 1, tuple(Q(int(i == j)) for j in range(len(signs))))
        for i, pattern in enumerate(signs)
    ]
    rows = original
    counts = [len(rows)]
    retained = [0, 1, 2, 3]
    for variable in (3, 2, 1):
        rows = eliminate(rows, variable)
        retained.remove(variable)
        counts.append(len(rows))
        assert_multiplier_invariant(rows, original, tuple(retained))

    assert counts == [16, 64, 288, 7856]
    upper = min(row.rhs / row.coeffs[0]
                for row in rows if row.coeffs[0] > 0)
    lower = max(row.rhs / row.coeffs[0]
                for row in rows if row.coeffs[0] < 0)
    assert (lower, upper) == (Q(-1), Q(1))
    assert all(row.rhs >= 0 for row in rows if row.coeffs[0] == 0)


def test_one_hundred_random_systems_preserve_certificates_and_feasibility():
    rng = random.Random(90909)
    feasible_count = 0
    infeasible_count = 0

    for _ in range(100):
        count = rng.randint(4, 6)
        source_data = [
            (tuple(Q(rng.randint(-3, 3)) for _ in range(3)),
             Q(rng.randint(-8, 8)))
            for _ in range(count)
        ]
        original = [
            Row(coeffs, rhs,
                tuple(Q(int(i == j)) for j in range(count)))
            for i, (coeffs, rhs) in enumerate(source_data)
        ]

        first = eliminate(original, 1)
        assert_multiplier_invariant(first, original, (0, 2))
        projected = project(original, (0, 2))
        assert_multiplier_invariant(projected, original, (0, 2))

        working = original
        retained = [0, 1, 2]
        for original_index in range(3):
            position = retained.index(original_index)
            working = eliminate(working, position)
            retained.pop(position)
            assert_multiplier_invariant(working, original, tuple(retained))
        fully_eliminated = working
        assert project(original, ()) == fully_eliminated

        for _ in range(8):
            point = (Q(rng.randint(-8, 8), 2),
                     Q(rng.randint(-8, 8), 2))
            expected = projected_by_interval(original, point, 1)
            actual = all(dot(row.coeffs, point) <= row.rhs
                         for row in projected)
            assert actual == expected

        split_lp = LP.build(
            c=(0,) * 6,
            A=[row.coeffs + tuple(-value for value in row.coeffs)
               for row in original],
            b=[row.rhs for row in original],
        )
        feasible = bool(vertices(split_lp))
        contradiction = any(
            not row.coeffs and row.rhs < 0 for row in fully_eliminated
        )
        assert contradiction == (not feasible)
        feasible_count += feasible
        infeasible_count += not feasible

    assert feasible_count > 0
    assert infeasible_count > 0


def test_prose_numbers_and_figure_paths_match_computations():
    lesson = (TOPIC / "lesson.md").read_text()
    chapter = lesson.split("## 9 · Shadows: eliminating a variable", 1)[1]
    chapter = re.split(r"\n## [^\n]+", chapter, maxsplit=1)[0]
    flat = re.sub(r"\s+", " ", chapter)

    source = mill_rows()
    t_rows = eliminate(source, 0)
    value_rows = project(source, (2,))
    top_corners = sorted(point for point in SHADOW_CORNERS if point[1] > 0)
    assert len(t_rows) == 5
    assert len(value_rows) == 6
    assert "0 ≤ f ≤ 16" in flat
    redundant_f_bound = max(
        row.rhs / row.coeffs[0]
        for row in t_rows
        if row.coeffs[0] > 0 and row.coeffs[1] == 0
    )
    assert f"f ≤ {redundant_f_bound}" in flat
    lathe_value_row = next(row for row in t_rows
                           if row.coeffs[1] > 0 and row.coeffs[0] > 0)
    press_value_row = next(row for row in t_rows
                           if row.coeffs[1] > 0 and row.coeffs[0] < 0)
    assert f"v + f ≤ {lathe_value_row.rhs}" in flat
    assert (f"v − 2f ≤ {press_value_row.rhs}" in flat)
    assert "f ≥ 0" in flat
    assert "3 × lathe + value" in flat
    assert "3 × press + value" in flat
    corner_phrase = (f"corners are ({top_corners[0][0]}, {top_corners[0][1]}), "
                     f"({top_corners[1][0]}, {top_corners[1][1]}) and "
                     f"({top_corners[2][0]}, {top_corners[2][1]})")
    assert corner_phrase in flat
    assert "top is at f = 12" in flat
    assert "v = 78" in flat
    assert "f = 9, where it is the single point t = 11" in flat
    assert "f = 12 (t from 6 to 8)" in flat
    assert "f = 16 (only t = 0)" in flat
    best_bound = min(
        row.rhs / row.coeffs[0]
        for row in value_rows if row.coeffs[0] > 0
    )
    best_row = next(
        row for row in value_rows
        if row.coeffs[0] > 0 and row.rhs / row.coeffs[0] == best_bound
    )
    scale = Q(1) / best_row.coeffs[0]
    normalized = tuple(scale * value for value in best_row.mult)
    prices = normalized[:2]
    resource_bound = sum(
        (prices[i] * mill.MILL.b[i] for i in range(len(prices))), Q(0)
    )
    assert "The smallest bound is " + str(best_bound) + ", the best value." in flat
    assert normalized == (Q(2), Q(1), Q(0), Q(0), Q(1))
    assert resource_bound == best_bound
    assert (f"{best_row.mult[0]} × lathe + {best_row.mult[1]} × press + "
            f"{best_row.mult[4]} × value") in flat
    assert (f"{prices[0]} × (t + 2f ≤ {mill.MILL.b[0]}) + "
            f"{prices[1]} × (t + f ≤ {mill.MILL.b[1]})") in flat
    assert (f"{normalized[4]} × (v − {mill.MILL.c[0]}t − "
            f"{mill.MILL.c[1]}f ≤ 0)") in flat
    assert (f"v ≤ {prices[0]} × {mill.MILL.b[0]} + "
            f"{prices[1]} × {mill.MILL.b[1]} = {resource_bound}") in flat
    equality_rows = project(mill_rows(equality=True), (2,))
    image_lower = max(
        row.rhs / row.coeffs[0]
        for row in equality_rows if row.coeffs[0] < 0
    )
    image_upper = min(
        row.rhs / row.coeffs[0]
        for row in equality_rows if row.coeffs[0] > 0
    )
    assert f"0 ≤ v ≤ {image_upper}" in flat
    assert image_lower == 0

    cross_rows = [
        Row(pattern, 1, tuple(Q(int(i == j)) for j in range(16)))
        for i, pattern in enumerate(product((-1, 1), repeat=4))
    ]
    counts = [len(cross_rows)]
    for index in (3, 2, 1):
        cross_rows = eliminate(cross_rows, index)
        counts.append(len(cross_rows))
    assert f"whose {counts[0]} rows are the sign patterns" in flat
    assert (f"gives {counts[1]}, then {counts[2]}, then "
            f"{counts[3]:,} rows") in flat
    assert "−1 ≤ x₁ ≤ 1" in flat

    for filename in ("shadow.gif", "pairs.gif"):
        relative = f"chapters/09-shadows/{filename}"
        assert relative in lesson
        assert (TOPIC / relative).is_file()
