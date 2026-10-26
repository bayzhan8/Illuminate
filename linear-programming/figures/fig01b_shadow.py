"""Chapter 1: the lathe time a plan uses is |a| times its shadow on a.

Staged: slide along the lathe wall (shadow fixed at 32 ÷ √5), step past it
(shadow longer, over the lathe hours), step back inside (shadow shorter).
"""

from illuminate.draw import PLAN, TEXT, TEXT_DIM, WARN, animate, chapter_dir, figure, margin_note
from linprog import mill as f
from scene import (Stages, arrow, claim, direction_line, dot, draw_axes, draw_wall, foot, mark,
                   norm, right_angle, unit)

OUT = chapter_dir("01-inside-the-walls")
A = tuple(float(v) for v in f.MILL.A[0])
NA = norm(A)
U = unit(A)
B = float(f.MILL.b[0])
PATH = [(0.0, 16.0), (19.0, 6.5), (21.0, 10.5), (17.0, 2.5), (8.0, 4.0)]
STAGES = Stages((0, 10), (28, 12), (14, 12), (16, 0), (14, 0))
TITLE = "lathe hours = |a| × (shadow of the plan on a) = √5 × shadow"
SUBS = ["start on the wall: a plan that uses exactly 32 lathe hours",
        "step 1 · slide along the wall: the shadow stays 14.3, lathe time stays 32",
        "step 2 · step away from the origin: shadow past 14.3, more than 32",
        "step 3 · step back inside: a shorter shadow, lathe time to spare",
        "step 3 · step back inside: a shorter shadow, lathe time to spare"]
END = "the wall is exactly the plans whose shadow on a is 32 ÷ √5"


def shadow_gif():
    fig, ax = figure(7.0, 6.6)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.86, bottom=0.17)
    note = margin_note(fig, y=0.02, size=9.5)
    frames = STAGES.total
    wall_len = B / NA
    tick = (wall_len * U[0], wall_len * U[1])

    def update(i):
        i = min(i, frames - 1)
        k, s = STAGES(i)
        if i == frames - 1:
            s = 1.0
        if k == 0:
            x = PATH[0]
        else:
            (x0, y0), (x1, y1) = PATH[k - 1], PATH[k]
            x = (x0 + s * (x1 - x0), y0 + s * (y1 - y0))
        ax.clear()
        draw_axes(ax)
        draw_wall(ax, 0, "lathe wall", at=13.5, color=TEXT_DIM)
        direction_line(ax, A, TEXT_DIM, None, reach=20.5)
        arrow(ax, (0, 0), A, TEXT, "a = (1, 2)", dx=0.5, dy=-0.4)
        p = foot(x, A)
        used = dot(A, x)
        over = used > B + 1e-6
        ax.plot([0, p[0]], [0, p[1]], color=WARN if over else PLAN, lw=7, alpha=0.45,
                solid_capstyle="butt", zorder=3)
        ax.plot([tick[0] - 0.5 * U[1], tick[0] + 0.5 * U[1]],
                [tick[1] + 0.5 * U[0], tick[1] - 0.5 * U[0]], color=TEXT, lw=1.6, zorder=6)
        ax.text(tick[0] - 0.7, tick[1] + 0.3, "32 ÷ √5 = 14.3", color=TEXT, fontsize=9,
                ha="right", va="bottom", zorder=7)
        ax.plot([x[0], p[0]], [x[1], p[1]], color=TEXT_DIM, lw=1.0, dashes=(3, 2), zorder=5)
        if norm((x[0] - p[0], x[1] - p[1])) > 0.8:
            right_angle(ax, p, (-U[0], -U[1]), unit((x[0] - p[0], x[1] - p[1])))
        verdict = "over the lathe hours" if over else ("on the wall" if abs(used - B) < 0.05 else "lathe time to spare")
        label_right = abs(used - B) < 0.05 and x[0] > 15
        mark(ax, x, verdict, color=WARN if over else PLAN, size=10,
             dx=0.6 if label_right else (-0.5 if x[0] > 15 else 0.5), dy=0.8,
             ha="left" if label_right else ("right" if x[0] > 15 else "left"))
        claim(ax, TITLE, END if i == frames - 1 else SUBS[k])
        note.set_text(f"a·x = {A[0]:g} × {x[0]:4.1f} + {A[1]:g} × {x[1]:4.1f} = {used:4.1f} lathe hours"
                      f"  (the mill has {B:g})\n"
                      f"shadow = a·x ÷ √5 = {used / NA:4.1f}    the wall is at {wall_len:4.1f}")
        return []

    animate(fig, update, frames, OUT / "shadow.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    shadow_gif()
