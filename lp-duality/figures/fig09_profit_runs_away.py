"""Chapter 9: profit with nothing to stop it, and what the price side says.

If the rules leave a direction the workshop can travel forever there is no
best plan, and no honest price list either: a ceiling would have to be a
number larger than every plan, and there is no such number.
"""

from fractions import Fraction

from lpduality import workshop as w
from illuminate.draw import (TEXT, TEXT_DIM, TEXT_FAINT, OK, SURFACE, PLAN, PRICE, HAIRLINE,
                            chapter_dir, heading, save, tag)
from lpduality.duality import farkas_certificate, mixture, verify_farkas
from lpduality.lp import solve
from scene import clipped_corners

OUT = chapter_dir("09-profit-runs-away")


def edges_png():
    import matplotlib.pyplot as plt

    fig, axL = plt.subplots(1, 1, figsize=(5.6, 4.6))
    fig.subplots_adjust(left=0.13, right=0.96, bottom=0.14, top=0.86)

    # --- left: nothing stops it
    heading(axL, "profit with nothing to stop it")
    corners = clipped_corners(w.ENDLESS, 11.5, 11.0)
    axL.fill([p[0] for p in corners], [p[1] for p in corners],
             color=PLAN, alpha=0.13, zorder=1, linewidth=0)
    axL.plot([p[0] for p in corners] + [corners[0][0]],
             [p[1] for p in corners] + [corners[0][1]],
             color=PLAN, linewidth=1.6, zorder=3)
    xs = [0, 11.5]
    axL.plot(xs, [2 * x - 10 for x in xs], color=TEXT, linewidth=1.3, zorder=2)
    # three lines of equal profit, each labelled, marching out of the picture
    for level, alpha in ((150, 0.42), (300, 0.66), (450, 0.92)):
        axL.plot(xs, [(level - 30 * x) / 20 for x in xs], color=PRICE,
                 linewidth=1.5, alpha=alpha, zorder=4)
        # put the label where this line meets the edge of the panel: near the
        # top if it leaves through the top, otherwise on the left
        top_x = (level - 20 * 10.3) / 30
        if top_x > 0.4:
            lx, ly = top_x, 10.3
        else:
            lx, ly = 0.3, (level - 30 * 0.3) / 20
        axL.text(lx, ly, f"${level}", color=PRICE, fontsize=9,
                 alpha=alpha, ha="center", va="center", zorder=5,
                 bbox=dict(boxstyle="square,pad=0.18", facecolor=SURFACE,
                           edgecolor="none"))
    axL.annotate("", xy=(9.9, 10.4), xytext=(7.2, 6.3),
                 arrowprops=dict(arrowstyle="-|>", color=PRICE, linewidth=1.8))
    axL.text(6.9, 6.0, "and onwards,\nwith no last line", color=PRICE,
             fontsize=9.5, ha="left", va="top", zorder=6,
             bbox=dict(boxstyle="square,pad=0.25", facecolor=SURFACE,
                       edgecolor="none"))
    axL.set_xlim(0, 11.5)
    axL.set_ylim(0, 11.0)
    axL.set_xlabel("tables", fontsize=10, color=TEXT_DIM, labelpad=6)
    axL.set_ylabel("chairs", fontsize=10, color=TEXT_DIM, labelpad=6)
    for s in ("top", "right"):
        axL.spines[s].set_visible(False)
    axL.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    axL.set_axisbelow(True)
    axL.text(6.4, 1.0, "no best plan\n→ no prices at all", color=TEXT_DIM,
             fontsize=10.5, va="bottom")

    save(fig, OUT / "edges.png", tight=False)


if __name__ == "__main__":
    edges_png()
