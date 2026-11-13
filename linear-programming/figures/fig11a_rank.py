"""Tight rows leave exactly the directions that rank has not used."""

from fractions import Fraction as Q
import math
from pathlib import Path

from matplotlib.patches import Circle, Polygon

from illuminate.draw import (PLAN, SURFACE, TEXT, TEXT_DIM, WARN, figure, save,
                             style)
from linprog import mill
from linprog.corners import rank, tight
from linprog.lp import vertices

OUT = Path(__file__).resolve().parents[1] / "chapters/11-corners-by-algebra"
MILL_A = tuple(mill.MILL.A) + ((Q(-1), Q(0)), (Q(0), Q(-1)))
MILL_B = tuple(mill.MILL.b) + (Q(0), Q(0))
MILL_VERTICES = tuple(vertices(mill.MILL))
CORNER = mill.BEST
OTHER_EDGE_END = next(point for point in MILL_VERTICES
                      if point[0] == 0 and point[1] > 0)
EDGE_POINT = tuple((CORNER[i] + OTHER_EDGE_END[i]) / 2 for i in range(2))
INTERIOR_POINT = tuple(CORNER[i] / 2 for i in range(2))
RANK_POINTS = (CORNER, EDGE_POINT, INTERIOR_POINT)
POINT_LABEL_ANCHORS = RANK_POINTS
WALL_LABEL_ANCHORS = ((Q(0), mill.MILL.b[0] / 2),
                      (mill.MILL.b[1], Q(0)))
EDGE_DIRECTION = (Q(2), Q(-1))
EDGE_EPSILON = min(
    (bound - sum((a * x for a, x in zip(row, EDGE_POINT)), Q(0)))
    / abs(sum((a * d for a, d in zip(row, EDGE_DIRECTION)), Q(0)))
    for row, bound in zip(MILL_A, MILL_B)
    if sum((a * d for a, d in zip(row, EDGE_DIRECTION)), Q(0)) != 0
)
EDGE_ENDPOINTS = tuple(
    tuple(EDGE_POINT[i] + sign * EDGE_EPSILON * EDGE_DIRECTION[i]
          for i in range(2))
    for sign in (1, -1)
)
INTERIOR_RADIUS = min(
    (bound - sum((a * x for a, x in zip(row, INTERIOR_POINT)), Q(0)))
    / sum((abs(a) for a in row), Q(0))
    for row, bound in zip(MILL_A, MILL_B)
    if any(row)
) / 4
BREAKING_MOVES = (
    ((Q(2), Q(-1)), "breaks press"),
    ((Q(-1), Q(1)), "breaks lathe"),
)
BREAKING_LENGTH = 2.5
BREAKING_ENDS = tuple(
    tuple(float(CORNER[i]) + BREAKING_LENGTH * float(direction[i])
          / math.hypot(*(float(value) for value in direction))
          for i in range(2))
    for direction, _ in BREAKING_MOVES
)
BREAKING_LABEL_ANCHORS = BREAKING_ENDS
BREAKING_LABEL_LEADERS = (True, True)


def _fmt(point):
    return ", ".join(str(value.numerator) if value.denominator == 1
                     else str(value) for value in point)


def _polygon_points():
    points = [(float(x), float(y)) for x, y in MILL_VERTICES]
    center = (sum(x for x, _ in points) / len(points),
              sum(y for _, y in points) / len(points))
    return sorted(points,
                  key=lambda point: math.atan2(point[1] - center[1],
                                               point[0] - center[0]))


def _base(ax, point):
    style(ax, xlabel="3-ply batches t", ylabel="5-ply batches f")
    ax.set_xlim(-1, 22)
    ax.set_ylim(-1, 20)
    ax.set_xticks((0, 4, 8, 12, 16, 20))
    ax.set_yticks((0, 4, 8, 12, 16, 20))
    ax.set_aspect("equal", adjustable="box")
    polygon = _polygon_points()
    ax.add_patch(Polygon(polygon, closed=True, facecolor=PLAN, alpha=0.12,
                         edgecolor="none", zorder=1))
    for row, bound in zip(mill.MILL.A, mill.MILL.b):
        ax.plot([0, 22], [float(bound / row[1]),
                          float((bound - 22 * row[0]) / row[1])],
                color=TEXT_DIM, linewidth=1.05, zorder=2)
    ax.axhline(0, color=TEXT_DIM, linewidth=1.0, zorder=2)
    ax.axvline(0, color=TEXT_DIM, linewidth=1.0, zorder=2)
    ax.plot([float(point[0])], [float(point[1])], "o", color=PLAN,
            markersize=7, markeredgecolor=SURFACE, markeredgewidth=1.3,
            zorder=8)
    ax.annotate(
        f"({_fmt(point)})", xy=tuple(map(float, point)),
        xytext=(8, 8), textcoords="offset points", color=PLAN, fontsize=7.7,
        bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE,
                  edgecolor=PLAN, linewidth=0.45),
        zorder=10,
    )


def _arrow(ax, start, end, color, label, offset, ha="left", leader=False):
    ax.annotate(
        "", xy=tuple(map(float, end)), xytext=tuple(map(float, start)),
        arrowprops=dict(arrowstyle="-|>", color=color, linewidth=1.7,
                        mutation_scale=11, shrinkA=0, shrinkB=0),
        zorder=7,
    )
    ax.annotate(
        label, xy=tuple(map(float, end)), xytext=offset,
        textcoords="offset points", color=color, fontsize=6.8, ha=ha,
        arrowprops=(dict(arrowstyle="-", color=color, linewidth=0.65,
                         shrinkA=2, shrinkB=3) if leader else None),
        bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                  edgecolor=color, linewidth=0.4),
        zorder=9,
    )


def rank_figure():
    fig, axes = figure(14, 5.8)
    fig.delaxes(axes)
    panels = [fig.add_axes((left, 0.25, 0.28, 0.56))
              for left in (0.04, 0.36, 0.68)]
    headings = ("(A) Two independent walls",
                "(B) One free direction",
                "(C) Every direction is free")
    for ax, title, point in zip(panels, headings, RANK_POINTS):
        _base(ax, point)
        fig.text(ax.get_position().x0, 0.85, title, fontsize=8.3,
                 color=TEXT_DIM, ha="left")

    first = panels[0]
    for (direction, label), end, offset, ha in zip(
            BREAKING_MOVES, BREAKING_ENDS,
            ((16, -20), (-16, 16)), ("left", "right")):
        _arrow(first, CORNER, end, WARN, label, offset, ha=ha, leader=True)
    for anchor, label, offset, ha in (
            (WALL_LABEL_ANCHORS[0], "lathe wall", (8, 5), "left"),
            (WALL_LABEL_ANCHORS[1], "press wall", (-8, 8), "right")):
        first.annotate(
            label, xy=tuple(map(float, anchor)), xytext=offset,
            textcoords="offset points", color=TEXT_DIM, fontsize=7,
            ha=ha, bbox=dict(boxstyle="square,pad=0.12",
                             facecolor=SURFACE, edgecolor=TEXT_DIM,
                             linewidth=0.4),
            zorder=9,
        )

    middle = panels[1]
    for endpoint, label, offset, ha in (
            (EDGE_ENDPOINTS[0], "(8, 12)", (8, 7), "left"),
            (EDGE_ENDPOINTS[1], "(0, 16)", (-8, -12), "right")):
        _arrow(middle, EDGE_POINT, endpoint, PLAN, "", offset)
        middle.plot([float(endpoint[0])], [float(endpoint[1])], "o",
                    color=PLAN, markersize=5, markeredgecolor=SURFACE,
                    markeredgewidth=0.9, zorder=8)
        middle.annotate(
            label, xy=tuple(map(float, endpoint)), xytext=offset,
            textcoords="offset points", color=PLAN, fontsize=7,
            ha=ha, bbox=dict(boxstyle="square,pad=0.12",
                             facecolor=SURFACE, edgecolor=PLAN,
                             linewidth=0.4),
            zorder=9,
        )
    middle.text(0.5, 0.08, f"epsilon = {EDGE_EPSILON}",
                transform=middle.transAxes, color=PLAN, fontsize=8,
                ha="center", bbox=dict(boxstyle="square,pad=0.12",
                                       facecolor=SURFACE, edgecolor="none"))

    interior = panels[2]
    interior.add_patch(Circle(tuple(map(float, INTERIOR_POINT)),
                              float(INTERIOR_RADIUS), facecolor=PLAN,
                              edgecolor=PLAN, alpha=0.17, linewidth=1.4,
                              zorder=5))

    captions = ("rank 2: no free direction, a corner",
                "rank 1: midpoint of (0, 16) and (8, 12)",
                "rank 0: every direction is free")
    for ax, point, caption in zip(panels, RANK_POINTS, captions):
        value = rank(mill.MILL.A[i] for i in tight(MILL_A, MILL_B, point))
        fig.text(ax.get_position().x0 + 0.14, 0.11,
                 f"({ _fmt(point)}) · rank {value}: {caption.split(': ', 1)[1]}",
                 fontsize=7.3, color=TEXT_DIM, ha="center")
    save(fig, OUT / "rank.png", tight=False)


if __name__ == "__main__":
    rank_figure()
