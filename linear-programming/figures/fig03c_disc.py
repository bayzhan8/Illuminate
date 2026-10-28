"""The largest disc inside the mill's region."""

import math

from matplotlib.patches import Circle

from illuminate.draw import (PLAN, PLAN_FILL, SURFACE, TEXT_DIM, animate, chapter_dir, figure,
                             margin_note, tag)
from linprog import mill as f
from scene import Stages, claim, draw_axes, draw_region, draw_wall, norm, unit

OUT = chapter_dir("03-writing-it-down")
LATHE = tuple(float(v) for v in f.MILL.A[0])
PRESS = tuple(float(v) for v in f.MILL.A[1])
LATHE_LIMIT = float(f.MILL.b[0])
PRESS_LIMIT = float(f.MILL.b[1])
LATHE_NORM = norm(LATHE)
PRESS_NORM = norm(PRESS)
R_STAR = PRESS_LIMIT / (sum(PRESS) + PRESS_NORM)
STAGES = Stages((28, 12), (28, 12), (0, 18))
TITLE = "the largest disc touches the press wall first"
SUBS = (
    "grow a disc around (r, r), touching both axes",
    "the press wall stops the radius at r = 20 − 10√2",
    "",
)
FINAL = "the largest disc touches the press wall and both axes, not the lathe wall"


def disc_gif():
    fig, ax = figure(7.0, 6.6)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.85, bottom=0.2)
    note = margin_note(fig, y=0.025, size=8.9)
    frames = STAGES.total

    def update(i):
        i = min(i, frames - 1)
        stage, s = STAGES(i)
        if i == frames - 1:
            s = 1.0
        if stage == 0:
            radius = 3 * s
        elif stage == 1:
            radius = 3 + (R_STAR - 3) * s
        else:
            radius = R_STAR
        center = (radius, radius)

        ax.clear()
        draw_axes(ax)
        draw_region(ax, alpha=0.11)
        draw_wall(ax, 0, color=TEXT_DIM, lw=1.3)
        draw_wall(ax, 1, color=TEXT_DIM, lw=1.3)
        tag(ax, 20.4, 6.25, "lathe wall", color=TEXT_DIM, size=9.2)
        tag(ax, 2.0, 18.05, "press wall", color=TEXT_DIM, size=9.2)
        ax.add_patch(Circle(center, radius, facecolor=PLAN_FILL, edgecolor=PLAN,
                            linewidth=1.8, zorder=5))
        ax.plot([center[0]], [center[1]], "o", color=PLAN, markersize=4.5, zorder=7)

        press_used = (sum(PRESS) + PRESS_NORM) * radius
        lathe_used = (sum(LATHE) + LATHE_NORM) * radius
        if i == frames - 1:
            press_unit = unit(PRESS)
            press_touch = (center[0] + radius * press_unit[0],
                           center[1] + radius * press_unit[1])
            ax.plot([press_touch[0]], [press_touch[1]], "o", color=PLAN,
                    markeredgecolor=SURFACE, markeredgewidth=1.3, markersize=7.5,
                    zorder=8)
            tag(ax, 11.2, 9.4, "touch (10, 10)", color=PLAN, size=8.8)

            lathe_unit = unit(LATHE)
            slack = (LATHE_LIMIT - sum(LATHE) * radius) / LATHE_NORM
            circle_edge = (center[0] + radius * lathe_unit[0],
                           center[1] + radius * lathe_unit[1])
            wall_foot = (center[0] + slack * lathe_unit[0],
                         center[1] + slack * lathe_unit[1])
            ax.annotate("", xy=wall_foot, xytext=circle_edge,
                        arrowprops=dict(arrowstyle="<->", color=TEXT_DIM, lw=0.9,
                                        shrinkA=0, shrinkB=0, mutation_scale=7),
                        zorder=8)
            midpoint = ((circle_edge[0] + wall_foot[0]) / 2,
                        (circle_edge[1] + wall_foot[1]) / 2)
            tag(ax, midpoint[0] + 0.75 * lathe_unit[0],
                midpoint[1] + 0.75 * lathe_unit[1], f"{slack - radius:.2f}",
                color=TEXT_DIM, size=8.8)

        if i == frames - 1:
            claim(ax, TITLE)
            ax.text(0, 1.025, FINAL, transform=ax.transAxes, fontsize=8.4,
                    color=TEXT_DIM, ha="left", va="bottom")
        else:
            claim(ax, TITLE, SUBS[stage])
        note.set_text(
            f"r = {radius:.2f}   press: t + f + √2 r = {press_used:.2f} ≤ 20\n"
            f"lathe: t + 2f + √5 r = {lathe_used:.2f} ≤ 32"
        )
        return []

    animate(fig, update, frames, OUT / "disc.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    disc_gif()
