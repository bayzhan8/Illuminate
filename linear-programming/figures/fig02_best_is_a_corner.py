"""Chapter 2: slide a line of equal profit up until it is about to leave.

Animated because the sweep is the argument: the last point the line touches
is a corner, and the reader should watch that happen rather than be told.
"""

from fractions import Fraction

from illuminate.draw import PLAN, TEXT_DIM, animate, chapter_dir, figure, margin_note
from linprog import farm as f
from scene import arrow, direction_line, draw_axes, draw_region, draw_wall, foot, heading, iso_profit, mark, norm

OUT = chapter_dir("02-best-is-a-corner")


def sweep_gif():
    fig, ax = figure(7.6, 5.0)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.2)
    note = margin_note(fig, y=0.02)
    top = float(f.BEST_PROFIT)
    frames = 42

    def update(i):
        i = min(i, frames - 1)
        s = i / (frames - 1)
        level = top * s * s * (3 - 2 * s)
        ax.clear()
        draw_axes(ax)
        heading(ax, "plans worth the same lie on one straight line")
        draw_wall(ax, 0)
        draw_wall(ax, 1)
        draw_region(ax)
        iso_profit(ax, level)
        direction_line(ax, f.PROFIT, TEXT_DIM, "direction of c", reach=21)
        arrow(ax, (0, 0), (3, 5), TEXT_DIM, "c", dx=0.3, dy=0.0)
        k = level / norm(f.PROFIT) ** 2
        ax.plot([0, 3 * k], [0, 5 * k], color=PLAN, lw=4.0, solid_capstyle="butt",
                zorder=4, alpha=0.85)
        mark(ax, f.ALL_CORN, f"all corn: {f.money(f.ALL_CORN_PROFIT)}",
             color=TEXT_DIM, size=8, dx=0.6, dy=-3.5)
        if i == frames - 1:
            mark(ax, f.BEST, f"8 wheat, 12 corn: {f.money(f.BEST_PROFIT)}",
                 color=PLAN, size=11, dx=0.5, dy=0.5)
        note.set_text(f"every plan on the dashed line earns {f.money(Fraction(round(level)))}"
                      f"   shadow on c = {level / norm(f.PROFIT):4.1f}")
        return []

    animate(fig, update, frames, OUT / "sweep.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    sweep_gif()
