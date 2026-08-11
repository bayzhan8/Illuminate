"""Chapter 0: the poster. Two problems, drawn side by side, arriving at one number.

Left is the workshop choosing a plan, pushing its profit up.  Right is a buyer
choosing prices, pushing the bill down.  Neither picture knows about the other
-- different axes, different rules, opposite directions -- and they stop at the
same number anyway.  That is the whole guide in one frame.

The dual has three prices and a page has two axes, so the right-hand panel is
the dual sliced at a saw-time price of zero.  That is not a fudge chosen to fit:
the saw is the row with capacity to spare, and chapter 6 is where the reader
finds out that such a row is worth nothing, which is why the slice passes
through the answer.
"""

from fractions import Fraction

from lpduality import workshop as w
from lpduality.draw import (INK, INK2, MUTED, PAPER, PLAN, PRICE, RULE, animate,
                            chapter_dir, figure, heading, readout, tag)
from lpduality.lp import LP
from scene import clipped_corners, draw_constraint, draw_region, ordered_corners

OUT = chapter_dir("00-what-this-is")

# the dual, with the saw-time price held at zero so it fits on a page
DUAL_SLICE = LP.build(
    c=[44, 30],
    A=[[4, 2], [2, 3]],
    b=[30, 20],
    op=">=",
    sense="min",
    var_names=("price of a plank", "price of an hour"),
    row_names=("a table must not be underpriced",
               "a chair must not be underpriced"),
)

PRIMAL_WINDOW = (0, 12.4, 0, 11.6)
DUAL_WINDOW = (0, 12.4, 0, 16.5)


def hero_gif(frames=54, fps=12):
    import matplotlib.pyplot as plt
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.6, 4.5))
    fig.subplots_adjust(bottom=0.24, wspace=0.28)

    # --- left: the workshop's plans
    axL.set_xlim(*PRIMAL_WINDOW[:2])
    axL.set_ylim(*PRIMAL_WINDOW[2:])
    for spine in ("top", "right"):
        axL.spines[spine].set_visible(False)
    axL.grid(True, color=RULE, linewidth=0.7, linestyle=(0, (1, 3)), zorder=0)
    axL.set_axisbelow(True)
    axL.set_xlabel("tables", fontsize=9.5, color=MUTED, labelpad=5)
    axL.set_ylabel("chairs", fontsize=9.5, color=MUTED, labelpad=5)
    heading(axL, "the workshop picks a plan")
    for i in range(w.PRIMAL.m):
        draw_constraint(axL, w.PRIMAL, i, label=False, color=INK, lw=1.0)
    draw_region(axL, w.PRIMAL, edge=PLAN)
    up_line, = axL.plot([], [], color=PLAN, linewidth=2.0, zorder=5)
    up_dot, = axL.plot([], [], "o", markersize=8, color=PLAN, zorder=7,
                       markeredgecolor=PAPER, markeredgewidth=2)

    # --- right: the buyer's prices
    axR.set_xlim(*DUAL_WINDOW[:2])
    axR.set_ylim(*DUAL_WINDOW[2:])
    for spine in ("top", "right"):
        axR.spines[spine].set_visible(False)
    axR.grid(True, color=RULE, linewidth=0.7, linestyle=(0, (1, 3)), zorder=0)
    axR.set_axisbelow(True)
    axR.set_xlabel("price of a plank", fontsize=9.5, color=MUTED, labelpad=5)
    axR.set_ylabel("price of an hour", fontsize=9.5, color=MUTED, labelpad=5)
    heading(axR, "a buyer picks prices")
    corners = clipped_corners(DUAL_SLICE, DUAL_WINDOW[1], DUAL_WINDOW[3])
    axR.fill([p[0] for p in corners], [p[1] for p in corners],
             color=PRICE, alpha=0.13, zorder=1, linewidth=0)
    axR.plot([p[0] for p in corners] + [corners[0][0]],
             [p[1] for p in corners] + [corners[0][1]],
             color=PRICE, linewidth=1.8, zorder=3)
    for i in range(DUAL_SLICE.m):
        draw_constraint(axR, DUAL_SLICE, i, label=False, color=INK, lw=1.0)
    down_line, = axR.plot([], [], color=PRICE, linewidth=2.0, zorder=5)
    down_dot, = axR.plot([], [], "o", markersize=8, color=PRICE, zorder=7,
                         markeredgecolor=PAPER, markeredgewidth=2)

    floor_txt = readout(fig, x=0.045, size=11.5, color=PLAN)
    ceil_txt = readout(fig, x=0.56, size=11.5, color=PRICE)

    answer = float(w.BEST_PROFIT)
    start_floor, start_ceil = 0.0, 760.0

    def update(i):
        i = min(i, frames - 1)
        t = i / (frames - 1)
        ease = t * t * (3 - 2 * t)
        floor = start_floor + (answer - start_floor) * ease
        ceil = start_ceil + (answer - start_ceil) * ease

        xs = [PRIMAL_WINDOW[0], PRIMAL_WINDOW[1]]
        up_line.set_data(xs, [(floor - 30 * x) / 20 for x in xs])
        xs2 = [DUAL_WINDOW[0], DUAL_WINDOW[1]]
        down_line.set_data(xs2, [(ceil - 44 * x) / 30 for x in xs2])

        done = i == frames - 1
        up_dot.set_data([9.0] if done else [], [4.0] if done else [])
        down_dot.set_data([6.25] if done else [], [2.5] if done else [])
        floor_txt.set_text(f"best plan so far   ${floor:,.0f}"
                           + ("\n9 tables, 4 chairs" if done else "\npush it higher"))
        ceil_txt.set_text(f"cheapest prices so far   ${ceil:,.0f}"
                          + ("\n$6.25 a plank, $2.50 an hour" if done
                             else "\npush it lower"))
        return []

    animate(fig, update, frames, OUT / "hero.gif", fps=fps, hold=3.0)


if __name__ == "__main__":
    hero_gif()
