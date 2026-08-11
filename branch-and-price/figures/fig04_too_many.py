"""Chapter 4: the number of patterns, as the order gets more widths."""

from bandp import mill as m
from bandp.cutting import count_patterns
from illuminate.draw import (INK, INK2, MUTED, PAPER, PLAN, PRICE, RULE,
                             chapter_dir, figure, heading, save, tag)

OUT = chapter_dir("04-too-many-to-write-down")


def explosion_png():
    """Patterns against the number of ordered widths, for one real roll size.

    Drawn on a log scale, because on a linear one the whole picture is a flat
    line and then a vertical one, which tells the reader nothing except that
    something happened.
    """
    counts = [count_patterns(m.MILL_ROLL, m.MILL_WIDTHS[:k])
              for k in range(1, len(m.MILL_WIDTHS) + 1)]

    fig, ax = figure(7.8, 4.4)
    fig.subplots_adjust(top=0.84, bottom=0.16, left=0.13, right=0.96)
    heading(ax, "patterns for one 5600mm roll")

    xs = list(range(1, len(counts) + 1))
    ax.plot(xs, counts, color=PLAN, linewidth=2.2, zorder=5)
    ax.plot(xs, counts, "o", color=PLAN, markersize=5, zorder=6,
            markeredgecolor=PAPER, markeredgewidth=1.5)
    ax.set_yscale("log")
    ax.set_xlabel("different widths on the order", fontsize=10, color=INK2, labelpad=7)
    ax.set_ylabel("ways to cut one roll", fontsize=10, color=INK2, labelpad=7)
    ax.set_xticks(xs)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=RULE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)

    ax.annotate(f"{m.thousands(counts[-1])}\nways to cut one roll",
                xy=(xs[-1], counts[-1]), xytext=(3.1, counts[-1] * 0.55),
                color=PRICE, fontsize=10, ha="center",
                bbox=dict(boxstyle="square,pad=0.45", facecolor=PAPER,
                          edgecolor=PRICE, linewidth=1.1),
                arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.9,
                                shrinkA=6, shrinkB=8), zorder=9)
    # the empty paper on this chart is under the curve to the right
    tag(ax, 6.3, 1.1e2,
        "one variable each, and the\nmodel cannot be written down",
        color=INK2, size=9.5)
    save(fig, OUT / "explosion.png", tight=False)


if __name__ == "__main__":
    explosion_png()
