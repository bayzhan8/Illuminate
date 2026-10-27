"""The law of cosines makes the dot product the length of a shadow."""

import math
from fractions import Fraction

from matplotlib.patches import Arc

from illuminate.draw import PLAN, TEXT, TEXT_DIM, chapter_dir, figure, margin_note, save
from linprog import mill as f
from scene import arrow, claim, draw_axes, right_angle, unit

OUT = chapter_dir("01-inside-the-walls")
A = f.MILL.A[0]
X = (Fraction(6), Fraction(8))
AX = sum((u * v for u, v in zip(A, X)), Fraction(0))
AA = sum((u * u for u in A), Fraction(0))
P = tuple(AX * u / AA for u in A)


def cosine_still():
    fig, ax = figure(7.2, 6.1)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.83, bottom=0.19)
    note = margin_note(fig, y=0.035, size=9.5)
    draw_axes(ax)
    ax.set_xlim(-0.8, 9.2)
    ax.set_ylim(-0.8, 11.2)
    ax.set_xticks(range(0, 10, 2))
    ax.set_yticks(range(0, 12, 2))

    a = tuple(float(v) for v in A)
    x = tuple(float(v) for v in X)
    p = tuple(float(v) for v in P)
    side = tuple(xi - ai for xi, ai in zip(x, a))
    ua = unit(a)

    ax.plot([0, p[0]], [0, p[1]], color=PLAN, lw=7, alpha=0.45,
            solid_capstyle="butt", zorder=3)
    ax.plot([x[0], p[0]], [x[1], p[1]], color=TEXT_DIM, lw=1.2,
            dashes=(4, 3), zorder=4)
    arrow(ax, (0, 0), a, TEXT, "a = (1, 2)", dx=0.2, dy=-0.4)
    arrow(ax, (0, 0), x, PLAN, "x = (6, 8)", dx=0.35, dy=0.35)
    arrow(ax, a, side, TEXT_DIM, "x − a", dx=-1.2, dy=-0.85, ha="right")

    angle_a = math.degrees(math.atan2(a[1], a[0]))
    angle_x = math.degrees(math.atan2(x[1], x[0]))
    ax.add_patch(Arc((0, 0), 2.6, 2.6, theta1=angle_x, theta2=angle_a,
                     color=TEXT_DIM, lw=1.1, zorder=5))
    theta = math.radians((angle_x + angle_a) / 2)
    ax.text(1.65 * math.cos(theta), 1.65 * math.sin(theta), "θ",
            color=TEXT, fontsize=11, ha="center", va="center",
            fontfamily="DejaVu Sans")
    right_angle(ax, p, (-ua[0], -ua[1]), unit((x[0] - p[0], x[1] - p[1])),
                s=0.48)
    ax.plot([p[0]], [p[1]], "o", color=PLAN, markersize=6,
            markeredgecolor="#fffff8", markeredgewidth=1.5, zorder=7)
    ax.text(p[0] - 0.5, p[1] + 0.35, "p = (4.4, 8.8)", color=PLAN,
            fontsize=9.2, ha="right", va="bottom", zorder=8)

    claim(ax, "the dot product equals a shadow length",
          "law of cosines: the third side is x − a")
    shadow = float(AX) / math.sqrt(float(AA))
    note.set_text(f"a·x = {AX} = |a| × |x| × cos(angle)\n"
                  f"shadow |p| = {AX} ÷ √5 ≈ {shadow:.1f}")
    return save(fig, OUT / "cosine.png", tight=False)


if __name__ == "__main__":
    cosine_still()
