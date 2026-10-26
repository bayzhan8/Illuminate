"""Chapter 2: turn the value arrow and the best corner changes.

A gallery: four value arrows, each with the line of equal value through its
best plan. When c points along a wall's arrow, a whole edge ties.
"""

import matplotlib.pyplot as plt

from illuminate.draw import PLAN, TEXT, chapter_dir, save
from linprog import mill as f
from linprog.lp import LP, vertices
from scene import arrow, draw_axes, draw_region, iso_value, mark, unit, roubles

OUT = chapter_dir("02-best-is-a-corner")
GALLERY = [(1, 3), (3, 5), (1, 1), (3, 1)]
NAMES = {(0, 16): "all 5-ply", (8, 12): "8 3-ply, 12 5-ply",
         (20, 0): "all 3-ply", (0, 0): "nothing made"}


def best_of(c):
    lp = LP.build(c=c, A=[list(r) for r in f.MILL.A], b=list(f.MILL.b))
    pts = vertices(lp)
    top = max(lp.value(p) for p in pts)
    return lp, [p for p in pts if lp.value(p) == top], top


def turns_png():
    fig, axes = plt.subplots(2, 2, figsize=(7.6, 7.0))
    for ax, c in zip(axes.flat, GALLERY):
        lp, best, top = best_of(c)
        draw_axes(ax)
        ax.set_xlabel("")
        ax.set_ylabel("")
        draw_region(ax, lp)
        iso_value(ax, float(top), c=c)
        pts = sorted(tuple(float(v) for v in p) for p in best)
        if len(pts) > 1:
            ax.plot([p[0] for p in pts], [p[1] for p in pts], color=PLAN, lw=4.5, zorder=6)
            verdict = f"a whole edge ties at {roubles(top)}"
        else:
            verdict = f"best: {NAMES[tuple(int(v) for v in pts[0])]}, {roubles(top)}"
        for p in pts:
            mark(ax, p, size=9)
        u = unit(c)
        end = pts[-1]
        arrow(ax, (end[0] - 5 * u[0], end[1] - 5 * u[1]), (5 * u[0], 5 * u[1]), TEXT)
        ax.text(end[0] - 5 * u[0] - 0.4, end[1] - 5 * u[1] - 0.4, "c", fontsize=10, ha="right", va="top")
        ax.set_title(f"c = ({c[0]}, {c[1]})\n{verdict}", loc="left", fontsize=10, color=TEXT)
    fig.subplots_adjust(hspace=0.5)
    fig.suptitle("turn the value arrow c and the best corner moves", x=0.02, ha="left",
                 fontsize=11, fontweight="semibold")
    save(fig, OUT / "turns.png")


if __name__ == "__main__":
    turns_png()
