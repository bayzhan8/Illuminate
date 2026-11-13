"""Gordan's alternative: a closed sum or a strict direction."""

from fractions import Fraction as Q
from pathlib import Path

from matplotlib.patches import Polygon

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             figure, save, style)

OUT = Path(__file__).resolve().parents[1] / "chapters/10-plan-or-proof"

ROWS = ((Q(1), Q(2)), (Q(1), Q(1)), (Q(-3), Q(-5)))
WEIGHTS = (Q(2), Q(1), Q(1))
DIRECTION = (Q(-1), Q(-1))


def _chain_points():
    points = [(Q(0), Q(0))]
    for weight, row in zip(WEIGHTS, ROWS):
        points.append(tuple(
            points[-1][j] + weight * row[j] for j in range(2)
        ))
    return tuple(points)


CHAIN_POINTS = _chain_points()
ROW_ORIGIN = (Q(0), Q(0))
ROW_LABEL_ANCHORS = ROWS
ROW_PANEL_XLIM = (-4, 3)
ROW_PANEL_YLIM = (-6, 3)
CHAIN_PANEL_XLIM = (-1, 4)
CHAIN_PANEL_YLIM = (-1, 6)
CHAIN_LABEL_ANCHORS = tuple(
    tuple((a + b) / 2 for a, b in zip(start, end))
    for start, end in zip(CHAIN_POINTS, CHAIN_POINTS[1:])
)
CHAIN_LABELS = tuple(f"{weight}×" for weight in WEIGHTS)
CHAIN_LABEL_OFFSETS = ((-34, 12), (-14, 18), (34, -12))
CHAIN_LABEL_ALIGNMENTS = ("right", "right", "left")
CHAIN_LINE_STYLES = ("-", "-", (0, (4, 2)))
HALF_PLANE_LABEL_ANCHOR = (Q(2), Q(3))
DIRECTION_LABEL_ANCHOR = DIRECTION
HALF_PLANE_POLYGON = (
    (Q(4), Q(-4)), (Q(4), Q(6)), (Q(-4), Q(6)), (Q(-4), Q(4))
)


def dot(a, b):
    return sum((x * y for x, y in zip(a, b)), Q(0))


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def _fmt(value):
    value = Q(value)
    return str(value.numerator) if value.denominator == 1 else str(value)


def _row_label(index, row):
    coordinates = ", ".join(
        f"−{_fmt(abs(value))}" if value < 0 else _fmt(value)
        for value in row
    )
    return f"r{index + 1} = ({coordinates})"


def _equation_label():
    terms = []
    for weight, row in zip(WEIGHTS, ROWS):
        coordinates = ", ".join(
            f"−{_fmt(abs(value))}" if value < 0 else _fmt(value)
            for value in row
        )
        term = f"({coordinates})" if weight == 1 else f"{_fmt(weight)}({coordinates})"
        terms.append(term)
    total = tuple(sum((weight * row[j] for weight, row
                       in zip(WEIGHTS, ROWS)), Q(0))
                  for j in range(2))
    result = ", ".join(_fmt(value) for value in total)
    return " + ".join(terms) + f" = ({result})"


def _arrow(ax, start, end, color, linewidth=1.8, linestyle="-"):
    ax.annotate(
        "", xy=tuple(map(float, end)), xytext=tuple(map(float, start)),
        arrowprops=dict(arrowstyle="-|>", color=color, linewidth=linewidth,
                        linestyle=linestyle, mutation_scale=12,
                        shrinkA=0, shrinkB=0),
        zorder=6,
    )


def _boxed_label(ax, text, anchor, offset, color, ha="left"):
    ax.annotate(
        text, xy=tuple(map(float, anchor)), xytext=offset,
        textcoords="offset points", color=color, fontsize=7.4, ha=ha,
        bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                  edgecolor=color, linewidth=0.45),
        zorder=10,
    )


def _leader_label(ax, text, anchor, offset, color, ha):
    ax.annotate(
        text, xy=tuple(map(float, anchor)), xytext=offset,
        textcoords="offset points", color=color, fontsize=7.4, ha=ha,
        va="center",
        bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                  edgecolor=color, linewidth=0.45),
        arrowprops=dict(arrowstyle="-", color=color, linewidth=0.75,
                        shrinkA=2, shrinkB=1),
        zorder=10,
    )


def _axes(ax, xlabel, ylabel, xlim, ylim, xticks, yticks):
    style(ax, xlabel=xlabel, ylabel=ylabel)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.axhline(0, color=HAIRLINE, linewidth=0.8, zorder=0)
    ax.axvline(0, color=HAIRLINE, linewidth=0.8, zorder=0)


def _row_panel(ax):
    _axes(ax, "first coordinate", "second coordinate",
          ROW_PANEL_XLIM, ROW_PANEL_YLIM, (-4, -2, 0, 2),
          (-6, -4, -2, 0, 2))
    for row, anchor, label, offset in zip(
            ROWS, ROW_LABEL_ANCHORS,
            (_row_label(i, row) for i, row in enumerate(ROWS)),
            ((8, 7), (8, -12), (8, -12))):
        _arrow(ax, ROW_ORIGIN, anchor, TEXT_DIM, linewidth=1.7)
        _boxed_label(ax, label, anchor, offset, TEXT_DIM)
    ax.plot([0], [0], "o",
            color=TEXT_DIM, markersize=3.8, markeredgecolor=SURFACE,
            markeredgewidth=0.7, zorder=8)


def _chain_panel(ax):
    _axes(ax, "first coordinate", "second coordinate",
          CHAIN_PANEL_XLIM, CHAIN_PANEL_YLIM,
          (-1, 0, 1, 2, 3, 4), (-1, 0, 1, 2, 3, 4, 5, 6))
    for (start, end), label, anchor, offset, align, linestyle in zip(
            zip(CHAIN_POINTS, CHAIN_POINTS[1:]),
            CHAIN_LABELS,
            CHAIN_LABEL_ANCHORS,
            CHAIN_LABEL_OFFSETS,
            CHAIN_LABEL_ALIGNMENTS,
            CHAIN_LINE_STYLES):
        _arrow(ax, start, end, PRICE, linewidth=2.2, linestyle=linestyle)
        _leader_label(ax, label, anchor, offset, PRICE, ha=align)

    for point in CHAIN_POINTS[:-1]:
        ax.plot([float(point[0])], [float(point[1])], "o",
                color=PRICE, markersize=4.7, markeredgecolor=SURFACE,
                markeredgewidth=0.7, zorder=8)


def _right_panel(ax):
    _axes(ax, "row coordinate 1", "row coordinate 2",
          (-4.4, 4.2), (-5.2, 6.7), (-4, -2, 0, 2, 4), (-4, -2, 0, 2, 4, 6))

    halfplane = [(float(x), float(y)) for x, y in HALF_PLANE_POLYGON]
    ax.add_patch(Polygon(halfplane, closed=True, facecolor=PLAN, alpha=0.12,
                        edgecolor="none", zorder=1))
    ax.plot([-4, 4], [4, -4], color=TEXT_DIM, linewidth=1.1,
            linestyle=(0, (3, 3)), zorder=3)

    for row in ROWS[:2]:
        _arrow(ax, (Q(0), Q(0)), row, TEXT_DIM, linewidth=1.7)

    _boxed_label(ax, "open half-plane", HALF_PLANE_LABEL_ANCHOR,
                 (8, 7), PLAN)
    _arrow(ax, (Q(0), Q(0)), DIRECTION, PLAN, linewidth=2.0,
           linestyle=(0, (4, 2)))
    _boxed_label(ax, "d = (−1, −1)", DIRECTION_LABEL_ANCHOR,
                 (-8, -15), PLAN, ha="right")


def gordan_figure():
    fig, blank = figure(12, 6)
    fig.delaxes(blank)
    rows = fig.add_axes((0.04, 0.26, 0.27, 0.53))
    chain = fig.add_axes((0.33, 0.26, 0.30, 0.53))
    right = fig.add_axes((0.67, 0.26, 0.29, 0.53))
    fig.text(0.07, 0.95, "Either a strict direction or a weighted zero",
             fontsize=11, color=TEXT, fontweight="semibold", ha="left")
    fig.text(0.07, 0.89,
             "Gordan: the rows fit in an open half-plane, or nonnegative weights cancel them",
             fontsize=8.4, color=TEXT_DIM, ha="left")
    fig.text(0.05, 0.82, "(A) The three rows",
             fontsize=8.2, color=TEXT_DIM, ha="left")
    fig.text(0.34, 0.82, "(B) Multiply and add head-to-tail",
             fontsize=8.2, color=PRICE, ha="left")

    _row_panel(rows)
    _chain_panel(chain)
    _right_panel(right)
    fig.text(0.33, 0.07, _equation_label(),
             fontsize=7.2, color=PRICE, ha="center", va="top")
    right.text(0.5, -0.24,
               "without the value row, d = (−1, −1) saves both",
               transform=right.transAxes, fontsize=7.8, color=PLAN,
               ha="center", va="top")
    save(fig, OUT / "gordan.png", tight=False)


if __name__ == "__main__":
    gordan_figure()
