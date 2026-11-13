"""Exact checks for the extra row and multiple bases at one corner."""

from fractions import Fraction as Q
from pathlib import Path

from figures import fig12a_kink as kink
from figures import fig12b_glue as glue_figure
from linprog.corners import bases, is_degenerate
from linprog.lp import (LP, best_by_enumeration, dual_by_enumeration, simplex,
                        solve_square, vertices)

LATHE = (1, 2)
PRESS = (1, 1)
GLUE = (2, 3)
T_NONNEGATIVE = (-1, 0)
F_NONNEGATIVE = (0, -1)
ROWS = (LATHE, PRESS, GLUE, T_NONNEGATIVE, F_NONNEGATIVE)
RHS = (32, 20, 52, 0, 0)
OBJECTIVE = (3, 5)


def test_glue_row_is_redundant_and_the_vertex_sets_match():
    assert GLUE == tuple(LATHE[i] + PRESS[i] for i in range(2))
    assert RHS[2] == RHS[0] + RHS[1]
    without_glue = LP.build(c=OBJECTIVE, A=(LATHE, PRESS), b=(32, 20))
    with_glue = LP.build(c=OBJECTIVE, A=(LATHE, PRESS, GLUE), b=(32, 20, 52))
    assert set(vertices(without_glue)) == set(vertices(with_glue))


def test_all_ten_pair_bases_match_the_prose_table():
    expected = {
        ((0, 1), (Q(8), Q(12)), True),
        ((0, 2), (Q(8), Q(12)), True),
        ((1, 2), (Q(8), Q(12)), True),
        ((0, 3), (Q(0), Q(16)), True),
        ((1, 4), (Q(20), Q(0)), True),
        ((3, 4), (Q(0), Q(0)), True),
        ((0, 4), (Q(32), Q(0)), False),
        ((1, 3), (Q(0), Q(20)), False),
        ((2, 3), (Q(0), Q(52, 3)), False),
        ((2, 4), (Q(26), Q(0)), False),
    }
    found = tuple(bases(ROWS, RHS))
    assert {(indices, point, feasible)
            for indices, point, feasible in found} == expected
    assert len(found) == 10
    assert len({point for _, point, _ in found}) == 8
    assert sum(feasible for _, _, feasible in found) == 6
    assert sum(point == (Q(8), Q(12)) for _, point, _ in found) == 3


def test_degeneracy_belongs_to_tight_rows_not_the_region():
    without_glue = (LATHE, PRESS, T_NONNEGATIVE, F_NONNEGATIVE)
    without_glue_rhs = (32, 20, 0, 0)
    corner = (Q(8), Q(12))
    assert is_degenerate(ROWS, RHS, corner)
    assert not is_degenerate(without_glue, without_glue_rhs, corner)
    for point in ((Q(0), Q(16)), (Q(20), Q(0)), (Q(0), Q(0))):
        assert not is_degenerate(ROWS, RHS, point)
    assert not is_degenerate(ROWS, RHS, (Q(32), Q(0)))


def _fair_prices(y):
    return (
        all(price >= 0 for price in y)
        and y[0] + y[1] + 2 * y[2] >= 3
        and 2 * y[0] + y[1] + 3 * y[2] >= 5
    )


DUAL_FACE_A = (
    (-1, -1, -2),
    (-2, -1, -3),
    (32, 20, 52),
    (-32, -20, -52),
)
DUAL_FACE_B = (-3, -5, 84, -84)


def test_optimal_price_segment_and_prices_from_each_basis():
    face = LP.build(c=(0, 0, 0), A=DUAL_FACE_A, b=DUAL_FACE_B)
    endpoints = {
        (Q(2), Q(1), Q(0)),
        (Q(1), Q(0), Q(1)),
    }
    assert set(vertices(face)) == endpoints

    toward_lathe = LP.build(c=(1, 0, 0), A=DUAL_FACE_A, b=DUAL_FACE_B)
    toward_glue = LP.build(c=(0, 0, 1), A=DUAL_FACE_A, b=DUAL_FACE_B)
    assert best_by_enumeration(toward_lathe)[0] == (Q(2), Q(1), Q(0))
    assert best_by_enumeration(toward_glue)[0] == (Q(1), Q(0), Q(1))

    for step in range(11):
        s = Q(step, 10)
        prices = (2 - s, 1 - s, s)
        assert _fair_prices(prices)
        assert 32 * prices[0] + 20 * prices[1] + 52 * prices[2] == 84

    basis_prices = []
    for selected in ((0, 1), (0, 2), (1, 2)):
        matrix = tuple(
            tuple(ROWS[index][column] for index in selected)
            for column in range(2)
        )
        multipliers = solve_square(matrix, OBJECTIVE)
        prices = [Q(0), Q(0), Q(0)]
        for index, price in zip(selected, multipliers):
            prices[index] = price
        basis_prices.append(tuple(prices))
    assert tuple(basis_prices) == (
        (Q(2), Q(1), Q(0)),
        (Q(1), Q(0), Q(1)),
        (Q(0), Q(-1), Q(2)),
    )
    assert all(_fair_prices(prices) for prices in basis_prices[:2])
    assert not _fair_prices(basis_prices[2])


def _value_and_plan(lathe_stock, glue_stock=52):
    lp = kink.chapter_lp(lathe_stock=lathe_stock, glue_stock=glue_stock)
    enumerated_point, enumerated_value = best_by_enumeration(lp)
    walked = simplex(lp, rule="bland")
    assert walked.value == enumerated_value
    return enumerated_point, enumerated_value


def test_value_curve_breakpoints_and_chapter_numbers():
    assert _value_and_plan(31) == ((Q(9), Q(11)), Q(82))
    assert _value_and_plan(32) == ((Q(8), Q(12)), Q(84))
    assert _value_and_plan(33) == ((Q(5), Q(14)), Q(85))
    assert kink.BREAKPOINTS == (Q(20), Q(32), Q(104, 3))
    assert kink.TANGENT_SLOPES == (Q(2), Q(1))

    curve = kink.value_curve()
    slopes = tuple((curve[index + 1][1] - curve[index][1])
                   / kink.GRID_STEP for index in range(len(curve) - 1))
    assert all(slope == 3 for slope in slopes[:60])
    assert all(slope == 2 for slope in slopes[60:96])
    assert all(slope == 1 for slope in slopes[96:104])
    assert all(slope == 0 for slope in slopes[104:])
    assert kink.value_at(Q(104, 3))[1] == Q(260, 3)
    assert kink.value_at(44, include_glue=False)[1] == 100


def test_one_sided_price_bound_for_every_sampled_optimal_price():
    for step in range(9):
        s = Q(step, 8)
        lathe_price = 2 - s
        for delta_step in range(-20, 21):
            delta = Q(delta_step, 2)
            value = best_by_enumeration(
                kink.chapter_lp(lathe_stock=32 + delta)
            )[1]
            assert value <= 84 + delta * lathe_price


def test_glue_perturbation_splits_the_corner_and_changes_the_prices():
    for delta in (Q(1, 4), Q(1), Q(2), Q(3), Q(15, 4)):
        stock = 52 - delta
        lp = kink.chapter_lp(glue_stock=stock)
        first = (Q(8) - 2 * delta, Q(12) + delta)
        second = (Q(8) + delta, Q(12) - delta)
        assert lp.feasible(first) and lp.feasible(second)
        assert first in vertices(lp) and second in vertices(lp)
        assert lp.value(first) == 84 - delta
        assert lp.value(second) == 84 - 2 * delta
        assert not is_degenerate(ROWS, (32, 20, stock, 0, 0), first)
        assert not is_degenerate(ROWS, (32, 20, stock, 0, 0), second)
        assert dual_by_enumeration(lp) == ((Q(1), Q(0), Q(1)), 84 - delta)

    for stock in (Q(53), Q(56)):
        lp = kink.chapter_lp(glue_stock=stock)
        assert best_by_enumeration(lp)[1] == 84
        assert dual_by_enumeration(lp) == ((Q(2), Q(1), Q(0)), 84)


def test_figure_label_anchors_and_every_glue_frame_subtitle():
    assert kink.BREAKPOINTS == (Q(20), Q(32), Q(104, 3))
    for stock, value in kink.BEND_LABEL_ANCHORS:
        assert kink.value_at(stock)[1] == value
    assert kink.PRICE_SEGMENT_ANCHOR == (Q(32), Q(84))
    assert kink.TANGENT_SLOPES == (Q(2), Q(1))
    for index, (stock, value) in enumerate(kink.TANGENT_LABEL_ANCHORS):
        slope = kink.TANGENT_SLOPES[index]
        assert value == kink.VALUE_AT_32 + slope * (stock - 32)
    for (stock, value), include_glue in zip(
            kink.CURVE_LABEL_ANCHORS, (True, False)):
        assert kink.value_at(stock, include_glue=include_glue)[1] == value

    assert glue_figure.TITLE.strip()
    assert tuple(glue_figure.frame_stock(i)
                 for i in glue_figure.HOLD_INDICES) == (
                     Q(56), Q(52), Q(50))
    assert glue_figure.changed_corner_anchors(52) == ((Q(8), Q(12)),)
    assert glue_figure.changed_corner_anchors(50) == (
        (Q(4), Q(14)), (Q(10), Q(10)))
    for stock in (Q(56), Q(52), Q(51), Q(50)):
        lathe_anchor, press_anchor, glue_anchor = \
            glue_figure.wall_label_anchors(stock)
        assert lathe_anchor[0] + 2 * lathe_anchor[1] == 32
        assert sum(press_anchor) == 20
        assert 2 * glue_anchor[0] + 3 * glue_anchor[1] == stock
        for point in glue_figure.changed_corner_anchors(stock):
            assert point in vertices(kink.chapter_lp(glue_stock=stock))
    assert all(glue_figure.subtitle_for_frame(index).strip()
               for index in range(glue_figure.TOTAL_FRAMES))


def test_chapter_twelve_prose_numbers_and_figure_files():
    root = Path(__file__).resolve().parents[1]
    text = (root / "lesson.md").read_text()
    flat = " ".join(text.split())
    assert "2t + 3f ≤ 52" in flat
    assert "(1, 2) + (1, 1) = (2, 3)" in flat
    assert "32 + 20 = 52" in flat
    assert "C(5, 2) = 10" in flat
    assert "There are four corners but six feasible bases" in flat
    assert "(9, 11), worth 82" in flat
    assert "(5, 14), worth 85" in flat
    assert "slope 2 on the left and slope 1 on the right" in flat
    assert "(4, 14), worth 82" in flat
    assert "two corners (4, 14) worth 82 and (10, 10) worth 80" in flat

    images = (
        "chapters/12-degeneracy/kink.png",
        "chapters/12-degeneracy/glue.gif",
    )
    for relative in images:
        assert relative in text
        assert (root / relative).is_file()
