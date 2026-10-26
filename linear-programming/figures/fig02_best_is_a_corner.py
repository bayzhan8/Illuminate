"""Chapter 2: slide a line of equal profit along c until it is about to leave.

Staged: a pause at $80,000 (all corn) while the darker part of the region
shows the plans that still earn more, then on to the last point, a corner.
"""

from illuminate.draw import PLAN, TEXT_DIM, animate, chapter_dir, figure, margin_note
from linprog import farm as f
from scene import (Stages, arrow, claim, clip, direction_line, draw_axes, draw_region, draw_wall, fill,
                   iso_profit, mark, norm, ordered, usd)

OUT = chapter_dir("02-best-is-a-corner")
C = tuple(float(v) for v in f.PROFIT)
NC = norm(C)
MID = float(f.ALL_CORN_PROFIT)
TOP = float(f.BEST_PROFIT)
STAGES = Stages((0, 8), (36, 16), (14, 0))
TITLE = "plans that earn the same lie on one line, at right angles to c"


def sweep_gif():
    fig, ax = figure(7.0, 6.6)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.86, bottom=0.17)
    note = margin_note(fig, y=0.02, size=9.5)
    frames = STAGES.total
    region = ordered()

    def update(i):
        i = min(i, frames - 1)
        k, s = STAGES(i)
        level = (0.0, MID * s, MID + (TOP - MID) * s)[k]
        done = i == frames - 1
        ax.clear()
        draw_axes(ax)
        draw_wall(ax, 0)
        draw_wall(ax, 1)
        draw_region(ax)
        fill(ax, clip(region, C, level, keep_le=False), PLAN, 0.35, z=2)
        iso_profit(ax, level)
        direction_line(ax, C, TEXT_DIM, None, reach=21)
        arrow(ax, (0, 0), C, TEXT_DIM, "c = (3, 5)", dx=0.3, dy=0.0)
        k_ = level / NC ** 2
        ax.plot([0, C[0] * k_], [0, C[1] * k_], color=PLAN, lw=6, alpha=0.35, solid_capstyle="butt", zorder=3)
        if k >= 1 and s >= 1 or k == 2:
            mark(ax, f.ALL_CORN, f"all corn: {usd(MID)}", color=TEXT_DIM, size=8, dx=0.6, dy=-3.5)
        if done:
            mark(ax, f.BEST, f"8 wheat, 12 corn: {usd(TOP)}", color=PLAN, size=11, dx=0.5, dy=0.6)
            sub = "the last point the line touches is a corner: 8 wheat, 12 corn"
        elif k == 1 and s >= 1:
            sub = "all corn earns $80,000, but the dark part of the region earns more"
        elif k == 0:
            sub = "c = (3, 5) is the profit per acre; start at $0"
        else:
            sub = "raise the profit: the line slides out along c and never turns"
        claim(ax, TITLE, sub)
        note.set_text(f"every plan on the dashed line earns {usd(level)}; the dark plans earn more\n"
                      f"shadow on c = profit ÷ |c| = {level:4.1f} ÷ √34 = {level / NC:4.1f}")
        return []

    animate(fig, update, frames, OUT / "sweep.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    sweep_gif()
