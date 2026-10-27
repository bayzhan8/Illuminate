"""An unbounded set or an open edge can prevent a best plan."""

from fractions import Fraction

from matplotlib.patches import Polygon

from illuminate.draw import (HAIRLINE, PLAN, TEXT, TEXT_DIM, chapter_dir, figure,
                             margin_note, save)
from linprog import mill as f
from linprog.lp import solve_square
from scene import arrow, claim, ordered

OUT = chapter_dir("02-best-is-a-corner")


def format_roubles(thousands):
    amount = Fraction(thousands) * 1000
    return f"{int(amount):,} roubles"


def axes_style(ax, xlim, ylim, xticks, yticks):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.set_xlabel("3-ply batches t", fontsize=9.3, color=TEXT_DIM, labelpad=6)
    ax.set_ylabel("5-ply batches f", fontsize=9.3, color=TEXT_DIM, labelpad=6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.65, linestyle=(0, (1, 3)), zorder=0)
    ax.set_axisbelow(True)
    ax.set_aspect("equal", adjustable="box")


def no_best_still():
    fig, placeholder = figure(12.4, 6.2)
    fig.delaxes(placeholder)
    left = fig.add_subplot(1, 2, 1)
    right = fig.add_subplot(1, 2, 2)
    fig.subplots_adjust(left=0.075, right=0.985, top=0.81, bottom=0.2, wspace=0.3)
    note = margin_note(fig, y=0.025, size=9.1)

    levels_left = (f.MILL.b[1], 2 * f.MILL.b[1], 3 * f.MILL.b[1])
    c_left = f.MILL.c
    axes_style(left, (-1, 22), (-1, 15), range(0, 23, 5), range(0, 16, 3))
    left.axhline(0, color=TEXT, lw=1.2, zorder=2)
    left.axvline(0, color=TEXT, lw=1.2, zorder=2)
    left.fill([0, 21, 21, 0], [0, 0, 14, 14], color=PLAN, alpha=0.055, zorder=1)
    for level in levels_left:
        vertical = (Fraction(0), level / c_left[1])
        horizontal = (level / c_left[0], Fraction(0))
        left.plot([float(vertical[0]), float(horizontal[0])],
                  [float(vertical[1]), float(horizontal[1])],
                  color=TEXT_DIM, lw=1.25, dashes=(5, 3), zorder=3)
        left.text(float(vertical[0]) + 0.35, float(vertical[1]) + 0.16,
                  format_roubles(level),
                  fontsize=8.0, color=TEXT, ha="left", va="bottom",
                  bbox=dict(boxstyle="square,pad=0.16", facecolor="#fffff8",
                            edgecolor="none"), zorder=6)
    arrow(left, (0, 0), tuple(float(v) for v in c_left), TEXT,
          "c = (3, 5)", dx=0.25, dy=0.25, lw=1.8)
    claim(left, "no best plan when the region is unbounded",
          "the quadrant has no lathe or press limit")

    corners = ordered(f.MILL)
    right.add_patch(Polygon(corners, closed=True, facecolor=PLAN, alpha=0.12,
                            edgecolor="none", zorder=1))
    axes_style(right, (-1, 22), (-1, 21), range(0, 23, 5), range(0, 22, 5))
    right.axhline(0, color=TEXT, lw=1.1, zorder=2)
    right.axvline(0, color=TEXT, lw=1.1, zorder=2)
    lathe, press = f.MILL.A
    xlim = right.get_xlim()
    for row_index, row in enumerate((lathe, press)):
        rowf = tuple(float(v) for v in row)
        rhs = float(f.MILL.b[row_index])
        ys = [(rhs - rowf[0] * t) / rowf[1] for t in xlim]
        right.plot(xlim, ys, color=TEXT, lw=1.55 if row_index == 0 else 1.6,
                   dashes=(5, 3) if row_index == 1 else (), zorder=3)
    levels_right = tuple(f.MILL.b[1] - Fraction(1, 10 ** k) for k in (0, 1, 2))
    c_right = (Fraction(1), Fraction(1))
    for level, t in zip(levels_right, (Fraction(10), Fraction(12), Fraction(14))):
        p = solve_square([c_right, f.MILL.A[0]], [level, f.MILL.b[0]])
        # The chosen point on each level is interior to the feasible region.
        point = (t, level - t)
        assert f.MILL.feasible(point)
        bottom = solve_square([c_right, (Fraction(0), Fraction(1))], [level, 0])
        right.plot([float(p[0]), float(bottom[0])],
                   [float(p[1]), float(bottom[1])], color=TEXT_DIM,
                   lw=1.0, dashes=(3, 2), zorder=4)
        right.text(float(t) + 0.2, float(level - t) + 0.25,
                   f"{float(level):g}k", fontsize=8.4, color=TEXT,
                   ha="left", va="bottom",
                   bbox=dict(boxstyle="square,pad=0.16", facecolor="#fffff8",
                             edgecolor="none"), zorder=7)
    arrow(right, (1, 1), (3, 3), TEXT, "c = (1, 1)", dx=0.22, dy=0.18,
          lw=1.8)
    claim(right, "no best plan when the edge is missing",
          "the dashed press edge would be forbidden")
    note.set_text("The left value lines continue forever.  On the right, 19,000, "
                  "19,900 and 19,990 roubles approach the missing 20,000-rouble edge.")
    return save(fig, OUT / "no_best.png", tight=False)


if __name__ == "__main__":
    no_best_still()
