"""Chapter 8: the whole curve, with its bends where they really are.

The value of the workshop as a function of how many planks it has.  Three
straight pieces, each one flatter than the last, joined at two bends.  The
plank price is the slope of the piece you happen to be standing on, which is
why it is a local fact with a range attached rather than a number that is
simply true.

The bends are computed, not eyeballed: 20 planks, where tables drop out of the
plan entirely, and 316/7 planks, where the saw takes over as the binding rule.
Both are re-solved directly and checked against the two lines that meet there,
so a bend drawn in the wrong place would fail rather than look plausible.
"""

from lpduality import workshop as w
from illuminate.draw import (INK, INK2, MUTED, OK, PAPER, PLAN, PRICE, RULE,
                            chapter_dir, figure, heading, save, tag)

OUT = chapter_dir("08-the-price-breaks")


def curve_png():
    segments = w.WOOD_CURVE
    fig, ax = figure(8.4, 4.8)
    fig.subplots_adjust(top=0.82, bottom=0.16)
    heading(ax, "what the workshop is worth, plank by plank")

    for seg in segments:
        xs = [float(seg.start), float(seg.end)]
        ys = [float(seg.value(seg.start)), float(seg.value(seg.end))]
        ax.plot(xs, ys, color=PLAN, linewidth=2.4, zorder=5)
        mid = (xs[0] + xs[1]) / 2
        # the paper is punched out behind each slope label: the first piece is
        # steep enough that a plain offset still leaves the line running
        # through the words
        ax.text(mid + 3.0, float(seg.value((seg.start + seg.end) / 2)) - 34,
                f"${float(seg.slope):.2f} a plank", color=INK2, fontsize=10,
                ha="center", va="top", zorder=6,
                bbox=dict(boxstyle="square,pad=0.28", facecolor=PAPER,
                          edgecolor="none"))

    for seg in segments[:-1]:
        bx = float(seg.end)
        by = float(seg.value(seg.end))
        ax.plot([bx], [by], "o", markersize=7, color=PRICE, zorder=7,
                markeredgecolor=PAPER, markeredgewidth=1.8)
        ax.plot([bx, bx], [0, by], color=PRICE, linewidth=0.9,
                linestyle=(0, (3, 3)), zorder=3)

    here = float(w.PRIMAL.b[w.WOOD])
    ax.plot([here], [float(w.BEST_PROFIT)], "o", markersize=9, color=PLAN,
            zorder=8, markeredgecolor=PAPER, markeredgewidth=2)

    ax.set_xlim(0, 60)
    ax.set_ylim(0, 430)
    ax.set_xlabel("planks in stock", fontsize=10, color=INK2, labelpad=7)
    ax.set_ylabel("best profit", fontsize=10, color=INK2, labelpad=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(True, color=RULE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)
    ax.set_xticks([0, 10, 20, 30, 40, 50, 60])

    ax.annotate("the workshop today\n44 planks, $350", xy=(here, float(w.BEST_PROFIT)),
                xytext=(30.5, 128), color=PLAN, fontsize=10, ha="center",
                bbox=dict(boxstyle="square,pad=0.45", facecolor=PAPER,
                          edgecolor=PLAN, linewidth=1.1),
                arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.9,
                                shrinkA=6, shrinkB=8), zorder=9)
    ax.text(20, 396, "below 20, tables\nare not worth building",
            color=PRICE, fontsize=9.5, ha="center", va="top")
    ax.text(float(w.WOOD_TO) + 1.2, 214,
            "above 45⅐, the saw\nis the binding rule\nand planks are free",
            color=PRICE, fontsize=9.5, ha="left", va="center")
    save(fig, OUT / "curve.png")


if __name__ == "__main__":
    curve_png()
