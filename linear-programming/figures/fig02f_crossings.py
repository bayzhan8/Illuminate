"""Every corner is among the pairwise crossings of the four walls."""

from fractions import Fraction
from itertools import combinations

from matplotlib.patches import Polygon

from illuminate.draw import HAIRLINE, PLAN, TEXT, TEXT_DIM, WARN, chapter_dir, figure, margin_note, save
from linprog import mill as f
from linprog.lp import solve_square
from scene import claim, ordered

OUT = chapter_dir("02-best-is-a-corner")
ROWS = [
    ("lathe", f.MILL.A[0], f.MILL.b[0]),
    ("press", f.MILL.A[1], f.MILL.b[1]),
    ("t = 0", (Fraction(-1), Fraction(0)), Fraction(0)),
    ("f = 0", (Fraction(0), Fraction(-1)), Fraction(0)),
]


def crossings():
    out = []
    for first, second in combinations(ROWS, 2):
        point = solve_square([first[1], second[1]], [first[2], second[2]])
        assert point is not None
        out.append((first[0], second[0], point, f.MILL.feasible(point)))
    return out


CROSSINGS = crossings()


def draw_wall(ax, row, rhs, xlim, ylim):
    a0, a1 = row
    if a1:
        xs = xlim
        ys = tuple(float((rhs - a0 * Fraction(str(x))) / a1) for x in xs)
        ax.plot(xs, ys, color=TEXT, lw=1.45, zorder=2)
    else:
        x = float(rhs / a0)
        ax.plot([x, x], ylim, color=TEXT, lw=1.45, zorder=2)


def crossings_still():
    fig, ax = figure(8.4, 6.8)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.83, bottom=0.18)
    note = margin_note(fig, y=0.025, size=9.5)
    xlim = (-1.0, 34.0)
    ylim = (-1.0, 22.0)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_xticks(range(0, 35, 5))
    ax.set_yticks(range(0, 23, 5))
    ax.set_xlabel("3-ply batches t", fontsize=10, color=TEXT_DIM, labelpad=7)
    ax.set_ylabel("5-ply batches f", fontsize=10, color=TEXT_DIM, labelpad=7)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)), zorder=0)
    ax.set_axisbelow(True)
    ax.set_aspect("equal", adjustable="box")

    corners = ordered(f.MILL)
    ax.add_patch(Polygon(corners, closed=True, facecolor=PLAN, alpha=0.13,
                         edgecolor=PLAN, linewidth=1.6, zorder=1))
    for _, row, rhs in ROWS:
        draw_wall(ax, row, rhs, xlim, ylim)

    label_positions = {
        (Fraction(0), Fraction(0)): (1.1, 1.1, "left"),
        (Fraction(20), Fraction(0)): (20.5, 1.1, "left"),
        (Fraction(0), Fraction(16)): (1.1, 16.5, "left"),
        (Fraction(8), Fraction(12)): (8.7, 12.7, "left"),
        (Fraction(32), Fraction(0)): (31.2, 1.7, "right"),
        (Fraction(0), Fraction(20)): (1.2, 20.4, "left"),
    }
    for _, _, point, feasible in CROSSINGS:
        x, y = float(point[0]), float(point[1])
        color = PLAN if feasible else WARN
        if feasible:
            ax.plot([x], [y], "o", color=color, markersize=9,
                    markeredgecolor="#fffff8", markeredgewidth=1.8, zorder=7)
        else:
            ax.plot([x], [y], marker="x", color=color, markersize=10,
                    markeredgewidth=2.2, linestyle="none", zorder=8)
        lx, ly, ha = label_positions[point]
        if feasible:
            label = f"({point[0]}, {point[1]})"
        elif point == (Fraction(32), Fraction(0)):
            label = "(32, 0), breaks press"
        else:
            label = "(0, 20), breaks lathe"
        ax.text(lx, ly, label, color=color, fontsize=9.0, ha=ha, va="center",
                bbox=dict(boxstyle="square,pad=0.18", facecolor="#fffff8",
                          edgecolor="none"), zorder=9)

    claim(ax, "six wall crossings; four are feasible corners",
          "the lathe, press and two axes give exactly four walls")
    note.set_text("Blue dots are plans. Amber crosses break a resource limit.")
    return save(fig, OUT / "crossings.png", tight=False)


if __name__ == "__main__":
    crossings_still()
