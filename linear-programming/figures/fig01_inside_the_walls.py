"""Chapter 1: the plans the farm can carry out, and three test plans.

A still: nothing moves in the argument. Each test plan is labelled with the
resource it breaks, so colour is never the only cue.
"""

from illuminate.draw import PLAN, PRICE, chapter_dir, figure, save, tag
from linprog import farm as f
from scene import draw_axes, draw_region, draw_wall, heading, mark

OUT = chapter_dir("01-inside-the-walls")
TESTS = [(6, 8), (6, 14), (14, 9)]


def verdict(p):
    broken = [f.RESOURCES[i] for i in range(f.FARM.m) if f.FARM.slack(i, p) < 0]
    return "fits" if not broken else "too much " + " and ".join(broken)


def region_png():
    fig, ax = figure(7.6, 5.2)
    draw_axes(ax)
    heading(ax, "every plan the farm can actually carry out")
    draw_wall(ax, 0, "water: 32 units", at=20.8)
    draw_wall(ax, 1, "land: 20 acres", at=3.2)
    draw_region(ax)
    tag(ax, 3.0, 4.0, "possible plans", color=PLAN, size=11, weight="bold")
    for p, dy in zip(TESTS, (0.0, 0.0, -1.3)):
        ok = f.FARM.feasible(p)
        mark(ax, p, f"{p[0]} wheat, {p[1]} corn\n{verdict(p)}",
             color=PLAN if ok else PRICE, size=8, dx=0.5, dy=dy)
    save(fig, OUT / "region.png")


if __name__ == "__main__":
    region_png()
