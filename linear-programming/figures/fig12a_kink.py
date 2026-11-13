"""The marginal value changes when the glue wall starts to bind."""

from fractions import Fraction as Q
from functools import lru_cache

from illuminate.draw import (PRICE, SURFACE, TEXT, TEXT_DIM, chapter_dir,
                             figure, save, style)
from linprog.lp import LP, best_by_enumeration

OUT = chapter_dir("12-degeneracy")
OBJECTIVE = (Q(3), Q(5))
LATHE_ROW = (Q(1), Q(2))
PRESS_ROW = (Q(1), Q(1))
GLUE_ROW = (Q(2), Q(3))
PRESS_STOCK = Q(20)
GLUE_STOCK = Q(52)
LATHE_STOCK = Q(32)
GRID_STEP = Q(1, 3)
STOCKS = tuple(GRID_STEP * i for i in range(133))
TITLE = "One more hour, in which direction?"
SUBTITLE = "Press 20 and glue 52: two prices meet at lathe stock 32."


def chapter_lp(lathe_stock=LATHE_STOCK, glue_stock=GLUE_STOCK,
               include_glue=True):
    rows = [LATHE_ROW, PRESS_ROW]
    bounds = [Q(lathe_stock), PRESS_STOCK]
    if include_glue:
        rows.append(GLUE_ROW)
        bounds.append(Q(glue_stock))
    return LP.build(c=OBJECTIVE, A=rows, b=bounds)


@lru_cache(maxsize=None)
def _best(stock, include_glue):
    return best_by_enumeration(chapter_lp(
        lathe_stock=stock, include_glue=include_glue
    ))


def value_at(stock, include_glue=True):
    return _best(Q(stock), bool(include_glue))


def value_curve(include_glue=True):
    return tuple((stock, value_at(stock, include_glue)[1])
                 for stock in STOCKS)


def curve_breakpoints():
    values = value_curve()
    slopes = tuple((values[i + 1][1] - values[i][1]) / GRID_STEP
                   for i in range(len(values) - 1))
    return tuple(STOCKS[i] for i in range(1, len(slopes))
                 if slopes[i] != slopes[i - 1])


BREAKPOINTS = curve_breakpoints()
BEND_LABEL_ANCHORS = tuple(
    (stock, value_at(stock)[1]) for stock in BREAKPOINTS
)
VALUE_AT_32 = value_at(Q(32))[1]
TANGENT_SLOPES = (
    VALUE_AT_32 - value_at(Q(31))[1],
    value_at(Q(33))[1] - VALUE_AT_32,
)
TANGENT_LABEL_ANCHORS = (
    (Q(30), VALUE_AT_32 - 2 * TANGENT_SLOPES[0]),
    (Q(34), VALUE_AT_32 + 2 * TANGENT_SLOPES[1]),
)
PRICE_SEGMENT_ANCHOR = (Q(32), VALUE_AT_32)
CURVE_LABEL_ANCHORS = (
    (Q(38), value_at(Q(38))[1]),
    (Q(38), value_at(Q(38), include_glue=False)[1]),
)


def format_number(value):
    value = Q(value)
    return (str(value.numerator) if value.denominator == 1
            else str(value))


def kink_figure():
    fig, ax = figure(8.4, 6.0)
    fig.subplots_adjust(left=0.13, right=0.97, bottom=0.16, top=0.80)
    fig.text(0.08, 0.96, TITLE, fontsize=11, color=TEXT,
             fontweight="semibold", ha="left")
    fig.text(0.08, 0.90, SUBTITLE, fontsize=9.2, color=TEXT_DIM,
             ha="left")
    style(ax, xlabel="lathe stock b₁", ylabel="best value V(b₁)")
    ax.set_xlim(0, 44)
    ax.set_ylim(0, 112)
    ax.set_xticks(range(0, 45, 4))
    ax.set_yticks(range(0, 113, 10))

    with_glue = value_curve()
    without_glue = value_curve(include_glue=False)
    ax.plot([float(stock) for stock, _ in without_glue],
            [float(value) for _, value in without_glue],
            color=PRICE, linewidth=1.35, linestyle=(0, (5, 3)),
            alpha=0.82, zorder=2)
    ax.plot([float(stock) for stock, _ in with_glue],
            [float(value) for _, value in with_glue],
            color=PRICE, linewidth=2.5, zorder=4)

    for stock, value in BEND_LABEL_ANCHORS:
        ax.plot([float(stock)], [float(value)], "o", color=PRICE,
                markeredgecolor=SURFACE, markeredgewidth=1.0,
                markersize=5.0, zorder=7)

    left, right = Q(28), Q(36)
    for slope in TANGENT_SLOPES:
        xs = (left, right)
        ys = tuple(VALUE_AT_32 + slope * (stock - 32) for stock in xs)
        ax.plot([float(stock) for stock in xs],
                [float(value) for value in ys], color=TEXT_DIM,
                linewidth=1.1, linestyle=(0, (2, 2)), zorder=3)

    for (stock, value), label, offset in zip(
            BEND_LABEL_ANCHORS,
            (f"b = {format_number(BREAKPOINTS[0])}",
             f"b = {format_number(BREAKPOINTS[1])}",
             f"b = {format_number(BREAKPOINTS[2])}"),
            ((-22, 12), (-27, -18), (8, 12))):
        ax.annotate(
            label, xy=(float(stock), float(value)), xytext=offset,
            textcoords="offset points", color=PRICE, fontsize=7.2,
            bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                      edgecolor=PRICE, linewidth=0.4),
            zorder=9,
        )

    for (anchor, slope, label, offset) in (
            (TANGENT_LABEL_ANCHORS[0], TANGENT_SLOPES[0],
             f"left slope {TANGENT_SLOPES[0]}", (-46, -25)),
            (TANGENT_LABEL_ANCHORS[1], TANGENT_SLOPES[1],
             f"right slope {TANGENT_SLOPES[1]}", (8, -25))):
        expected = VALUE_AT_32 + slope * (anchor[0] - 32)
        ax.annotate(
            label, xy=tuple(float(value) for value in anchor),
            xytext=offset, textcoords="offset points", color=TEXT_DIM,
            fontsize=7.0,
            arrowprops=dict(arrowstyle="-", color=TEXT_DIM, linewidth=0.55),
            bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                      edgecolor=TEXT_DIM, linewidth=0.4),
            zorder=10,
        )
        assert anchor[1] == expected

    ax.annotate(
        "prices (2 − s, 1 − s, s), 0 ≤ s ≤ 1",
        xy=tuple(float(value) for value in PRICE_SEGMENT_ANCHOR),
        xytext=(24, 101), textcoords="data", color=PRICE, fontsize=7.1,
        ha="left",
        arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.6),
        bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE,
                  edgecolor=PRICE, linewidth=0.45),
        zorder=10,
    )

    for anchor, label, offset in (
            (CURVE_LABEL_ANCHORS[0], "with glue, g = 52", (8, -12)),
            (CURVE_LABEL_ANCHORS[1], "without glue", (8, 8))):
        ax.annotate(
            label, xy=tuple(float(value) for value in anchor),
            xytext=offset, textcoords="offset points", color=PRICE,
            fontsize=7.1,
            arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.55),
            bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                      edgecolor=PRICE, linewidth=0.4),
            zorder=10,
        )

    save(fig, OUT / "kink.png", tight=False)


if __name__ == "__main__":
    kink_figure()
