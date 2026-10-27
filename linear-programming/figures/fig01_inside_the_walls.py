"""Chapter 1: the plans the mill can carry out, and three test plans.

A still: nothing moves in the argument. Each test plan is labelled with the
resource it breaks, so colour is never the only cue.
"""

from illuminate.draw import PLAN, PRICE, chapter_dir, figure, save, tag
from linprog import mill as f
from scene import draw_axes, draw_region, draw_wall, heading, mark

OUT = chapter_dir("01-inside-the-walls")
TESTS = [(6, 8), (6, 14), (14, 9)]


def verdict(p):
    broken = [f.RESOURCES[i] for i in range(f.MILL.m) if f.MILL.slack(i, p) < 0]
    if not broken:
        return "fits"
    return "over the lathe hours" if "lathe" in broken else "too many press hours"


def region_png():
    fig, ax = figure(7.6, 5.2)
    draw_axes(ax)
    heading(ax, "every plan the mill can actually carry out")
    draw_wall(ax, 0, "lathe: 32 h", at=20.8)
    draw_wall(ax, 1, "press: 20 h", at=3.2)
    draw_region(ax)
    tag(ax, 3.0, 4.0, "possible plans", color=PLAN, size=11, weight="bold")
    for p, dy in zip(TESTS, (0.0, 0.0, -1.3)):
        ok = f.MILL.feasible(p)
        mark(ax, p, f"{p[0]} 3-ply, {p[1]} 5-ply\n{verdict(p)}",
             color=PLAN if ok else PRICE, size=8, dx=0.5, dy=dy)
    save(fig, OUT / "region.png")


if __name__ == "__main__":
    region_png()
