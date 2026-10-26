"""Chapter 1: one line for every amount of water, all at right angles to a.

The line a·x = b moves out along a as b grows. Three fixed plans report how
much water they use, so the reader sees that only plans on the line use
exactly b, the shaded side less, the far side more.
"""

from illuminate.draw import HAIRLINE, PLAN, TEXT, TEXT_DIM, animate, chapter_dir, figure, margin_note, tag
from linprog import farm as f
from scene import (WINDOW_POLY, Stages, arrow, claim, clip, direction_line, dot, draw_axes, fill,
                   line_where, mark, norm, right_angle, unit)

OUT = chapter_dir("01-inside-the-walls")
A = tuple(float(v) for v in f.FARM.A[0])
NA = norm(A)
U = unit(A)
V = (U[1], -U[0])
WALL = float(f.FARM.b[0])
TOP = 40.0
PASSED = [8, 16, 24, 32, 40]
WITNESS = [(4.0, 14.0), (10.0, 6.0), (16.0, 12.0)]
STAGES = Stages((0, 10), (48, 10), (16, 0))
TITLE = "each amount of water b gives one line a·x = b, at right angles to a"


def level(k, s):
    return (0.0, TOP * s, TOP - (TOP - WALL) * s)[k]


def levels_gif():
    fig, ax = figure(7.0, 6.6)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.86, bottom=0.17)
    note = margin_note(fig, y=0.02, size=9.5)
    frames = STAGES.total

    def update(i):
        i = min(i, frames - 1)
        k, s = STAGES(i)
        b = level(k, s)
        done = i == frames - 1
        ax.clear()
        draw_axes(ax)
        fill(ax, clip(WINDOW_POLY, A, b), PLAN, 0.12)
        for pb in PASSED:
            if pb <= max(b, TOP if k == 2 else 0) + 1e-9 and abs(pb - b) > 0.5:
                line_where(ax, A, pb, color=HAIRLINE, linewidth=1.0)
                t = (pb / NA * U[0], pb / NA * U[1])
                ax.text(t[0] + 0.5, t[1] - 0.1, f"{pb}", color=TEXT_DIM, fontsize=8.5, zorder=6)
        direction_line(ax, A, TEXT_DIM, None, reach=20.5)
        arrow(ax, (0, 0), A, TEXT, "a = (1, 2)", dx=0.5, dy=-0.4)
        tip = (b / NA * U[0], b / NA * U[1])
        if b > 0.3:
            ax.plot([0, tip[0]], [0, tip[1]], color=PLAN, lw=6, alpha=0.35, solid_capstyle="butt", zorder=3)
            line_where(ax, A, b, color=TEXT, linewidth=2.0 if done else 1.6)
            right_angle(ax, tip, (-U[0], -U[1]), V)
            ax.text(tip[0] + 0.5, tip[1] - 0.1, ("water wall  a·x = 32" if done else f"a·x = {b:.0f}"),
                    color=TEXT, fontsize=10, zorder=7, fontweight="semibold" if done else "normal")
        if b >= 12:
            lo = (tip[0] - 2.4 * U[0] + 4.6 * V[0], tip[1] - 2.4 * U[1] + 4.6 * V[1])
            hi = (tip[0] + 2.0 * U[0] + 5.6 * V[0], tip[1] + 2.0 * U[1] + 5.6 * V[1])
            tag(ax, *lo, "a·x < b", color=PLAN, size=9.5, ha="center")
            tag(ax, *hi, "a·x > b", color=TEXT_DIM, size=9.5, ha="center")
        for w in WITNESS:
            use = dot(A, w)
            if abs(use - b) < 0.6:
                mark(ax, w, f"uses {use:g}: on the line", color=TEXT, size=10)
            elif use < b:
                mark(ax, w, f"uses {use:g}: less", color=PLAN, size=8)
            else:
                mark(ax, w, f"uses {use:g}: more", color=TEXT_DIM, size=8)
        if done:
            sub = "b = 32 is the water wall: on it exactly 32, behind it less, beyond more"
        elif k == 0:
            sub = "a = (1, 2) holds the water per acre of wheat and of corn"
        elif k == 1:
            sub = "raise b: the line slides out along a and never turns"
        else:
            sub = "back to b = 32, the water the farm actually has"
        claim(ax, TITLE, sub)
        note.set_text(f"b = {b:4.1f}: every plan on the line uses exactly {b:4.1f} units of water\n"
                      f"the line crosses a's direction at distance b ÷ |a| = {b:4.1f} ÷ √5 = {b / NA:4.1f}")
        return []

    animate(fig, update, frames, OUT / "levels.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    levels_gif()
