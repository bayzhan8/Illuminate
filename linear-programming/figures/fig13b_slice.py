"""Slice the buyer's recession cone to expose its extreme rays."""

from fractions import Fraction as Q
from pathlib import Path

from matplotlib.patches import Polygon

from illuminate.draw import (PRICE, SURFACE, TEXT, TEXT_DIM, chapter_dir,
                             figure, save, style)
from linprog.corners import basic_points
from linprog.representation import extreme_rays, recession_cone

if __package__:
    from .fig11c_crash import BUYER
else:
    from fig11c_crash import BUYER

OUT = chapter_dir("13-corners-and-escape")
TITLE = "A slice turns escape routes into corners"
SUBTITLE = "Normalize every nonzero direction with 4d₁ + 3d₂ = 1."
CONE_A, CONE_B = recession_cone(BUYER)
SLICE_NORMAL = tuple(
    -sum((row[index] for row in CONE_A), Q(0))
    for index in range(len(CONE_A[0]))
)
SLICE_A = CONE_A + (SLICE_NORMAL, tuple(-value for value in SLICE_NORMAL))
SLICE_B = CONE_B + (Q(1), Q(-1))
SLICE_ENDPOINTS = tuple(sorted(
    point for point, feasible in basic_points(SLICE_A, SLICE_B) if feasible
))
SLICE_X_ENDPOINT = next(point for point in SLICE_ENDPOINTS if point[1] == 0)
SLICE_Y_ENDPOINT = next(point for point in SLICE_ENDPOINTS if point[0] == 0)
EXTREME_RAYS = extreme_rays(BUYER)
RAY_LABEL_ANCHORS = ((Q(1, 2), Q(0)), (Q(0), Q(1, 2)))
SLICE_LABEL_ANCHOR = tuple(
    (SLICE_X_ENDPOINT[index] + SLICE_Y_ENDPOINT[index]) / 2
    for index in range(2)
)
SAMPLE_DIRECTION = (Q(1), Q(1))
SAMPLE_SCALE = sum((a * d for a, d in zip(SLICE_NORMAL, SAMPLE_DIRECTION)),
                   Q(0))
SAMPLE_HIT = tuple(value / SAMPLE_SCALE for value in SAMPLE_DIRECTION)
SAMPLE_LABEL_ANCHOR = SAMPLE_HIT
SAMPLE_RAY_END = (Q(3, 5), Q(3, 5))


def slice_figure():
    fig, ax = figure(8.2, 6.0)
    fig.subplots_adjust(left=0.15, right=0.96, bottom=0.18, top=0.80)
    fig.text(0.08, 0.96, TITLE, fontsize=11, color=TEXT,
             fontweight="semibold", ha="left")
    fig.text(0.08, 0.90, SUBTITLE, fontsize=8.9, color=TEXT_DIM,
             ha="left")
    style(ax, xlabel="direction d₁", ylabel="direction d₂")
    ax.set_xlim(-0.06, 0.78)
    ax.set_ylim(-0.06, 0.78)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks(tuple(index / 10 for index in range(0, 8)))
    ax.set_yticks(tuple(index / 10 for index in range(0, 8)))

    ax.add_patch(Polygon(((0, 0), (0.74, 0), (0.74, 0.74), (0, 0.74)),
                         closed=True, facecolor=PRICE, alpha=0.10,
                         edgecolor="none", zorder=1))
    ax.annotate(
        "", xy=(0.72, 0), xytext=(0, 0),
        arrowprops=dict(arrowstyle="-|>", color=PRICE, linewidth=1.8,
                        mutation_scale=12), zorder=3,
    )
    ax.annotate(
        "", xy=(0, 0.72), xytext=(0, 0),
        arrowprops=dict(arrowstyle="-|>", color=PRICE, linewidth=1.8,
                        mutation_scale=12), zorder=3,
    )
    ax.plot(
        [float(SLICE_X_ENDPOINT[0]), float(SLICE_Y_ENDPOINT[0])],
        [float(SLICE_X_ENDPOINT[1]), float(SLICE_Y_ENDPOINT[1])],
        color=PRICE, linewidth=2.5, zorder=5,
    )
    for endpoint, label, offset in (
            (SLICE_X_ENDPOINT, "(1/4, 0)", (8, -18)),
            (SLICE_Y_ENDPOINT, "(0, 1/3)", (8, 8))):
        ax.plot([float(endpoint[0])], [float(endpoint[1])], "o",
                color=PRICE, markeredgecolor=SURFACE, markeredgewidth=1.0,
                markersize=6, zorder=6)
        ax.annotate(
            label, xy=tuple(float(value) for value in endpoint),
            xytext=offset, textcoords="offset points", color=PRICE,
            fontsize=7.5,
            bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                      edgecolor=PRICE, linewidth=0.4),
            zorder=8,
        )
    ax.annotate(
        "extreme ray (1, 0)", xy=tuple(map(float, RAY_LABEL_ANCHORS[0])),
        xytext=(0, 11), textcoords="offset points", color=PRICE, fontsize=7.4,
        arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.55),
        bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                  edgecolor=PRICE, linewidth=0.4), zorder=8,
    )
    ax.annotate(
        "extreme ray (0, 1)", xy=tuple(map(float, RAY_LABEL_ANCHORS[1])),
        xytext=(9, 0), textcoords="offset points", color=PRICE, fontsize=7.4,
        arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.55),
        bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                  edgecolor=PRICE, linewidth=0.4), zorder=8,
    )
    ax.annotate(
        "4d₁ + 3d₂ = 1", xy=tuple(map(float, SLICE_LABEL_ANCHOR)),
        xytext=(34, 21), textcoords="offset points", color=PRICE, fontsize=7.4,
        arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.55),
        bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                  edgecolor=PRICE, linewidth=0.4), zorder=8,
    )
    ax.annotate(
        "", xy=tuple(map(float, SAMPLE_RAY_END)), xytext=(0, 0),
        arrowprops=dict(arrowstyle="-|>", color=TEXT_DIM, linewidth=1.2,
                        linestyle=(0, (4, 3)), mutation_scale=11), zorder=4,
    )
    ax.plot([float(SAMPLE_HIT[0])], [float(SAMPLE_HIT[1])], "o",
            color=PRICE, markeredgecolor=SURFACE, markeredgewidth=1.0,
            markersize=6.2, zorder=7)
    ax.annotate(
        "scaled by 7: (1, 1) hits (1/7, 1/7)",
        xy=tuple(map(float, SAMPLE_LABEL_ANCHOR)), xytext=(10, 12),
        textcoords="offset points", color=TEXT_DIM, fontsize=7.3,
        arrowprops=dict(arrowstyle="-", color=TEXT_DIM, linewidth=0.55),
        bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                  edgecolor=TEXT_DIM, linewidth=0.4), zorder=9,
    )
    save(fig, OUT / "slice.png", tight=False)


if __name__ == "__main__":
    slice_figure()
