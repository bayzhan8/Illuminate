"""The epigraph of an absolute value has a bottom but no top."""

from pathlib import Path

from illuminate.draw import (HAIRLINE, PLAN, PLAN_FILL, SURFACE, TEXT, TEXT_DIM, figure, save,
                             tag)
from scene import claim, clip, fill

OUT = Path(__file__).resolve().parents[1] / "chapters" / "03-writing-it-down"
WINDOW = (-3.0, 3.0, -0.6, 3.4)
WINDOW_POLY = [(WINDOW[0], WINDOW[2]), (WINDOW[1], WINDOW[2]),
               (WINDOW[1], WINDOW[3]), (WINDOW[0], WINDOW[3])]


def vee_png():
    fig, ax = figure(7.0, 5.8)
    fig.subplots_adjust(left=0.13, right=0.98, top=0.83, bottom=0.16)
    ax.set_xlim(WINDOW[0], WINDOW[1])
    ax.set_ylim(WINDOW[2], WINDOW[3])
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("y", fontsize=10, color=TEXT_DIM, labelpad=7)
    ax.set_ylabel("z", fontsize=10, color=TEXT_DIM, labelpad=7)
    ax.set_xticks(range(-3, 4))
    ax.set_yticks(range(0, 4))
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)), zorder=0)
    ax.set_axisbelow(True)

    region = clip(WINDOW_POLY, (1, -1), 0, keep_le=True)
    region = clip(region, (-1, -1), 0, keep_le=True)
    fill(ax, region, PLAN_FILL, 0.14, z=1)
    ax.axhline(0, color=TEXT_DIM, linewidth=0.9, zorder=2)
    ax.plot([-3, 0], [3, 0], color=PLAN, linewidth=1.7, zorder=4)
    ax.plot([0, 3], [0, 3], color=PLAN, linewidth=1.7, zorder=4)
    tag(ax, -1.85, 1.15, "z ≥ −y", color=PLAN, size=9.5)
    tag(ax, 1.85, 1.15, "z ≥ y", color=PLAN, size=9.5)

    ax.annotate("", xy=(0, 0.12), xytext=(0, 2.2),
                arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=2.0,
                                shrinkA=0, shrinkB=0, mutation_scale=14), zorder=7)
    tag(ax, -0.72, 1.34, "minimize z", color=TEXT, size=9.5, ha="center")
    ax.plot([0], [0], "o", color=PLAN, markeredgecolor=SURFACE,
            markeredgewidth=1.5, markersize=8, zorder=8)

    ax.annotate("", xy=(2.35, 3.25), xytext=(2.35, 2.35),
                arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=2.0,
                                shrinkA=0, shrinkB=0, mutation_scale=14), zorder=7)
    tag(ax, 0.35, 3.15, "maximize z: no top", color=TEXT, size=9.2)
    claim(ax, "minimize z reaches the V; maximize z has no top")
    return save(fig, OUT / "vee.png", tight=False)


if __name__ == "__main__":
    vee_png()
