"""Chapter 6: one line for two clerks, and the case where that is wrong."""

import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, figure, heading, save, tag)
from queues import desk as d
from queues.formulas import MM1, MMC

OUT = chapter_dir("06-two-clerks")


def pooling_png():
    import matplotlib.pyplot as plt

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10.0, 4.4),
                                   gridspec_kw={"width_ratios": [1.25, 1]})
    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.16, top=0.84, wspace=0.30)

    # --- left: the gain, across utilisation
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

    # --- right: the counterexample
    heading(axR, "and when it is the wrong answer")
    values = [float(d.DEDICATED), float(d.COMBINED)]
    names = ["a desk for quick jobs\nand a desk for slow ones",
             "one line, one desk\nof double speed"]
    colours = [OK, PRICE]
    ys = [1, 0]
    axR.barh(ys, values, height=0.42, color=colours, zorder=4,
             edgecolor=SURFACE, linewidth=2)
    for y, v, c in zip(ys, values, colours):
        axR.text(v + 0.12, y, f"{v:.2f} hr", va="center", ha="left",
                 fontsize=11, color=c, fontweight="semibold", zorder=6)
    axR.set_yticks(ys)
    axR.set_yticklabels(names, fontsize=9, color=TEXT_DIM)
    axR.set_xlim(0, 7.6)
    axR.set_ylim(-0.55, 1.75)
    axR.set_xlabel("average wait, hours", fontsize=10, color=TEXT_DIM, labelpad=6)
    for side in ("top", "right", "left"):
        axR.spines[side].set_visible(False)
    axR.tick_params(axis="y", length=0)
    axR.grid(True, axis="x", color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    axR.set_axisbelow(True)
    axR.text(0.05, 1.55, "identical total capacity, identical utilisation",
             color=TEXT_FAINT, fontsize=9)
    save(fig, OUT / "pooling.png", tight=False)


if __name__ == "__main__":
    pooling_png()
