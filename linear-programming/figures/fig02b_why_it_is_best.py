"""Chapter 2: why nothing beats the corner, as arrows.

A still: at 8 wheat and 12 corn the profit arrow c = (3, 5) is exactly
2 x (water arrow) + 1 x (land arrow), drawn head to tail so the reader can
count it.
"""

from illuminate.draw import PLAN, TEXT, TEXT_DIM, chapter_dir, figure, save
from linprog import farm as f
from scene import arrow, draw_axes, draw_region, draw_wall, heading, mark

OUT = chapter_dir("02-best-is-a-corner")


def arrows_png():
    fig, ax = figure(7.6, 5.2)
    draw_axes(ax)
    ax.set_xlim(2, 16)
    ax.set_ylim(6, 18.5)
    heading(ax, "at the best corner, c is built from the two walls' arrows")
    draw_wall(ax, 0, "water wall", at=14.5, color=TEXT_DIM)
    draw_wall(ax, 1, "land wall", at=4.2, color=TEXT_DIM)
    draw_region(ax)
    o = tuple(float(v) for v in f.BEST)
    water, land = (tuple(float(v) for v in r) for r in f.FARM.A)
    y = [float(v) for v in f.PRICES]
    c = tuple(float(v) for v in f.PROFIT)
    step = (y[0] * water[0], y[0] * water[1])
    arrow(ax, o, step, TEXT, f"{y[0]:g} × water arrow (1, 2)", dx=-0.3, dy=0.0, ha="right")
    arrow(ax, (o[0] + step[0], o[1] + step[1]), (y[1] * land[0], y[1] * land[1]), TEXT,
          f"+ {y[1]:g} × land arrow (1, 1)", dx=0.3, dy=0.2)
    arrow(ax, o, c, PLAN, lw=2.6)
    ax.text(o[0] + c[0] / 2 + 0.35, o[1] + c[1] / 2 - 0.3, "c = (3, 5), the profit arrow",
            color=PLAN, fontsize=10, ha="left", va="center", zorder=8)
    mark(ax, o, "8 wheat, 12 corn", size=10, dx=-0.4, dy=-1.4, ha="right")
    save(fig, OUT / "arrows.png")


if __name__ == "__main__":
    arrows_png()
