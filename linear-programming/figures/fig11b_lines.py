"""A line gives no corner; the buyer's price region is pointed."""

import math
from pathlib import Path

from matplotlib.patches import Polygon

from illuminate.draw import (PLAN, PRICE, SURFACE, TEXT, TEXT_DIM, figure, save,
                             style)
from linprog.corners import basic_points
from linprog.lp import LP, vertices

OUT = Path(__file__).resolve().parents[1] / "chapters/11-corners-by-algebra"
STRIP_A = ((1, 1), (-1, -1))
STRIP_B = (20, -12)
STRIP_DIRECTION = (1, -1)
STRIP_POINT = (12, 4)
STRIP_WALL_LABEL_ANCHORS = ((0, 12), (0, 20))
STRIP_DIRECTION_LABEL_ANCHOR = (14, 2)
BUYER_A = ((-1, -1), (-2, -1), (-1, 0), (0, -1))
BUYER_B = (-3, -5, 0, 0)
BUYER_CORNERS = tuple(sorted(
    point for point, feasible in basic_points(BUYER_A, BUYER_B) if feasible
))
BUYER_CORNER_LABEL_ANCHORS = BUYER_CORNERS
BUYER_DIRECTION_START = (2, 1)
BUYER_DIRECTION_VECTORS = ((2, 0), (0, 2))
BUYER_DIRECTION_LABEL_ANCHOR = (2, 2)
BUYER_WINDOW = (8, 8)


def _polygon(lp):
    points = [(float(x), float(y)) for x, y in vertices(lp)]
    center = (sum(x for x, _ in points) / len(points),
              sum(y for _, y in points) / len(points))
    return sorted(points,
                  key=lambda p: math.atan2(p[1] - center[1], p[0] - center[0]))


def _strip(ax):
    style(ax, xlabel="t", ylabel="f")
    ax.set_xlim(-8, 28)
    ax.set_ylim(-8, 28)
    ax.set_aspect("equal", adjustable="box")
    poly = ((-8, 20), (-8, 28), (28, -8), (20, -8))
    ax.add_patch(Polygon(poly, closed=True, facecolor=PLAN, alpha=0.12,
                         edgecolor="none", zorder=1))
    for level, anchor, label, offset in (
            (12, STRIP_WALL_LABEL_ANCHORS[0], "t + f = 12", (8, -12)),
            (20, STRIP_WALL_LABEL_ANCHORS[1], "t + f = 20", (8, 8))):
        ax.plot([-8, 28], [level + 8, level - 28], color=TEXT_DIM,
                linewidth=1.15, zorder=2)
        ax.annotate(label, xy=anchor, xytext=offset, textcoords="offset points",
                    color=TEXT_DIM, fontsize=7.5,
                    bbox=dict(boxstyle="square,pad=0.13", facecolor=SURFACE,
                              edgecolor=TEXT_DIM, linewidth=0.4), zorder=6)
    ax.plot([STRIP_POINT[0]], [STRIP_POINT[1]], "o", color=PLAN,
            markersize=6, markeredgecolor=SURFACE, markeredgewidth=1.1, zorder=7)
    for sign in (1, -1):
        end = tuple(STRIP_POINT[i] + sign * 4 * STRIP_DIRECTION[i]
                    for i in range(2))
        ax.annotate("", xy=end, xytext=STRIP_POINT,
                    arrowprops=dict(arrowstyle="-|>", color=PLAN, linewidth=1.8,
                                    mutation_scale=12), zorder=8)
    ax.annotate(
        "±(1, −1)", xy=STRIP_DIRECTION_LABEL_ANCHOR, xytext=(7, 7),
        textcoords="offset points", color=PLAN, fontsize=7.3,
        bbox=dict(boxstyle="square,pad=0.13", facecolor=SURFACE,
                  edgecolor=PLAN, linewidth=0.4), zorder=9)
    ax.text(0, -6.6, "a line: no corner anywhere", color=PLAN, fontsize=8,
            bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                      edgecolor="none"))


def _buyer(ax):
    style(ax, xlabel="3-ply price y₁", ylabel="5-ply price y₂")
    ax.set_xlim(-0.8, 8)
    ax.set_ylim(-0.8, 8)
    ax.set_aspect("equal", adjustable="box")
    plot_A = BUYER_A + ((1, 0), (0, 1))
    plot_b = BUYER_B + BUYER_WINDOW
    plot_lp = LP.build(c=(0, 0), A=plot_A, b=plot_b)
    polygon = _polygon(plot_lp)
    ax.add_patch(Polygon(polygon, closed=True, facecolor=PRICE, alpha=0.13,
                         edgecolor=PRICE, linewidth=1.2, zorder=1))
    x = [0, 8]
    ax.plot(x, [3 - v for v in x], color=TEXT_DIM, linewidth=1.1, zorder=3)
    ax.plot(x, [5 - 2 * v for v in x], color=TEXT_DIM, linewidth=1.1, zorder=3)
    ax.axhline(0, color=TEXT_DIM, linewidth=1.0, zorder=2)
    ax.axvline(0, color=TEXT_DIM, linewidth=1.0, zorder=2)
    offsets = ((8, 8), (-48, -12), (8, -13))
    for point, offset in zip(BUYER_CORNERS, offsets):
        ax.plot([point[0]], [point[1]], "o", color=PRICE, markersize=5.8,
                markeredgecolor=SURFACE, markeredgewidth=1.1, zorder=7)
        ax.annotate(f"({point[0]}, {point[1]})", xy=point, xytext=offset,
                    textcoords="offset points", color=PRICE, fontsize=7.3,
                    bbox=dict(boxstyle="square,pad=0.13", facecolor=SURFACE,
                              edgecolor=PRICE, linewidth=0.4), zorder=8)
    for vector in BUYER_DIRECTION_VECTORS:
        end = tuple(BUYER_DIRECTION_START[i] + vector[i] for i in range(2))
        ax.annotate("", xy=end, xytext=BUYER_DIRECTION_START,
                    arrowprops=dict(arrowstyle="-|>", color=PRICE, linewidth=1.7,
                                    mutation_scale=12), zorder=8)
    ax.annotate(
        "d ≥ 0", xy=BUYER_DIRECTION_LABEL_ANCHOR, xytext=(16, 1),
        textcoords="offset points", color=PRICE, fontsize=7.3,
        arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.8),
        bbox=dict(boxstyle="square,pad=0.13", facecolor=SURFACE,
                  edgecolor=PRICE, linewidth=0.4), zorder=9)


def lines_figure():
    fig, blank = figure(12.5, 5.8)
    fig.delaxes(blank)
    left = fig.add_axes((0.07, 0.22, 0.38, 0.61))
    right = fig.add_axes((0.56, 0.22, 0.38, 0.61))
    fig.text(0.07, 0.95, "Lines can remove every corner",
             fontsize=11, color=TEXT, fontweight="semibold", ha="left")
    fig.text(0.07, 0.89,
             "A direction that works both ways makes a line; buyer prices only rise",
             fontsize=8.5, color=TEXT_DIM, ha="left")
    fig.text(0.09, 0.84, "(A) The strip", fontsize=8, color=PLAN, ha="left")
    fig.text(0.58, 0.84, "(B) The buyer's region", fontsize=8, color=PRICE,
             ha="left")
    _strip(left)
    _buyer(right)
    save(fig, OUT / "lines.png", tight=False)


if __name__ == "__main__":
    lines_figure()
