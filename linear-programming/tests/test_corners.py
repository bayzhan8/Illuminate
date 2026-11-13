from fractions import Fraction as Q
from itertools import product
import math
from pathlib import Path
import random

import pytest

from figures import fig11a_rank as rank_figure
from figures import fig11b_lines as line_figure
from figures import fig11c_crash as crash_figure
from linprog import mill
from linprog.corners import (basic_points, crash, is_bfs, is_direction,
                             nullspace, rank, tight)
from linprog.lp import LP, best_by_enumeration, simplex, vertices

TOPIC = Path(__file__).resolve().parents[1]
LESSON = (TOPIC / "lesson.md").read_text()
MILL_A = tuple(mill.MILL.A) + ((Q(-1), Q(0)), (Q(0), Q(-1)))
MILL_B = tuple(mill.MILL.b) + (Q(0), Q(0))
BUYER_A = crash_figure.BUYER
BUYER_B = crash_figure.BUYER_RHS
BUYER_C = crash_figure.OBJECTIVE


def dot(a, x):
    return sum((u * v for u, v in zip(a, x)), Q(0))


def midpoint_vertices(A, b, x, upper):
    n = len(x)
    rows, rhs = [], []
    for row, bound in zip(A, b):
        slack = bound - dot(row, x)
        rows.extend((tuple(row) + tuple(-v for v in row),
                     tuple(-v for v in row) + tuple(row)))
        rhs.extend((slack, slack))
    for j in range(n):
        row = [Q(0)] * (2 * n)
        row[j] = row[n + j] = Q(1)
        rows.append(tuple(row))
        rhs.append(Q(upper[j]))
    lp = LP.build(c=(Q(0),) * (2 * n), A=rows, b=rhs)
    return {
        tuple(point[j] - point[n + j] for j in range(n))
        for point in vertices(lp)
    }


def test_mill_basic_points_match_vertices():
    points = basic_points(MILL_A, MILL_B)
    assert len(points) == 6
    feasible = {point for point, ok in points if ok}
    assert len(feasible) == 4
    assert feasible == {(Q(0), Q(0)), (Q(20), Q(0)),
                        (Q(0), Q(16)), (Q(8), Q(12))}
    assert {point for point, ok in points if not ok} == {
        (Q(32), Q(0)), (Q(0), Q(20))
    }
    assert feasible == set(vertices(mill.MILL))
    assert all(is_bfs(MILL_A, MILL_B, point) == ok for point, ok in points)


def test_rank_nullspace_and_epsilon_examples():
    corner, edge, interior = rank_figure.RANK_POINTS
    expected = ((corner, 2), (edge, 1), (interior, 0))
    for point, want in expected:
        indices = tight(MILL_A, MILL_B, point)
        rows = [MILL_A[i] for i in indices]
        assert rank(rows) == want
        assert len(nullspace(rows, 2)) == 2 - want
        assert all(dot(row, vector) == 0
                   for row in rows for vector in nullspace(rows, 2))
    assert nullspace((), 2) == ((Q(1), Q(0)), (Q(0), Q(1)))
    assert dot((1, 2), (2, -1)) == 0
    assert rank_figure.EDGE_EPSILON == 2
    assert set(rank_figure.EDGE_ENDPOINTS) == {(Q(8), Q(12)), (Q(0), Q(16))}
    assert all(all(dot(row, point) <= bound
                   for row, bound in zip(MILL_A, MILL_B))
               for point in rank_figure.EDGE_ENDPOINTS)
    assert tight(MILL_A, MILL_B, corner) == (0, 1)
    assert tight(MILL_A, MILL_B, edge) == (0,)
    assert tight(MILL_A, MILL_B, interior) == ()


def test_random_rank_nullity():
    rng = random.Random(1101)
    for _ in range(200):
        n = rng.randint(1, 5)
        rows = tuple(tuple(Q(rng.randint(-3, 3)) for _ in range(n))
                     for _ in range(rng.randint(1, 7)))
        r = rank(rows)
        basis = nullspace(rows)
        assert len(basis) == n - r
        assert rank(basis) == len(basis)
        assert all(dot(row, vector) == 0
                   for row in rows for vector in basis)


def test_random_polytope_bfs_midpoint_characterization():
    rng = random.Random(1102)
    for _ in range(32):
        upper = (Q(rng.randint(2, 5)), Q(rng.randint(2, 5)))
        rows, rhs = [], []
        for j in range(2):
            e = tuple(Q(int(i == j)) for i in range(2))
            rows.extend((tuple(-v for v in e), e))
            rhs.extend((Q(0), upper[j]))
        center = tuple(value / 2 for value in upper)
        for _ in range(rng.randint(0, 2)):
            row = tuple(Q(rng.randint(-2, 2)) for _ in range(2))
            if not any(row):
                row = (Q(1), Q(0))
            rows.append(row)
            rhs.append(dot(row, center) + rng.randint(1, 3))
        A, b = tuple(rows), tuple(rhs)
        basics = basic_points(A, b)
        feasible = [point for point, ok in basics if ok]
        assert feasible
        lp = LP.build(c=(0, 0), A=A, b=b)
        assert set(feasible) == set(vertices(lp))
        for point in feasible:
            assert is_bfs(A, b, point)
            assert midpoint_vertices(A, b, point, upper) == {(Q(0), Q(0))}
        assert not is_bfs(A, b, center)
        basis = nullspace([A[i] for i in tight(A, b, center)], 2)
        direction = basis[0]
        epsilon = min(
            (bound - dot(row, center)) / abs(dot(row, direction))
            for row, bound in zip(A, b) if dot(row, direction) != 0
        )
        ends = [tuple(center[j] + sign * epsilon * direction[j]
                      for j in range(2)) for sign in (1, -1)]
        assert ends[0] != ends[1]
        assert tuple((ends[0][j] + ends[1][j]) / 2 for j in range(2)) == center
        assert all(all(dot(row, end) <= bound for row, bound in zip(A, b))
                   for end in ends)


def picker(directions):
    chosen = iter(directions)
    return lambda basis, c: next(chosen)


def test_crash_paths_and_strip():
    path, status = crash(BUYER_A, BUYER_B, BUYER_C, (4, 4),
                         choose=picker(((-1, -1), (1, -2))))
    assert status == "bfs"
    assert [(p, r, v) for p, _, r, v in path] == [
        ((Q(4), Q(4)), 0, Q(208)),
        ((Q(5, 3), Q(5, 3)), 1, Q(260, 3)),
        ((Q(2), Q(1)), 2, Q(84)),
    ]
    assert path[1][1] == (1,)
    alt, status = crash(BUYER_A, BUYER_B, BUYER_C, (4, 4),
                        choose=picker(((0, -1), (-1, 0))))
    assert status == "bfs"
    assert alt[-1][0] == (Q(3), Q(0)) and alt[-1][3] == 96

    strip_A, strip_b = ((1, 1), (-1, -1)), (20, -12)
    strip_path, status = crash(strip_A, strip_b, (1, 1), (16, 0))
    assert status == "line"
    assert not basic_points(strip_A, strip_b)
    assert dot((1, 1), (20, 0)) == 20
    assert dot(strip_A[0], (20, 0)) == strip_b[0] == 20
    assert all(dot(row, (20, 0)) <= bound
               for row, bound in zip(strip_A, strip_b))


def test_random_pointed_fundamental_theorem_and_unbounded_case():
    rng = random.Random(1103)
    for _ in range(40):
        n = rng.randint(2, 3)
        upper = tuple(Q(rng.randint(2, 5)) for _ in range(n))
        rows, rhs = [], []
        for j in range(n):
            e = tuple(Q(int(i == j)) for i in range(n))
            rows.extend((tuple(-v for v in e), e))
            rhs.extend((Q(0), upper[j]))
        start = tuple(v / 2 for v in upper)
        for _ in range(rng.randint(0, 2)):
            row = tuple(Q(rng.randint(0, 3)) for _ in range(n))
            rows.append(row)
            rhs.append(dot(row, start) + rng.randint(1, 4))
        A, b = tuple(rows), tuple(rhs)
        c = tuple(Q(rng.randint(-4, 5)) for _ in range(n))
        path, status = crash(A, b, c, start)
        assert status == "bfs" and path[-1][3] <= path[0][3]
        best_bfs = min(dot(c, point) for point, ok in basic_points(A, b) if ok)
        lp = LP.build(c=tuple(-v for v in c), A=A, b=b)
        _, enumerated = best_by_enumeration(lp)
        walked = simplex(lp, rule="bland")
        assert best_bfs == -enumerated == -walked.value
    A, b, c = ((-1, 0), (0, -1)), (0, 0), (-1, -2)
    assert crash(A, b, c, (1, 1))[1] == "unbounded"
    with pytest.raises(ValueError, match="unbounded"):
        simplex(LP.build(c=(1, 2), A=A, b=b), rule="bland")


def test_buyer_directions_are_exactly_nonnegative():
    for pair in product(range(-2, 3), repeat=2):
        direction = tuple(map(Q, pair))
        assert is_direction(BUYER_A, direction) == all(v >= 0 for v in direction)


def test_prose_figures_and_label_anchors():
    assert "## 11 · Corners by algebra" in LESSON
    for phrase in ("(8, 12)", "(4, 14)", "(4, 6)", "(5/3, 5/3)",
                   "260/3", "(3, 0)", "12 ≤ t + f ≤ 20"):
        assert phrase in LESSON
    chapter = TOPIC / "chapters/11-corners-by-algebra"
    for name in ("rank.png", "lines.png", "crash.gif"):
        assert (chapter / name).is_file()

    for point, anchor in zip(rank_figure.RANK_POINTS,
                             rank_figure.POINT_LABEL_ANCHORS):
        assert point == anchor
    assert rank_figure.BREAKING_LABEL_ANCHORS == rank_figure.BREAKING_ENDS
    assert rank_figure.BREAKING_LABEL_LEADERS == (True, True)
    for (direction, label), endpoint in zip(
            rank_figure.BREAKING_MOVES, rank_figure.BREAKING_ENDS):
        distance = math.dist(tuple(map(float, rank_figure.CORNER)), endpoint)
        assert math.isclose(distance, rank_figure.BREAKING_LENGTH)
        if label == "breaks press":
            assert math.isclose(endpoint[0] + 2 * endpoint[1], 32)
            assert endpoint[0] + endpoint[1] > 20
            assert direction == (Q(2), Q(-1))
        else:
            assert math.isclose(endpoint[0] + endpoint[1], 20)
            assert endpoint[0] + 2 * endpoint[1] > 32
            assert direction == (Q(-1), Q(1))
    a0, a1 = rank_figure.WALL_LABEL_ANCHORS
    assert a0[0] + 2 * a0[1] == 32
    assert a1[0] + a1[1] == 20
    assert all(x + f == level for (x, f), level in
               zip(line_figure.STRIP_WALL_LABEL_ANCHORS, (12, 20)))
    strip_anchor = tuple(line_figure.STRIP_DIRECTION_LABEL_ANCHOR[i]
                         - line_figure.STRIP_POINT[i] for i in range(2))
    assert strip_anchor[0] == -strip_anchor[1]
    assert line_figure.BUYER_CORNERS == ((0, 5), (2, 1), (3, 0))
    assert line_figure.BUYER_CORNER_LABEL_ANCHORS == line_figure.BUYER_CORNERS
    assert line_figure.BUYER_CORNER_LABEL_LEADERS == (False, True, False)
    buyer_anchor = tuple(line_figure.BUYER_DIRECTION_LABEL_ANCHOR[i]
                         - line_figure.BUYER_DIRECTION_START[i] for i in range(2))
    assert buyer_anchor[0] == 0 and 0 < buyer_anchor[1] < 2
    assert crash_figure.TITLE == "Crash until the rows pin the point"
    assert crash_figure.SUBTITLES == (
        "no tight rows: any direction is free",
        "moving along (−1, −1) until a row goes tight",
        "one tight row: slide along it, (1, −2), bill falling 8 per unit",
        "two tight rows, rank 2: a corner, bill 84",
    )
    assert crash_figure.STAGE_SUBTITLES == (
        crash_figure.SUBTITLES[0], crash_figure.SUBTITLES[1],
        crash_figure.SUBTITLES[2], crash_figure.SUBTITLES[2],
        crash_figure.SUBTITLES[3],
    )
    mid = crash_figure.STOP_LABEL_ANCHORS[1]
    arrow_end = crash_figure.MID_DIRECTION_ARROW_END
    delta = tuple(arrow_end[i] - mid[i] for i in range(2))
    assert delta == tuple(Q(1, 2) * value
                          for value in crash_figure.DIRECTIONS[1])
    assert dot(delta, delta) == Q(5, 4)
    assert 2 * arrow_end[0] + arrow_end[1] == 5
    assert sum(arrow_end) < 3
    assert crash_figure.CRASH_STATUS == "bfs"
    assert crash_figure.STOP_LABEL_ANCHORS == tuple(
        point for point, _, _, _ in crash_figure.CRASH_PATH)
    assert sum(crash_figure.WALL_LABEL_ANCHORS[0]) == 3
    assert 2 * crash_figure.WALL_LABEL_ANCHORS[1][0] + \
        crash_figure.WALL_LABEL_ANCHORS[1][1] == 5
    assert all(dot(BUYER_C, point) == value
               for (point, _, _, value) in crash_figure.CRASH_PATH)
