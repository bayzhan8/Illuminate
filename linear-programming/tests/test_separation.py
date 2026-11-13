import random
import re
from fractions import Fraction
from pathlib import Path

from figures.fig08a_closest import (CORNER, END, ORDER, START,
                                    closest_label_anchors)
from figures.fig08b_obtuse import (OUTSIDE, STAR, WALK_MIDPOINT,
                                   obtuse_label_anchors)
from figures.fig08c_no_wall import (ENDPOINTS, MIDPOINT, TRIAL_NORMALS,
                                    approach_points, dot,
                                    open_press_label_anchor,
                                    trial_wall_label_anchors,
                                    trial_wrong_endpoint)
from linprog import mill as mill
from linprog.lp import vertices
from linprog.separation import project_to_polygon, separator

Q = Fraction
POLYGON_A = mill.MILL.A + ((Q(-1), Q(0)), (Q(0), Q(-1)))
POLYGON_B = mill.MILL.b + (Q(0), Q(0))
TOPIC = Path(__file__).resolve().parents[1]


def dot_product(left, right):
    return sum((a * b for a, b in zip(left, right)), Q(0))


def grid_points():
    step = Q(1, 10)
    for i in range(201):
        for j in range(201):
            point = (step * i, step * j)
            if mill.MILL.feasible(point):
                yield point


def test_wall_feet_are_exact_and_infeasible():
    order = (Q(11), Q(16))
    press_foot = (Q(15, 2), Q(25, 2))
    lathe_foot = (Q(44, 5), Q(58, 5))

    assert dot_product(mill.MILL.A[1], press_foot) == 20
    assert dot_product(mill.MILL.A[0], press_foot) == Q(65, 2)
    assert not mill.MILL.feasible(press_foot)
    assert dot_product(mill.MILL.A[0], lathe_foot) == 32
    assert dot_product(mill.MILL.A[1], lathe_foot) == Q(102, 5)
    assert not mill.MILL.feasible(lathe_foot)
    assert order == (11, 16)


def test_projection_is_exact_and_agrees_with_a_fine_grid():
    order = (Q(11), Q(16))
    nearest, distance_squared = project_to_polygon(order, POLYGON_A,
                                                    POLYGON_B)

    assert nearest == (Q(8), Q(12))
    assert distance_squared == 25
    grid_best = min(
        sum(((a - b) ** 2 for a, b in zip(order, point)), Q(0))
        for point in grid_points()
    )
    assert grid_best == distance_squared
    assert project_to_polygon((Q(3), Q(4)), POLYGON_A,
                              POLYGON_B) == ((Q(3), Q(4)), Q(0))


def test_midpoint_separator_and_multiplier_certificate():
    order = (Q(11), Q(16))
    nearest = (Q(8), Q(12))
    pi, pi0 = separator(order, nearest)
    assert pi == (Q(-3), Q(-4))
    assert pi0 == Q(-169, 2)
    assert -dot_product(pi, order) == 97
    assert -pi0 == Q(169, 2)

    values = [3 * t + 4 * f for t, f in vertices(mill.MILL)]
    assert max(values) == 72
    lathe, press = mill.MILL.A
    assert tuple(lathe[j] + 2 * press[j] for j in range(2)) == (3, 4)
    assert mill.MILL.b[0] + 2 * mill.MILL.b[1] == 72
    assert (3, 4) == tuple(
        1 * a + 2 * b for a, b in zip((1, 2), (1, 1))
    )


def test_edge_projection_has_the_stated_wall_and_distance():
    order = (Q(14), Q(10))
    nearest, distance_squared = project_to_polygon(order, POLYGON_A,
                                                    POLYGON_B)
    pi, pi0 = separator(order, nearest)
    assert nearest == (Q(12), Q(8))
    assert distance_squared == 8
    assert pi == (Q(-2), Q(-2))
    assert pi0 == -44
    assert tuple(-value / 2 for value in pi) == (1, 1)
    assert -pi0 / 2 == 22


def test_step_two_inequality_holds_at_vertices_and_on_a_grid():
    order = (Q(11), Q(16))
    nearest = (Q(8), Q(12))

    def directional_value(point):
        return dot_product(
            tuple(a - b for a, b in zip(order, nearest)),
            tuple(a - b for a, b in zip(point, nearest)),
        )

    for point in vertices(mill.MILL):
        assert directional_value(point) == 3 * point[0] + 4 * point[1] - 72
        assert directional_value(point) <= 0
        assert (directional_value(point) == 0) == (point == nearest)
    for point in grid_points():
        assert directional_value(point) == 3 * point[0] + 4 * point[1] - 72
        assert directional_value(point) <= 0
        assert (directional_value(point) == 0) == (point == nearest)


def test_two_hundred_random_outside_points_are_strictly_separated():
    rng = random.Random(80808)
    corners = vertices(mill.MILL)
    checked = 0
    while checked < 200:
        point = (Q(rng.randint(-8, 32)), Q(rng.randint(-8, 32)))
        if mill.MILL.feasible(point):
            continue
        nearest, distance_squared = project_to_polygon(point, POLYGON_A,
                                                        POLYGON_B)
        assert distance_squared > 0
        pi, pi0 = separator(point, nearest)
        assert dot_product(pi, point) < pi0
        assert all(pi0 < dot_product(pi, corner) for corner in corners)
        checked += 1


def test_random_nonconvex_midpoint_and_nonclosed_limit_arguments():
    rng = random.Random(814)
    a, b = ENDPOINTS
    for _ in range(200):
        pi = (Q(rng.randint(-20, 20), rng.randint(1, 9)),
              Q(rng.randint(-20, 20), rng.randint(1, 9)))
        midpoint_value = dot_product(pi, MIDPOINT)
        endpoint_average = (dot_product(pi, a) + dot_product(pi, b)) / 2
        assert midpoint_value == endpoint_average
        threshold = Q(rng.randint(-20, 20), rng.randint(1, 9))
        values = (dot_product(pi, a), dot_product(pi, b))
        assert not (all(value > threshold for value in values)
                    and midpoint_value <= threshold)
        assert not (all(value < threshold for value in values)
                    and midpoint_value >= threshold)

        edge = (Q(10), Q(10))
        edge_value = dot_product(pi, edge)
        deltas = []
        for power in range(1, 7):
            epsilon = Q(1, 10 ** power)
            inside = (Q(10) - epsilon, Q(10) - epsilon)
            assert inside[0] + inside[1] < 20
            deltas.append(abs(dot_product(pi, inside) - edge_value))
        assert deltas[-1] <= deltas[0]

        gap = Q(1, 10)
        wall_value = edge_value + gap
        epsilon = gap / (2 * abs(pi[0] + pi[1]) + 1)
        just_inside = (Q(10) - epsilon, Q(10) - epsilon)
        assert dot_product(pi, just_inside) < wall_value


def test_figure_label_anchors_stay_on_their_objects():
    for probe in (START, CORNER, END):
        order_anchor, probe_anchor, wall_anchor = closest_label_anchors(probe)
        assert order_anchor == ORDER
        assert probe_anchor == probe
        pi, pi0 = separator(ORDER, CORNER)
        assert dot_product(pi, wall_anchor) == pi0

    order_anchor, star_anchor, outside_anchor, walk_anchor = (
        obtuse_label_anchors(OUTSIDE)
    )
    assert order_anchor == ORDER
    assert star_anchor == STAR
    assert outside_anchor == OUTSIDE
    assert walk_anchor == WALK_MIDPOINT
    assert not mill.MILL.feasible(OUTSIDE)
    assert not mill.MILL.feasible(WALK_MIDPOINT)
    distance_to_order = lambda point: sum(
        ((a - b) ** 2 for a, b in zip(point, ORDER)), Q(0)
    )
    assert distance_to_order(WALK_MIDPOINT) < distance_to_order(STAR)

    for normal, anchor in zip(TRIAL_NORMALS, trial_wall_label_anchors()):
        assert dot_product(normal, anchor) == dot_product(normal, MIDPOINT)
        wrong = trial_wrong_endpoint(normal)
        assert dot_product(normal, wrong) < dot_product(normal, MIDPOINT)
    press_anchor = open_press_label_anchor()
    assert dot_product(mill.MILL.A[1], press_anchor) == mill.MILL.b[1]
    assert len(approach_points()) == 3
    assert all(point[0] + point[1] < 20 for point in approach_points())


def test_chapter_numbers_and_figure_paths_match_the_code():
    lesson = (TOPIC / "lesson.md").read_text()
    flat = re.sub(r"\s+", " ", lesson)
    order = (Q(11), Q(16))
    press_foot = (Q(15, 2), Q(25, 2))
    lathe_foot = (Q(44, 5), Q(58, 5))
    nearest = project_to_polygon(order, POLYGON_A, POLYGON_B)[0]
    pi, pi0 = separator(order, nearest)
    assert mill.MILL.used(0, order) == 43
    assert mill.MILL.used(1, order) == 27

    expected = (
        "43 lathe hours and 27 press hours",
        f"({float(press_foot[0]):.1f}, {float(press_foot[1]):.1f})",
        f"{float(mill.MILL.used(0, press_foot)):.1f} lathe hours",
        f"({float(lathe_foot[0]):.1f}, {float(lathe_foot[1]):.1f})",
        f"{float(mill.MILL.used(1, lathe_foot)):.1f} press hours",
        "distance √(3² + 4²) = 5",
        f"3 × 11 + 4 × 16 = {-dot_product(pi, order)}, above {float(-pi0):.1f}",
        "at most 72",
        "3t + 4f = 1 × (t + 2f) + 2 × (t + f) ≤ 32 + 2 × 20 = 72",
        "3 × 9.5 + 4 × 14 = 84.5",
        "π = (−3, −4) and π0 = −84.5",
        "at (12, 8), the foot on the press wall, at distance 2√2",
        "t + f = 22",
        "at or below 0",
        "(20, 0) and (4, 14)",
        "(12, 7)",
        "(9.9, 9.9), (9.99, 9.99)",
    )
    for number in expected:
        assert number in flat

    for relative in (
        "chapters/08-separation/closest.gif",
        "chapters/08-separation/obtuse.gif",
        "chapters/08-separation/no_wall.png",
    ):
        assert f"({relative})" in lesson
        assert (TOPIC / relative).is_file()
