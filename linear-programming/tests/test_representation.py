"""Exact checks for corner-plus-ray representations."""

from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import random

from figures import fig13a_decompose as decomposition_figure
from figures import fig13b_slice as slice_figure
from figures.fig11c_crash import BUYER, BUYER_RHS
from linprog import mill
from linprog.corners import basic_points, is_bfs, is_direction, rank, tight
from linprog.lp import LP, vertices
from linprog.representation import (decompose, extreme_rays, recession_cone,
                                    weyl)

TOPIC = Path(__file__).resolve().parents[1]
BUYER_C = mill.MILL.b
MILL_A = tuple(mill.MILL.A) + ((Q(-1), Q(0)), (Q(0), Q(-1)))
MILL_B = tuple(mill.MILL.b) + (Q(0), Q(0))


def dot(a, x):
    return sum((left * right for left, right in zip(a, x)), Q(0))


def contains(rows, point):
    return all(dot(row.coeffs, point) <= row.rhs for row in rows)


def represented_by_lp(points, rays, point):
    dimension = len(point)
    variable_count = len(points) + len(rays)
    rows, rhs = [], []
    for coordinate in range(dimension):
        equality = tuple(vertex[coordinate] for vertex in points) + tuple(
            ray[coordinate] for ray in rays
        )
        rows.extend((equality, tuple(-value for value in equality)))
        rhs.extend((point[coordinate], -point[coordinate]))
    lambda_sum = (Q(1),) * len(points) + (Q(0),) * len(rays)
    rows.extend((lambda_sum, tuple(-value for value in lambda_sum)))
    rhs.extend((Q(1), Q(-1)))
    lp = LP.build(c=(0,) * variable_count, A=rows, b=rhs)
    return bool(vertices(lp))


def test_buyer_offer_decomposes_exactly_and_splits_its_bill():
    start = (Q(4), Q(4))
    (weights, escape), steps = decompose(BUYER, BUYER_RHS, start)
    assert weights == {
        (Q(2), Q(1)): Q(5, 6),
        (Q(0), Q(5)): Q(1, 6),
    }
    assert escape == (Q(7, 3), Q(7, 3))
    assert len(steps) == 2
    first, second = steps
    assert (first.point, first.direction, first.positive_step) == (
        start, (Q(-1), Q(-1)), Q(7, 3))
    assert first.positive_point == (Q(5, 3), Q(5, 3))
    assert first.negative_step is None and first.negative_point is None
    assert (second.point, second.direction, second.positive_step,
            second.negative_step) == (
                (Q(5, 3), Q(5, 3)), (Q(1), Q(-2)), Q(1, 3), Q(5, 3))
    assert second.positive_point == (Q(2), Q(1))
    assert second.negative_point == (Q(0), Q(5))

    directions = iter(((-1, -1), (1, -2)))
    (pinned_weights, pinned_escape), _ = decompose(
        BUYER, BUYER_RHS, start, choose=lambda basis: next(directions)
    )
    assert (pinned_weights, pinned_escape) == (weights, escape)
    total_bill = dot(BUYER_C, start)
    assert total_bill == 208
    assert total_bill == (
        Q(5, 6) * dot(BUYER_C, (2, 1))
        + Q(1, 6) * dot(BUYER_C, (0, 5))
        + Q(7, 3) * dot(BUYER_C, (1, 1))
    )
    assert (Q(5, 6) * 84, Q(1, 6) * 100, Q(7, 3) * 52) == (
        Q(70), Q(50, 3), Q(364, 3))


def test_buyer_recession_cone_slice_and_extreme_rays():
    cone_A, cone_b = recession_cone(BUYER)
    assert cone_A == BUYER
    assert cone_b == (Q(0),) * len(BUYER)
    assert slice_figure.SLICE_NORMAL == (Q(4), Q(3))
    assert set(slice_figure.SLICE_ENDPOINTS) == {
        (Q(1, 4), Q(0)), (Q(0), Q(1, 3)),
    }
    assert {ray for ray in extreme_rays(BUYER)} == {
        (Q(1), Q(0)), (Q(0), Q(1)),
    }
    assert all(is_direction(BUYER, ray)
               for ray in extreme_rays(BUYER))
    assert slice_figure.SAMPLE_HIT == (Q(1, 7), Q(1, 7))
    assert dot(slice_figure.SLICE_NORMAL, slice_figure.SAMPLE_HIT) == 1
    assert tuple(7 * value for value in slice_figure.SAMPLE_HIT) == (1, 1)

    assert recession_cone(MILL_A) == (MILL_A, (Q(0),) * len(MILL_A))
    assert extreme_rays(MILL_A) == ()


def test_random_bounded_and_unbounded_pointed_polyhedra_decompose():
    rng = random.Random(1301)
    for bounded in (True, False):
        for _ in range(24):
            width, height = rng.randint(1, 7), rng.randint(1, 7)
            A = ((Q(-1), Q(0)), (Q(0), Q(-1)), (Q(1), Q(0)))
            b = (Q(0), Q(0), Q(width))
            if bounded:
                A += ((Q(0), Q(1)),)
                b += (Q(height),)
                point = (Q(rng.randint(0, 3 * width), 3),
                         Q(rng.randint(0, 3 * height), 3))
                point = (min(point[0], Q(width)), min(point[1], Q(height)))
            else:
                point = (Q(rng.randint(0, 3 * width), 3),
                         Q(rng.randint(0, 12), 3))

            (weights, escape), _ = decompose(A, b, point)
            assert weights and all(weight >= 0 for weight in weights.values())
            assert sum(weights.values(), Q(0)) == 1
            assert is_direction(A, escape)
            assert tuple(
                sum((weight * corner[index]
                     for corner, weight in weights.items()), Q(0))
                + escape[index]
                for index in range(2)
            ) == point
            for corner in weights:
                assert all(dot(row, corner) <= bound
                           for row, bound in zip(A, b))
                assert is_bfs(A, b, corner)
            if bounded:
                assert escape == (Q(0), Q(0))


def test_weyl_rows_match_random_generator_combinations_and_lp_membership():
    rng = random.Random(1302)
    possible_rays = ((1, 0), (0, 1), (1, 1), (2, 1), (1, 2))
    for _ in range(18):
        points = tuple(
            tuple(Q(rng.randint(-3, 3)) for _ in range(2))
            for _ in range(3)
        )
        rays = tuple(
            tuple(map(Q, ray))
            for ray in rng.sample(possible_rays, rng.randint(1, 2))
        )
        rows = weyl(points, rays)
        for _ in range(5):
            raw = tuple(rng.randint(1, 5) for _ in points)
            total = sum(raw)
            weights = tuple(Q(value, total) for value in raw)
            amounts = tuple(Q(rng.randint(0, 6), 3) for _ in rays)
            point = tuple(
                sum((weights[i] * points[i][coordinate]
                     for i in range(len(points))), Q(0))
                + sum((amounts[i] * rays[i][coordinate]
                       for i in range(len(rays))), Q(0))
                for coordinate in range(2)
            )
            assert contains(rows, point)
            assert represented_by_lp(points, rays, point)

        outside = (min(point[0] for point in points) - 1, Q(rng.randint(-4, 4)))
        assert not represented_by_lp(points, rays, outside)
        assert not contains(rows, outside)


def test_cube_and_diamond_corner_row_counts():
    cube = tuple(tuple(map(Q, corner))
                 for corner in product((0, 1), repeat=3))
    cube_A = tuple(
        tuple(Q(int(index == coordinate)) * sign for index in range(3))
        for coordinate in range(3) for sign in (1, -1)
    )
    cube_b = tuple(Q(1 if row[coordinate] > 0 else 0)
                   for coordinate in range(3) for row in
                   (cube_A[2 * coordinate], cube_A[2 * coordinate + 1]))
    cube_rows = weyl(cube, ())
    cube_lp = LP.build(c=(0, 0, 0), A=cube_A, b=cube_b)
    assert len(cube_rows) == 6
    assert len(vertices(cube_lp)) == 8
    assert all(contains(cube_rows, point) for point in cube)

    diamond = tuple(
        tuple(Q(sign if coordinate == axis else 0) for coordinate in range(3))
        for axis in range(3) for sign in (1, -1)
    )
    diamond_rows = weyl(diamond, ())
    diamond_points = {
        point for point, feasible in basic_points(
            tuple(row.coeffs for row in diamond_rows),
            tuple(row.rhs for row in diamond_rows),
        ) if feasible
    }
    assert len(diamond) == 6
    assert len(diamond_rows) == 8
    assert len(diamond_points) == 6


def test_chapter_thirteen_figure_anchors_frames_and_prose_numbers():
    assert decomposition_figure.TITLE.strip()
    assert len(decomposition_figure.STEP_LOG) == 2
    assert all(decomposition_figure.subtitle_for_frame(index).strip()
               for index in range(decomposition_figure.TOTAL_FRAMES))
    assert tuple(decomposition_figure.frame_state(index)[0]
                 for index in decomposition_figure.HOLD_INDICES) == (0, 2, 4)
    for row, bound, anchor in zip(
            BUYER, BUYER_RHS, decomposition_figure.ROW_LABEL_ANCHORS):
        assert dot(row, anchor) == bound
    assert decomposition_figure.CORNER_LABEL_ANCHORS == (
        (Q(0), Q(5)), (Q(2), Q(1)))
    assert decomposition_figure.WEIGHT_LABEL_ANCHORS == \
        decomposition_figure.CORNER_LABEL_ANCHORS
    assert decomposition_figure.bill_split() == (
        (Q(70), Q(50, 3), Q(364, 3)), Q(208))
    assert tuple(decomposition_figure.format_amount(value)
                 for value in decomposition_figure.bill_split()[0]) == (
                     "70", "16.67", "121.33")

    assert slice_figure.TITLE.strip() and slice_figure.SUBTITLE.strip()
    assert dot(slice_figure.SLICE_NORMAL,
               slice_figure.SLICE_LABEL_ANCHOR) == 1
    assert slice_figure.SAMPLE_LABEL_ANCHOR == slice_figure.SAMPLE_HIT
    for anchor in slice_figure.RAY_LABEL_ANCHORS:
        assert any(
            anchor[0] * ray[1] - anchor[1] * ray[0] == 0
            for ray in slice_figure.EXTREME_RAYS
        )

    lesson = (TOPIC / "lesson.md").read_text()
    for phrase in (
            "corners, (0, 5), (2, 1) and",
            "(4, 4) = 5/6·(2, 1) + 1/6·(0, 5) + 7/3·(1, 1)",
            "208 = 5/6 · 84 + 1/6 · 100 + 7/3 · 52",
            "w = (4, 3)",
            "from (1/4, 0) to (0, 1/3)",
            "scaled by 7",
            "2n rows and 2ⁿ corners",
            "2n corners and 2ⁿ rows",
    ):
        assert phrase in lesson
    for relative in (
            "chapters/13-corners-and-escape/decompose.gif",
            "chapters/13-corners-and-escape/slice.png"):
        assert relative in lesson
        assert (TOPIC / relative).is_file()
