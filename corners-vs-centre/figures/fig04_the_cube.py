"""Chapter 4: the worst case belongs to the rule, not to the method."""

import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, figure, heading, save, tag)
from twopaths.simplex import (bland, corner_count, dantzig, klee_minty, solve,
                              steepest_edge)

OUT = chapter_dir("04-the-cube")
SIZES = range(1, 11)


def counts():
    rows = []
    for n in SIZES:
        c, A, b = klee_minty(n)
        rows.append((n, corner_count(n),
                     solve(c, A, b, rule=dantzig).steps,
                     solve(c, A, b, rule=bland).steps,
                     solve(c, A, b, rule=steepest_edge).steps))
    return rows


def cube_png():
    rows = counts()
    ns = [r[0] for r in rows]

    fig, ax = figure(8.0, 4.8)
    fig.subplots_adjust(top=0.84, bottom=0.16, left=0.12, right=0.96)
    heading(ax, "pivots taken on the squashed cube")

    ax.semilogy(ns, [r[1] for r in rows], color=TEXT_FAINT, linewidth=1.4,
                linestyle=(0, (4, 3)), zorder=4)
    ax.semilogy(ns, [r[2] for r in rows], color=PRICE, linewidth=2.4, zorder=6,
                marker="o", markersize=5, markeredgecolor=SURFACE, markeredgewidth=1.5)
    ax.semilogy(ns, [r[3] for r in rows], color=PLAN, linewidth=2.2, zorder=5,
                marker="o", markersize=4.5, markeredgecolor=SURFACE, markeredgewidth=1.4)
    ax.semilogy(ns, [max(r[4], 1) for r in rows], color=OK, linewidth=2.2, zorder=5,
                marker="o", markersize=4.5, markeredgecolor=SURFACE, markeredgewidth=1.4)

    ax.set_xlabel("dimensions of the cube", fontsize=10, color=TEXT_DIM, labelpad=6)
    ax.set_ylabel("pivots taken", fontsize=10, color=TEXT_DIM, labelpad=6)
    ax.set_xticks(list(ns))
    ax.set_xlim(0.7, max(ns) + 0.3)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, which="both", color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)

    last = rows[-1]
    tag(ax, 1.25, 260, f"corners the cube has\n(1 to {last[1]:,})",
        color=TEXT_FAINT, size=9)
    tag(ax, 5.9, 2.6, "the greedy rule stops at every corner:\none pivot short of the dashed line",
        color=PRICE, size=9.5)
    tag(ax, 2.6, 78, "the lowest-index rule", color=PLAN, size=9.5)
    tag(ax, 3.6, 1.32, "improvement per unit of movement: one pivot, every time",
        color=OK, size=9.5)
    save(fig, OUT / "cube.png", tight=False)
    return rows


if __name__ == "__main__":
    for n, corners, d, b, s in cube_png():
        print(f"  n={n:>2}  corners {corners:>5}  dantzig {d:>5}  bland {b:>4}  steepest {s:>3}")
