"""Chapter 4: the curve, and what the last sliver of idleness costs."""

import numpy as np

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, figure, heading, save, tag)
from queues import desk as d

OUT = chapter_dir("05-the-wait-explodes")


def explode_png():
    fig, ax = figure(8.4, 4.8)
    fig.subplots_adjust(top=0.84, bottom=0.15, left=0.11, right=0.97)
    heading(ax, "minutes of waiting, against how busy the clerk is")

    grid = np.linspace(0.001, 0.975, 900)
    ax.plot(grid, [float(r / (1 - r)) * 6 for r in grid],
            color=PLAN, linewidth=2.4, zorder=5)

    for rate in (d.RATES[0], d.RATES[3], d.RATES[4]):
        q = d.DESKS[rate]
        rho, wait = float(q.load), float(q.time_waiting) * 60
        if wait > 118:
            continue
        ax.plot([rho], [wait], "o", color=PLAN, markersize=7, zorder=7,
                markeredgecolor=SURFACE, markeredgewidth=2)
        ax.annotate(f"{rho * 100:.0f}% busy\n{wait:.0f} min",
                    xy=(rho, wait), xytext=(rho - 0.16, wait + 26),
                    fontsize=9.5, color=TEXT_DIM, ha="center",
                    bbox=dict(boxstyle="square,pad=0.35", facecolor=SURFACE,
                              edgecolor=HAIRLINE, linewidth=1.0),
                    arrowprops=dict(arrowstyle="-", color=TEXT_FAINT,
                                    linewidth=0.9, shrinkA=4, shrinkB=6),
                    zorder=9)

    ax.axvline(1.0, color=PRICE, linewidth=1.2, linestyle=(0, (4, 4)), zorder=3)
    tag(ax, 0.955, 108, "no idle time left", color=PRICE, size=9.5, ha="right")
    ax.set_xlim(0, 1.03)
    ax.set_ylim(0, 125)
    ax.set_xlabel("fraction of the time the clerk is busy", fontsize=10,
                  color=TEXT_DIM, labelpad=7)
    ax.set_ylabel("average wait, minutes", fontsize=10, color=TEXT_DIM, labelpad=7)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)
    tag(ax, 0.06, 92,
        "the curve is the service time\nmultiplied by 1/(idle fraction).\n"
        "selling the last of the idleness\nsells what was absorbing\nthe variability.",
        color=TEXT_DIM, size=9.5)
    save(fig, OUT / "explode.png", tight=False)


if __name__ == "__main__":
    explode_png()
