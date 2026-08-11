"""Chapter 6: which rules are actually holding the answer down.

The best plan sits on the planks line and on the hours line, and well clear of
the saw line.  Read the prices next to that picture and the pattern states
itself: the two rules the plan is pressed against carry a price, and the one it
is not pressed against is worth nothing.

Drawn as one figure with the prices written on the lines themselves, because
the claim is about a correspondence, and a correspondence shown as two separate
lists is a claim the reader has to take on trust.
"""

from lpduality import workshop as w
from illuminate.draw import (TEXT, TEXT_DIM, TEXT_FAINT, OK, SURFACE, PLAN, PRICE, chapter_dir,
                            figure, heading, save, tag)
from scene import (callout, draw_axes, draw_constraint, draw_region, mark_plan)

OUT = chapter_dir("06-who-is-binding")


def binding_png():
    fig, ax = figure(8.4, 5.0)
    fig.subplots_adjust(right=0.99)
    draw_axes(ax)
    # a little more room on the right than the other region figures, so the
    # hours label can sit on its own line out where the paper is empty
    ax.set_xlim(0, 13.6)
    heading(ax, "the two rules doing the work, and the one that is not")

    tight = [i for i in range(w.PRIMAL.m) if w.PRIMAL.slack(i, w.PLAN) == 0]
    for i in range(w.PRIMAL.m):
        is_tight = i in tight
        draw_constraint(ax, w.PRIMAL, i, label=False,
                        color=PRICE if is_tight else TEXT_FAINT,
                        lw=2.2 if is_tight else 1.2,
                        dashes=None if is_tight else (5, 4))
    draw_region(ax, w.PRIMAL)
    mark_plan(ax, w.PLAN)

    # each line labelled with its own price, on the line
    for i, (lx, ly) in enumerate(((6.15, 9.05), (12.05, 1.85), (8.5, 6.6))):
        price = w.PRICES[i]
        is_tight = i in tight
        colour = PRICE if is_tight else TEXT_FAINT
        spare = w.PRIMAL.slack(i, w.PLAN)
        text = (f"{w.PRIMAL.row_names[i]}\nnone spare\n{w.money(price)} each"
                if is_tight else
                f"{w.PRIMAL.row_names[i]}\n{w.number(spare)} spare\n{w.money(price)}")
        ax.text(lx, ly, text, color=colour, fontsize=9.5, ha="center",
                va="center", zorder=7,
                bbox=dict(boxstyle="square,pad=0.34", facecolor=SURFACE,
                          edgecolor=colour, linewidth=1.0))

    callout(ax, f"9 tables, 4 chairs\n{w.money(w.BEST_PROFIT)}", w.PLAN,
            at=(3.4, 6.6), color=PLAN)
    tag(ax, 0.35, 1.0,
        "a rule with something left over\ncannot be what is holding you back,\n"
        "so nobody would pay for more of it",
        color=TEXT_DIM, size=10)
    save(fig, OUT / "binding.png")


if __name__ == "__main__":
    binding_png()
