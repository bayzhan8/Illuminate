"""Chapter 9: the arrangement that loses, at identical capacity and load.

Same clerks, same total work, same utilisation. The only thing that differs
is whether a one-hour job can end up queueing behind a ten-hour one.
"""

from illuminate.draw import (HAIRLINE, OK, PRICE, SURFACE, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, heading, save)
from queues import desk as d

OUT = chapter_dir("10-when-pooling-loses")


def dedicated_png():
    import matplotlib.pyplot as plt

    fig, axR = plt.subplots(1, 1, figsize=(6.6, 4.0))
    fig.subplots_adjust(left=0.34, right=0.95, bottom=0.18, top=0.82)

    # same clerks, same total capacity, same utilisation; only the arrangement
    heading(axR, "when pooling is the wrong answer")
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
    save(fig, OUT / "dedicated.png", tight=False)


if __name__ == "__main__":
    dedicated_png()
