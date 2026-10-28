"""Exact checks for the chapter 1 and 2 proof examples."""

import math
import re
import sys
from decimal import Decimal
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from linprog import mill as f
from linprog.lp import solve_square

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "lesson.md").read_text()
FLAT = " ".join(TEXT.split())
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "figures"))
import fig02g_squeeze as squeeze  # noqa: E402
from illuminate.site import decorate, renderer  # noqa: E402


def dot(a, x):
    return sum((u * v for u, v in zip(a, x)), Fraction(0))


def test_cosine_projection_and_perpendicular_remainder():
    a = f.MILL.A[0]
    x = (Fraction(6), Fraction(8))
    product = dot(a, x)
    p = tuple(product * ai / dot(a, a) for ai in a)
    remainder = tuple(xi - pi for xi, pi in zip(x, p))

    assert product == 22
    assert p == (Fraction(22, 5), Fraction(44, 5))
    assert dot(a, remainder) == 0
    assert "For x = (6, 8), a·x = 22" in FLAT
    assert "(4.4, 8.8)" in FLAT
    assert "22 ÷ √5 ≈ 9.8" in FLAT


def test_converse_of_the_right_angle_claim():
    assert dot((Fraction(2), Fraction(-1)), f.MILL.A[0]) == 0
    assert "multiples of (2, −1)" in FLAT
    assert "a·d = 0" in FLAT


def test_nearest_point_on_the_lathe_wall_is_feasible_and_minimal():
    a = f.MILL.A[0]
    x = (Fraction(6), Fraction(14))
    b = f.MILL.b[0]
    gap = dot(a, x) - b
    y_star = tuple(xi - gap * ai / dot(a, a) for xi, ai in zip(x, a))
    distance_sq = sum(((xi - yi) ** 2 for xi, yi in zip(x, y_star)), Fraction(0))

    assert gap == 2
    assert y_star == (Fraction(28, 5), Fraction(66, 5))
    assert dot(a, y_star) == b
    assert f.MILL.feasible(y_star)
    assert distance_sq == Fraction(4, 5)
    assert "(5.6, 13.2)" in FLAT
    assert "2 ÷ √5 ≈ 0.89" in FLAT

    wall_samples = []
    for i in range(1001):
        t = Fraction(32 * i, 1000)
        point = (t, (b - a[0] * t) / a[1])
        wall_samples.append(point)
        sample_distance_sq = sum(((xi - yi) ** 2
                                  for xi, yi in zip(x, point)), Fraction(0))
        assert sample_distance_sq >= distance_sq
    assert wall_samples[175] == y_star
    assert min(sum(((xi - yi) ** 2 for xi, yi in zip(x, point)), Fraction(0))
               for point in wall_samples) == distance_sq


def test_closedness_radii_are_derived_from_the_excess_and_row_norm():
    a = f.MILL.A[0]
    x = (Fraction(6), Fraction(14))
    epsilon = dot(a, x) - f.MILL.b[0]
    norm_sq = dot(a, a)
    used = dot(a, x)
    radius_times_norm = epsilon / 2
    minimum_on_small_circle = used - radius_times_norm
    touch = tuple(xi - epsilon * ai / norm_sq for xi, ai in zip(x, a))
    too_large_minimum = float(used) - float(epsilon) * math.sqrt(float(norm_sq))

    assert epsilon == 2
    assert norm_sq == 5
    assert minimum_on_small_circle == 33
    assert dot(a, touch) == f.MILL.b[0]
    assert f.MILL.feasible(touch)
    assert f"{too_large_minimum:.1f}" == "29.5"
    assert "1 ÷ √5" in FLAT
    assert "34 − 2√5 ≈ 29.5" in FLAT
    assert "touches the wall at (5.6, 13.2)" in FLAT
    assert "never falls below 33" in FLAT


def test_convex_combination_is_a_plan_with_the_quoted_resource_use():
    x = (Fraction(6), Fraction(8))
    y = (Fraction(8), Fraction(12))
    midpoint = tuple((xi + yi) / 2 for xi, yi in zip(x, y))

    assert midpoint == (7, 10)
    assert f.MILL.feasible(midpoint)
    assert f.MILL.used(0, midpoint) == 27
    assert f.MILL.used(1, midpoint) == 17
    assert "plan (7, 10)" in FLAT
    assert "27 lathe hours and 17 press hours" in FLAT


def test_corner_definition_excludes_the_midpoint_of_two_corners():
    endpoints = ((Fraction(0), Fraction(16)), (Fraction(8), Fraction(12)))
    midpoint = tuple((x + y) / 2 for x, y in zip(*endpoints))

    assert midpoint == (4, 14)
    assert all(point in f.CORNERS for point in endpoints)
    assert f.MILL.feasible(midpoint)
    assert midpoint not in f.CORNERS
    assert "(4, 14) is not a corner" in FLAT
    assert "(0, 16), and (8, 12), both plans" in FLAT


def test_crossings_table_matches_all_six_exact_wall_intersections():
    rows = [
        ("lathe", f.MILL.A[0], f.MILL.b[0]),
        ("press", f.MILL.A[1], f.MILL.b[1]),
        ("t = 0", (Fraction(-1), Fraction(0)), Fraction(0)),
        ("f = 0", (Fraction(0), Fraction(-1)), Fraction(0)),
    ]
    computed = {}
    for first, second in combinations(rows, 2):
        point = solve_square([first[1], second[1]], [first[2], second[2]])
        assert point is not None
        key = frozenset((first[0], second[0]))
        computed[key] = (point[0], point[1],
                         f.MILL.used(0, point), f.MILL.used(1, point),
                         f.MILL.feasible(point))
    assert len(computed) == 6

    section = TEXT.split("### Finding the corners", 1)[1]
    section = section.split("### A proof that checks no other corner", 1)[0]
    table = re.search(r"(?m)(^\| walls that cross.*(?:\n\|.*)+)", section)
    assert table is not None
    parsed = {}
    for line in table.group(1).splitlines()[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        pair = frozenset(name.strip() for name in cells[0].split(" and "))
        parsed[pair] = (Fraction(cells[1]), Fraction(cells[2]),
                        Fraction(cells[3]), Fraction(cells[4]),
                        cells[5].startswith("yes"))
    assert parsed == computed
    yes_points = {(row[0], row[1]) for row in parsed.values() if row[4]}
    assert yes_points == set(f.CORNERS)


def test_combinatorial_count_is_formatted_from_the_exact_binomial():
    count = math.comb(100, 50)
    decimal = Decimal(count)
    exponent = decimal.adjusted()
    mantissa = decimal.scaleb(-exponent).quantize(Decimal("0.01"))
    superscript = str(exponent).translate(str.maketrans(
        "0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻"))

    assert f"{mantissa} × 10{superscript}" in FLAT
    assert f"{mantissa} × 10²⁹" == "1.01 × 10²⁹"


def test_all_five_value_decomposition_and_profitable_swap():
    multipliers = solve_square([[1, -1], [2, 0]], f.MILL.c)
    assert multipliers == (Fraction(5, 2), Fraction(-1, 2))
    assert tuple(multipliers[0] * a + multipliers[1] * axis
                 for a, axis in zip(f.MILL.A[0], (Fraction(-1), Fraction(0)))) \
        == f.MILL.c
    move = (Fraction(2), Fraction(-1))
    gain = f.MILL.value(move)
    assert gain == 1
    assert "2.5 × (1, 2) − 0.5 × (−1, 0)" in FLAT
    assert f.money(gain) == "1,000 roubles"
    assert "1,000 roubles" in FLAT


def test_edge_slide_reaches_both_corners_without_changing_value():
    end_minus = f.BEST
    end_plus = max(f.CORNERS, key=lambda point: point[0])
    start = tuple((end_minus[i] + end_plus[i]) / 2 for i in range(2))
    direction = (Fraction(1), Fraction(-1))
    press_change = dot(f.MILL.A[1], direction)
    value_change = dot((Fraction(1), Fraction(1)), direction)
    move_to_lathe = tuple(-v for v in direction)
    rate = dot(f.MILL.A[0], move_to_lathe)
    steps_to_lathe = f.MILL.slack(0, start) / rate
    left_corner = tuple(start[i] + steps_to_lathe * move_to_lathe[i]
                        for i in range(2))
    steps_to_axis = start[1] / -direction[1]
    right_corner = tuple(start[i] + steps_to_axis * direction[i]
                         for i in range(2))

    assert start == (14, 6)
    assert press_change == value_change == 0
    assert steps_to_lathe == 6
    assert left_corner == (8, 12) and left_corner == f.BEST
    assert f.MILL.used(0, start) == 26
    assert f.MILL.used(0, left_corner) == 32
    assert dot((Fraction(1), Fraction(1)), start) == 20
    assert dot((Fraction(1), Fraction(1)), left_corner) == 20
    assert dot((Fraction(1), Fraction(1)), right_corner) == 20
    assert right_corner == (20, 0) and right_corner in f.CORNERS
    assert "press change 0, value change 0" in FLAT
    assert "lathe hours climb from 26 to 32" in FLAT
    assert "value stays at 20,000 roubles" in FLAT
    assert "to (20, 0)" in FLAT


def test_continuity_constant_is_the_squared_length_of_the_value_arrow():
    norm_sq = dot(f.MILL.c, f.MILL.c)
    assert norm_sq == 34
    assert "√34 |x − y|" in FLAT
    assert "continuous" in FLAT


def test_proof_blocks_get_their_own_class_without_changing_takeaways():
    for label in ("Theorem", "Proposition", "Lemma", "Definition", "Proof"):
        rendered = decorate(renderer.render(f"> **{label}.** text"))
        assert '<blockquote class="proof">' in rendered
        assert '<blockquote class="aside">' not in rendered

    later_paragraph = decorate(renderer.render(
        "> Ordinary first paragraph.\n>\n> **Proof.** not a proof block"))
    takeaway = decorate(renderer.render(
        "> **In one sentence.** one-line landing"))
    assert '<blockquote class="aside">' in later_paragraph
    assert '<blockquote class="proof">' not in later_paragraph
    assert '<blockquote class="takeaway">' in takeaway


def test_quartering_squeeze_constants_and_increasing_pick_indices():
    final_side = squeeze.SIDE / (2 ** squeeze.CUTS)

    assert squeeze.N == 5_000
    assert squeeze.CUTS == 5
    assert squeeze.SIDE == f.MILL.b[1] == 20
    assert final_side == Fraction(5, 8)
    assert f"{squeeze.N:,}" in FLAT
    assert (f"{squeeze.SIDE} ÷ {2 ** squeeze.CUTS} = "
            f"{float(final_side):g}") in FLAT
    assert len(squeeze.POINTS) == squeeze.N
    assert len(squeeze.PICK_INDICES) == squeeze.CUTS
    assert all(first < second for first, second in zip(
        squeeze.PICK_INDICES, squeeze.PICK_INDICES[1:]))
    assert all(squeeze.in_square(point, square) for point, square in zip(
        squeeze.PICK_POINTS, squeeze.SQUARES))
    assert squeeze.COUNTS[-1] >= 3
