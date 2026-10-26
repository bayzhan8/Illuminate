"""Chapter 2: why nothing beats the corner, as arrows and moves.

Staged: build c = 2 x water arrow + 1 x land arrow head to tail, then sweep a
move d through every direction that stays in the region and read off the
water, land and profit it changes.
"""

import math

from illuminate.draw import PLAN, TEXT, TEXT_DIM, animate, chapter_dir, figure, margin_note
from linprog import farm as f
from scene import (Stages, arrow, claim, dot, draw_axes, draw_region, draw_wall, mark, signed, unit)

OUT = chapter_dir("02-best-is-a-corner")
O = tuple(float(v) for v in f.BEST)
WATER, LAND = (tuple(float(v) for v in r) for r in f.FARM.A)
Y = [float(v) for v in f.PRICES]
C = tuple(float(v) for v in f.PROFIT)
ALONG_WATER = unit((-WATER[1], WATER[0]))     # towards all corn
ALONG_LAND = unit((LAND[1], -LAND[0]))        # towards all wheat
START = math.degrees(math.atan2(ALONG_WATER[1], ALONG_WATER[0]))
END = math.degrees(math.atan2(ALONG_LAND[1], ALONG_LAND[0])) % 360
REACH = 3.5
STAGES = Stages((0, 10), (12, 10), (12, 10), (10, 14), (44, 0))
TITLE = "why nothing beats 8 wheat and 12 corn"
SUBS = ["both walls meet here: water arrow (1, 2), land arrow (1, 1)",
        "step 1 · 2 × the water arrow (1, 2) = (2, 4)",
        "step 2 · plus 1 × the land arrow (1, 1) = (3, 5)",
        "step 3 · that is exactly the profit arrow c = (3, 5)",
        "step 4 · every move into the region uses less water or land"]
FINAL = "c·d ≤ 0 for every move d that stays in: no plan earns more"


def why_gif():
    fig, ax = figure(7.0, 6.8)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.86, bottom=0.2)
    note = margin_note(fig, y=0.02, size=9.5)
    frames = STAGES.total
    step = (Y[0] * WATER[0], Y[0] * WATER[1])
    mid = (O[0] + step[0], O[1] + step[1])

    def update(i):
        i = min(i, frames - 1)
        k, s = STAGES(i)
        ax.clear()
        draw_axes(ax)
        ax.set_xlim(2, 16)
        ax.set_ylim(6, 18.5)
        draw_wall(ax, 0, "water wall", at=14.5, color=TEXT_DIM)
        draw_wall(ax, 1, "land wall", at=4.2, color=TEXT_DIM)
        draw_region(ax)
        lines = ["c = 2 × (1, 2) + 1 × (1, 1)"]
        if k >= 1:
            g = s if k == 1 else 1.0
            arrow(ax, O, (step[0] * g, step[1] * g), TEXT, "2 × (1, 2)" if g == 1 else None,
                  dx=-0.3, dy=-0.6, ha="right")
        if k >= 2:
            g = s if k == 2 else 1.0
            arrow(ax, mid, (LAND[0] * g, LAND[1] * g), TEXT, "+ 1 × (1, 1)" if g == 1 else None,
                  dx=0.3, dy=-0.5)
            lines = ["c = 2 × (1, 2) + 1 × (1, 1) = (2, 4) + (1, 1) = (3, 5)"]
        if k >= 3:
            a = s if k == 3 else 1.0
            ax.annotate("", xy=(O[0] + C[0], O[1] + C[1]), xytext=O, alpha=a,
                        arrowprops=dict(arrowstyle="-|>", color=PLAN, lw=2.6, alpha=a,
                                        shrinkA=0, shrinkB=0, mutation_scale=14), zorder=7)
            ax.text(O[0] + C[0] + 0.3, O[1] + C[1] + 0.3, "c = (3, 5)", color=PLAN, alpha=a,
                    fontsize=10, zorder=8)
        if k == 4:
            for e, lab in ((ALONG_WATER, "along the water wall"), (ALONG_LAND, "along the land wall")):
                ax.plot([O[0], O[0] + 5 * e[0]], [O[1], O[1] + 5 * e[1]], color=TEXT_DIM, lw=0.9,
                        dashes=(2, 2), zorder=4)
            ang = math.radians(START + s * (END - START))
            d = (REACH * math.cos(ang), REACH * math.sin(ang))
            arrow(ax, O, d, TEXT, "d", dx=0.2, dy=-0.4)
            wd, ld = dot(WATER, d), dot(LAND, d)
            lines = [f"move d = ({signed(d[0])}, {signed(d[1])})",
                     f"extra water (1, 2)·d = {signed(wd)}    extra land (1, 1)·d = {signed(ld)}",
                     f"extra profit c·d = 2 × ({signed(wd)}) + 1 × ({signed(ld)}) = {signed(dot(C, d))}"]
        mark(ax, O, "8 wheat, 12 corn", size=10, dx=-0.4, dy=-1.4, ha="right")
        claim(ax, TITLE, FINAL if i == frames - 1 else SUBS[k])
        note.set_text("\n".join(lines))
        return []

    animate(fig, update, frames, OUT / "why_best.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    why_gif()
