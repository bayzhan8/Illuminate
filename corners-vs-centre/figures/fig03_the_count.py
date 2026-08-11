"""How many corners there are to check, against how many anybody checks.

The gap between these two curves is the thing that needed explaining for
thirty years. Counting corners is a combinatorics exercise anyone can do on
the back of an envelope, and the number it produces is hopeless. Counting the
hops an actual solve takes gives a number so small that the first curve looks
like a mistake.
"""

from math import comb

import numpy as np

from illuminate.draw import (PLAN, PRICE, SURFACE, TEXT, TEXT_DIM, chapter_dir,
                             figure, heading, save, style, tag)

OUT = chapter_dir("03-it-should-have-been-slow")

SIZES = np.arange(2, 31)


def corner_bound(n, rules_per_variable=2):
    """Choose n of the m rules and solve them as equations: that is a corner.

    An upper bound, not a count -- some choices give a point outside the
    region, and some give no point at all. It is the size of the search a
    method that enumerated corners would face.
    """
    return comb(rules_per_variable * n, n)


def observed(n, rules_per_variable=2):
    """The rule of thumb from decades of practice: a small multiple of the
    number of rules. Drawn as a band rather than a line, because it is an
    observation about the problems people bring, not a theorem."""
    return rules_per_variable * n


def count_png():
    corners = np.array([float(corner_bound(int(n))) for n in SIZES])
    low = np.array([2.0 * observed(int(n)) for n in SIZES])
    high = np.array([4.0 * observed(int(n)) for n in SIZES])

    fig, ax = figure(7.6, 5.0)
    fig.subplots_adjust(top=0.85, bottom=0.15, left=0.13, right=0.96)
    heading(ax, "corners to search, against hops actually taken")
    style(ax, "variables in the problem", "count (log scale)")
    ax.set_yscale("log")

    ax.plot(SIZES, corners, color=PRICE, linewidth=2.2, zorder=5)
    ax.fill_between(SIZES, low, high, color=PLAN, alpha=0.18, zorder=4,
                    linewidth=0)
    ax.plot(SIZES, (low + high) / 2, color=PLAN, linewidth=2.0, zorder=5)

    ax.set_ylim(1, 1e18)
    tag(ax, 13.2, 2.5e13, "corners a search would have to consider",
        color=PRICE, size=10.5)
    tag(ax, 3.4, 6e3, "hops a solve is observed to take\n"
        "(a rule of thumb, not a measurement:\n"
        "two to four times the number of rules)", color=PLAN, size=10)

    biggest = corner_bound(int(SIZES[-1]))
    ax.annotate(f"{SIZES[-1]} variables: around 10$^{{{len(str(biggest)) - 1}}}$ "
                f"corners,\nand roughly {int((low[-1] + high[-1]) / 2)} hops",
                xy=(SIZES[-1], corners[-1]), xytext=(19.0, 8e2),
                fontsize=9.5, color=TEXT_DIM, ha="left",
                arrowprops=dict(arrowstyle="-", color=TEXT_DIM, linewidth=0.8,
                                shrinkA=3, shrinkB=5), zorder=9)
    save(fig, OUT / "the-count.png", tight=False)


if __name__ == "__main__":
    count_png()
