"""Chapter 4: the proof, as three bars and two reasons.

Weak duality is usually written as a line of algebra with a "hence" in the
middle.  It is really two separate observations that happen to point the same
way, and drawing them as three quantities makes the two steps visible as two
different gaps rather than one leap.

Take any plan and any covering set of prices.  Then

    what the plan earns
      <= what those prices charge for the ingredients the plan uses
      <= what those prices charge for everything in the building.

The first step holds because every product is priced at least what it earns.
The second holds because a plan cannot use more of anything than there is.
Neither step knows what the best plan is, which is exactly why the conclusion
applies to all of them at once.
"""

from lpduality import workshop as w
from lpduality.draw import (INK, INK2, MUTED, PAPER, PLAN, PRICE, RULE,
                            chapter_dir, figure, heading, save, tag)

OUT = chapter_dir("04-every-mix-is-a-ceiling")

PLAN_SHOWN = (10, 2)            # a real plan, deliberately not the best one
PRICES_SHOWN = (7, 3, 0)        # real prices, deliberately not the cheapest


def chain_png():
    used = [float(w.PRIMAL.row_value(i, PLAN_SHOWN)) for i in range(w.PRIMAL.m)]
    earns = float(w.PRIMAL.objective(PLAN_SHOWN))
    charged_for_used = sum(p * u for p, u in zip(PRICES_SHOWN, used))
    charged_for_all = sum(p * float(b) for p, b in zip(PRICES_SHOWN, w.PRIMAL.b))

    fig, ax = figure(8.4, 4.0)
    fig.subplots_adjust(left=0.30, right=0.97, bottom=0.16, top=0.80)
    heading(ax, "why no plan can beat the bill")

    labels = ["what this plan earns",
              "what these prices charge\nfor what it uses",
              "what these prices charge\nfor the whole workshop"]
    values = [earns, charged_for_used, charged_for_all]
    colors = [PLAN, INK2, PRICE]

    ys = [2, 1, 0]
    ax.barh(ys, values, height=0.44, color=colors, zorder=4,
            edgecolor=PAPER, linewidth=2)
    for y, v, col in zip(ys, values, colors):
        ax.text(v + 7, y, f"${v:,.0f}", va="center", ha="left", color=col,
                fontsize=11.5, fontweight="semibold", zorder=6)

    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=10, color=INK2)
    ax.set_xlim(0, 660)
    ax.set_ylim(-0.6, 2.9)
    ax.set_xlabel("dollars", fontsize=10, color=INK2, labelpad=7)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(True, axis="x", color=RULE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)

    # the two reasons, each drawn against the gap it explains
    # both arrows share one gutter clear of the longest bar, so the two steps
    # read as a single chain rather than as two unrelated annotations
    gutter = max(values) + 24
    for y_top, y_bot, text in (
            (2, 1, "every product is priced\nat least what it earns"),
            (1, 0, "a plan cannot use more\nof anything than there is")):
        ax.annotate("", xy=(gutter, y_top), xytext=(gutter, y_bot),
                    arrowprops=dict(arrowstyle="<->", color=MUTED, linewidth=1.0))
        ax.text(gutter + 14, (y_top + y_bot) / 2, text, va="center", ha="left",
                color=MUTED, fontsize=9.5)

    tag(ax, 8, 2.66,
        f"a plan: {PLAN_SHOWN[0]} tables and {PLAN_SHOWN[1]} chairs — not the best one\n"
        f"some prices: $7 a plank, $3 an hour, $0 of saw time — not the cheapest",
        color=INK2, size=9.5)
    save(fig, OUT / "chain.png")


if __name__ == "__main__":
    chain_png()
