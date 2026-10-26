"""Chapter 1: why a resource draws a straight line.

Animated because the claim is about motion: slide a plan along the water wall
and its shadow on the arrow a = (1, 2) does not change; step off the wall and
the shadow grows or shrinks. The straight line is "every plan with one
particular shadow length".
"""

import math

from illuminate.draw import PLAN, TEXT, TEXT_DIM, WARN, animate, chapter_dir, figure, margin_note
from linprog import farm as f
from scene import arrow, direction_line, draw_axes, draw_wall, foot, heading, mark, norm

OUT = chapter_dir("01-inside-the-walls")
A = f.FARM.A[0]
B = float(f.FARM.b[0])

# along the wall, then straight out past it, then back inside it
PATH = [(0.0, 16.0), (19.0, 6.5), (19.0, 6.5), (21.0, 10.5), (21.0, 10.5),
        (17.0, 2.5), (17.0, 2.5), (8.0, 4.0)]
PER = 16


def at(i):
    leg, t = divmod(i, PER)
    leg = min(leg, len(PATH) - 2)
    if i >= (len(PATH) - 1) * PER:
        t = PER
    s = t / PER
    s = s * s * (3 - 2 * s)
    (x0, y0), (x1, y1) = PATH[leg], PATH[leg + 1]
    return (x0 + s * (x1 - x0), y0 + s * (y1 - y0))


def shadow_gif():
    fig, ax = figure(7.6, 5.4)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.22)
    note = margin_note(fig, y=0.02)
    frames = (len(PATH) - 1) * PER + 1
    wall_len = B / norm(A)

    def update(i):
        i = min(i, frames - 1)
        x = at(i)
        ax.clear()
        draw_axes(ax)
        heading(ax, "the water a plan uses is its shadow on the arrow (1, 2)")
        draw_wall(ax, 0, "water runs out", at=12.0)
        direction_line(ax, A, TEXT_DIM, "direction of a", reach=19.5)
        arrow(ax, (0, 0), (float(A[0]) * 2, float(A[1]) * 2), TEXT, "a", dx=0.2, dy=0.1)
        p = foot(x, A)
        used = (float(A[0]) * x[0] + float(A[1]) * x[1])
        over = used > B + 1e-9
        ax.plot([x[0], p[0]], [x[1], p[1]], color=TEXT_DIM, lw=1.0, dashes=(3, 2), zorder=5)
        ax.plot([0, p[0]], [0, p[1]], color=WARN if over else PLAN, lw=4.0,
                solid_capstyle="butt", zorder=4, alpha=0.85)
        mark(ax, x, "too much water" if over else None, color=PLAN, size=10,
             dx=-0.4, dy=0.9, ha="right")
        note.set_text(f"a·x = 1×{x[0]:4.1f} + 2×{x[1]:4.1f} = {used:4.1f} units    "
                      f"shadow {used / norm(A):4.1f}, wall at {wall_len:4.1f}")
        return []

    animate(fig, update, frames, OUT / "shadow.gif", fps=12, hold=2.5)


if __name__ == "__main__":
    shadow_gif()
