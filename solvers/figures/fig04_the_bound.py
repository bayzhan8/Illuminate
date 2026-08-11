"""Chapter 4: what presolve did to the bound, which is the part that pays.

Nothing here is a cutting plane and nothing here is a search. The whole move
comes from fixing columns and tightening bounds.
"""

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, figure, heading, save, tag)
from solvers import library as L

OUT = chapter_dir("04-what-it-costs")

BEFORE = float(L.SMALL_RELAXATION)              # 248
AFTER = float(L.SMALL_REDUCED_RELAXATION)       # 263
BEST = float(L.SMALL_ANSWER.value)              # 290


def bound_png():
    fig, ax = figure(8.6, 3.5)
    fig.subplots_adjust(left=0.07, right=0.965, bottom=0.28, top=0.74)
    heading(ax, "what the relaxation could prove, before and after")

    lo, hi = 240, 298
    ax.set_xlim(lo, hi)
    ax.set_ylim(0, 1)
    ax.axis("off")

    ax.plot([lo, hi], [0.42, 0.42], color=HAIRLINE, linewidth=1.2, zorder=1)
    for v in range(240, 300, 10):
        ax.plot([v, v], [0.38, 0.42], color=HAIRLINE, linewidth=1.0, zorder=1)
        ax.text(v, 0.28, f"${v}", fontsize=9.5, color=TEXT_FAINT, ha="center")

    # the two bounds, and the answer they are both trying to reach
    ax.plot([BEFORE, BEST], [0.60, 0.60], color=TEXT_FAINT, linewidth=6,
            solid_capstyle="butt", alpha=0.30, zorder=2)
    ax.plot([AFTER, BEST], [0.60, 0.60], color=PLAN, linewidth=6,
            solid_capstyle="butt", alpha=0.55, zorder=3)

    for value, y, colour, label in (
            (BEFORE, 0.60, TEXT_FAINT, "as written"),
            (AFTER, 0.60, PLAN, "after presolve"),
            (BEST, 0.60, PRICE, "the true best plan")):
        ax.plot([value], [0.60], "o", color=colour, markersize=9,
                markeredgecolor=SURFACE, markeredgewidth=2, zorder=6)
        ax.text(value, 0.70, f"${value:.0f}", fontsize=11, color=colour,
                ha="center")
        ax.text(value, 0.80, label, fontsize=9.5, color=colour, ha="center")

    ax.annotate("", xy=(AFTER, 0.50), xytext=(BEFORE, 0.50),
                arrowprops=dict(arrowstyle="->", color=TEXT_DIM, linewidth=1.3))
    ax.text((BEFORE + AFTER) / 2, 0.435,
            f"${AFTER - BEFORE:.0f} of the gap closed with no cut and no search",
            fontsize=10, color=TEXT_DIM, ha="center")

    save(fig, OUT / "bound.png")


if __name__ == "__main__":
    bound_png()
