"""The cheap overtime tier pays for itself; the dear tier spends the gain."""

from fractions import Fraction

from illuminate.draw import (HAIRLINE, PLAN, PLAN_FILL, PRICE, SURFACE,
                             TEXT_DIM, chapter_dir, figure, margin_note, save)
from linprog.modeling import (CHEAP_OVERTIME_PRICE, DEAR_OVERTIME_PRICE,
                              OVERTIME_GAIN_PER_HOUR, OVERTIME_LIMIT,
                              OVERTIME_TIER_WIDTH, overtime_cost)
from scene import claim

OUT = chapter_dir("04-more-rows")


def tiers():
    fig, ax = figure(8.0, 5.8)
    fig.subplots_adjust(left=0.12, right=0.97, top=0.82, bottom=0.2)
    ax.set_xlim(0, float(OVERTIME_LIMIT))
    ax.set_ylim(-float(OVERTIME_LIMIT), 2 * float(OVERTIME_LIMIT) + 2)
    ax.set_xticks(range(0, int(OVERTIME_LIMIT) + 1, 2))
    ax.set_yticks(range(0, 2 * int(OVERTIME_LIMIT) + 1, 4))
    ax.set_xlabel("extra lathe hours u", fontsize=10, color=TEXT_DIM, labelpad=7)
    ax.set_ylabel("thousand roubles", fontsize=10, color=TEXT_DIM, labelpad=7)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)), zorder=0)
    ax.set_axisbelow(True)

    samples = [OVERTIME_LIMIT * Fraction(i, 80) for i in range(81)]
    xs = [float(u) for u in samples]
    intercept = (DEAR_OVERTIME_PRICE - CHEAP_OVERTIME_PRICE) * OVERTIME_TIER_WIDTH
    first_line = [float(CHEAP_OVERTIME_PRICE * u) for u in samples]
    second_line = [float(DEAR_OVERTIME_PRICE * u - intercept) for u in samples]
    cost = [float(overtime_cost(u)) for u in samples]
    value = [float(OVERTIME_GAIN_PER_HOUR * u) for u in samples]
    tier = float(OVERTIME_TIER_WIDTH)
    limit = float(OVERTIME_LIMIT)

    ax.plot(xs, first_line, color=PRICE, linewidth=1.4, dashes=(4, 3),
            alpha=0.8, zorder=2)
    ax.plot(xs, second_line, color=PRICE, linewidth=1.4, dashes=(4, 3),
            alpha=0.8, zorder=2)
    first_indices = [i for i, u in enumerate(samples) if u <= OVERTIME_TIER_WIDTH]
    second_indices = [i for i, u in enumerate(samples) if u >= OVERTIME_TIER_WIDTH]
    ax.plot([xs[i] for i in first_indices], [cost[i] for i in first_indices],
            color=PRICE, linewidth=2.5, zorder=4)
    ax.plot([xs[i] for i in second_indices], [cost[i] for i in second_indices],
            color=PRICE, linewidth=2.5, zorder=4)
    ax.plot(xs, value, color=PLAN, linewidth=2.2, zorder=3)
    ax.fill_between(xs, cost, value, where=[v >= c for v, c in zip(value, cost)],
                    color=PLAN_FILL, alpha=0.45, zorder=1)

    ax.plot([tier], [float(overtime_cost(tier))], "o", color=PRICE,
            markeredgecolor=SURFACE, markeredgewidth=1.6, markersize=7.5, zorder=6)
    net_gain = OVERTIME_GAIN_PER_HOUR * OVERTIME_TIER_WIDTH - overtime_cost(
        OVERTIME_TIER_WIDTH
    )
    ax.annotate("", xy=(tier, float(2 * tier)), xytext=(tier, float(overtime_cost(tier))),
                arrowprops=dict(arrowstyle="<->", color=TEXT_DIM, linewidth=1.2))
    ax.text(tier + 0.25, float((2 * tier + overtime_cost(tier)) / 2),
            f"net gain {net_gain}", color=TEXT_DIM,
            fontsize=9, ha="left", va="center",
            bbox=dict(boxstyle="square,pad=0.16", facecolor=SURFACE, edgecolor="none"))
    ax.plot([limit], [float(overtime_cost(limit))], "o", color=PRICE,
            markeredgecolor=SURFACE, markeredgewidth=1.6, markersize=7.5, zorder=6)
    ax.text(limit - 1.25, float(OVERTIME_GAIN_PER_HOUR * OVERTIME_LIMIT) + 1.0,
            f"value added: {OVERTIME_GAIN_PER_HOUR}u",
            color=PLAN, fontsize=9.0, ha="right", va="bottom",
            bbox=dict(boxstyle="square,pad=0.16", facecolor=SURFACE, edgecolor="none"))
    ax.text(limit - 1.4, float(overtime_cost(limit)) - 1.0, "overtime cost h(u)",
            color=PRICE, fontsize=8.9, ha="right", va="top",
            bbox=dict(boxstyle="square,pad=0.16", facecolor=SURFACE, edgecolor="none"))

    claim(ax, "the first overtime tier pays; the second spends the gain",
          "the rust cost is the higher of its two linear pieces")
    note = margin_note(fig, y=0.025, size=9.2)
    note.set_text(
        f"h(u) = max({CHEAP_OVERTIME_PRICE}u, {DEAR_OVERTIME_PRICE}u − {intercept})"
        f"     value added = {OVERTIME_GAIN_PER_HOUR}u"
    )
    return save(fig, OUT / "tiers.png", tight=False)


if __name__ == "__main__":
    tiers()
