"""Chapter 5: same clerk, same speed, same utilisation, thirteen times the wait."""

import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, figure, heading, save, tag)
from queues import desk as d

OUT = chapter_dir("06-variance-not-utilisation")


def variance_png():
    import matplotlib.pyplot as plt

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10.0, 4.5),
                                   gridspec_kw={"width_ratios": [1.15, 1]})
    fig.subplots_adjust(left=0.20, right=0.97, bottom=0.16, top=0.84, wspace=0.42)

    # --- left: the ladder, at a fixed ninety percent busy
    heading(axL, "at 90% busy, only the spread changes")
    labels = ["exactly 6 min\nevery time", "mildly\nvariable",
              "exponential\n(the textbook)", "some much\nlonger",
              "a few enormously\nlonger"]
    waits = [float(w) * 60 for _, w, _ in d.LADDER]
    ys = list(range(len(waits)))[::-1]
    axL.barh(ys, waits, height=0.5, color=PLAN, zorder=4,
             edgecolor=SURFACE, linewidth=2)
    for y, w in zip(ys, waits):
        axL.text(w + 14, y, (f"{w:.0f} min" if w == int(w) else f"{w:.1f} min"),
                 va="center", ha="left",
                 fontsize=10, color=TEXT_DIM, zorder=6)
    axL.set_yticks(ys)
    axL.set_yticklabels(labels, fontsize=9, color=TEXT_DIM)
    axL.set_xlim(0, 830)
    axL.set_xlabel("average wait, minutes", fontsize=10, color=TEXT_DIM, labelpad=6)
    for side in ("top", "right", "left"):
        axL.spines[side].set_visible(False)
    axL.tick_params(axis="y", length=0)
    axL.grid(True, axis="x", color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    axL.set_axisbelow(True)

    # --- right: the two curves, one exactly half the other
    heading(axR, "constant service halves it, everywhere")
    grid = np.linspace(0.02, 0.955, 600)
    axR.plot(grid, [float(r / (1 - r)) * 6 for r in grid], color=PLAN,
             linewidth=2.3, zorder=5)
    axR.plot(grid, [float(r / (1 - r)) * 3 for r in grid], color=PRICE,
             linewidth=2.3, zorder=5)
    axR.set_xlim(0, 1.0)
    axR.set_ylim(0, 125)
    axR.set_xlabel("fraction of the time busy", fontsize=10, color=TEXT_DIM, labelpad=6)
    axR.set_ylabel("average wait, minutes", fontsize=10, color=TEXT_DIM, labelpad=6)
    for side in ("top", "right"):
        axR.spines[side].set_visible(False)
    axR.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    axR.set_axisbelow(True)
    axR.text(0.40, 96, "service time varies", color=PLAN, fontsize=9.5)
    axR.text(0.52, 34, "service time constant", color=PRICE, fontsize=9.5)
    for rho, wait, colour in ((0.9, 54, PLAN), (0.9, 27, PRICE)):
        axR.plot([rho], [wait], "o", color=colour, markersize=6.5, zorder=7,
                 markeredgecolor=SURFACE, markeredgewidth=1.8)
    axR.annotate("", xy=(0.9, 54), xytext=(0.9, 27),
                 arrowprops=dict(arrowstyle="<->", color=TEXT_FAINT, linewidth=1.0))
    axR.text(0.86, 40, "half", color=TEXT_DIM, fontsize=9.5, ha="right")
    save(fig, OUT / "variance.png", tight=False)


if __name__ == "__main__":
    variance_png()
