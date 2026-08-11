"""Chapter 8: what one shared queue buys, across the whole range of busy."""

import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, figure, heading, save, tag)
from queues import desk as d
from queues.formulas import MM1, MMC

OUT = chapter_dir("09-two-clerks")


def pooling_png():
    import matplotlib.pyplot as plt

    fig, axL = plt.subplots(1, 1, figsize=(7.4, 4.4))
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.16, top=0.84)

    # the gain from pooling, across the whole range of how busy the clerks are
    heading(axL, "one queue for two clerks, against two queues")
    loads = np.linspace(0.05, 0.95, 400)
    gain = []
    for rho in loads:
        rate = 20 * rho                                  # two clerks at 10/hr
        apart = MM1.build(round(rate / 2, 6), 10).time_waiting
        together = MMC.build(round(rate, 6), 10, 2).time_waiting
        gain.append(float(apart / together))
    axL.plot(loads, gain, color=PLAN, linewidth=2.4, zorder=5)
    axL.axhline(2.0, color=TEXT_FAINT, linewidth=1.0, linestyle=(0, (4, 4)), zorder=3)
    axL.text(0.06, 2.06, "never better than 2x once the desk is busy",
             color=TEXT_FAINT, fontsize=9)
    for rho, colour in ((0.45, PRICE), (0.9, PRICE)):
        rate = 20 * rho
        apart = MM1.build(round(rate / 2, 6), 10).time_waiting
        together = MMC.build(round(rate, 6), 10, 2).time_waiting
        g = float(apart / together)
        axL.plot([rho], [g], "o", color=PRICE, markersize=7, zorder=7,
                 markeredgecolor=SURFACE, markeredgewidth=2)
        axL.annotate(f"{rho * 100:.0f}% busy\n{g:.2f}x better",
                     xy=(rho, g), xytext=(rho + 0.02, g + 0.55), fontsize=9.5,
                     color=TEXT_DIM,
                     bbox=dict(boxstyle="square,pad=0.35", facecolor=SURFACE,
                               edgecolor=HAIRLINE, linewidth=1.0),
                     arrowprops=dict(arrowstyle="-", color=TEXT_FAINT,
                                     linewidth=0.9, shrinkA=4, shrinkB=6), zorder=9)
    axL.set_xlim(0, 1.0)
    axL.set_ylim(1.5, 5.2)
    axL.set_xlabel("fraction of the time each clerk is busy", fontsize=10,
                   color=TEXT_DIM, labelpad=6)
    axL.set_ylabel("how many times shorter the wait is", fontsize=10,
                   color=TEXT_DIM, labelpad=6)
    for side in ("top", "right"):
        axL.spines[side].set_visible(False)
    axL.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    axL.set_axisbelow(True)

    save(fig, OUT / "pooling.png", tight=False)


if __name__ == "__main__":
    pooling_png()
