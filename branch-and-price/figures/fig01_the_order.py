"""Chapter 1: the order, and every way there is to cut one board for it."""

import math

from bandp import mill as m
from illuminate.draw import (INK, INK2, MUTED, PLAN, PRICE, chapter_dir, figure,
                             heading, save, tag)
from boards import board_axes, draw_board

OUT = chapter_dir("01-the-order")


def patterns_png():
    """All six maximal ways to cut a 25-foot board into 4s, 9s and 10s.

    Small enough to print in full, which is the whole reason this is the
    instance the reader learns on.  Chapter 4 is where that stops being true.
    """
    inst = m.BOARDS
    patterns = m.PATTERNS
    fig, ax = figure(7.6, 4.6)
    fig.subplots_adjust(left=0.16, right=0.98, top=0.86, bottom=0.06)
    heading(ax, "every way to cut one board")
    board_axes(ax, inst, rows=len(patterns), row_gap=0.78)

    for k, pattern in enumerate(reversed(patterns)):
        y = k * 0.78
        waste = draw_board(ax, y, pattern, inst, height=0.55,
                           label=inst.describe(pattern))
        ax.text(inst.width + 0.8, y + 0.28, f"{int(waste)} wasted", ha="left",
                va="center", fontsize=8.5, color=MUTED)
    save(fig, OUT / "patterns.png", tight=False)


def order_png():
    """What was ordered, and the one obvious way to fill it."""
    inst = m.BOARDS
    fig, ax = figure(7.6, 2.6)
    fig.subplots_adjust(left=0.16, right=0.98, top=0.80, bottom=0.06)
    heading(ax, "one board, and what has to come out of the pile")
    board_axes(ax, inst, rows=2, row_gap=0.95)

    draw_board(ax, 0.95, tuple([0] * inst.m), inst, height=0.6,
               label="a board", show_waste=False)
    ax.add_patch(__import__("matplotlib").patches.Rectangle(
        (0, 0.95), inst.width, 0.6, facecolor="none", edgecolor=INK,
        linewidth=1.3, zorder=5))
    ax.text(inst.width / 2, 1.25, f"{inst.width} feet", ha="center",
            va="center", fontsize=9.5, color=INK2, zorder=6)

    x = 0.0
    for width, demand in zip(inst.widths, inst.demands):
        ax.text(x, 0.42, f"{demand} × {width}ft", ha="left", va="center",
                fontsize=10, color=PLAN)
        x += 8.2
    ax.text(-0.9, 0.42, "ordered", ha="right", va="center", fontsize=9.5,
            color=INK2)
    save(fig, OUT / "order.png", tight=False)


if __name__ == "__main__":
    order_png()
    patterns_png()
