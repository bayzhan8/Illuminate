"""A rising shortfall penalty moves the best plan along the lathe wall."""

from fractions import Fraction

from matplotlib.patches import Rectangle

from illuminate.draw import (PLAN, PRICE_FILL, SURFACE, TEXT_DIM, animate,
                             chapter_dir, figure, margin_note, tag)
from linprog import mill as mill
from linprog.lp import best_by_enumeration, vertices
from linprog.modeling import (SHORTFALL_MAX_PENALTY, SHORTFALL_ORDER,
                              shortfall)
from scene import Stages, claim, draw_axes, draw_region, draw_wall, line_where

OUT = chapter_dir("04-more-rows")
TRADE = (Fraction(-2), Fraction(1))
BREAK_Q = -mill.MILL.value(TRADE)
MAX_Q = SHORTFALL_MAX_PENALTY
STAGES = Stages((24, 0), (0, 18), (48, 0), (0, 36))
TITLE = "the order penalty changes the best plan"
SUBTITLES = (
    "raise q to the point where one lost batch of value is exactly repaid",
    "at q = 1, every point on the lathe-wall segment ties",
    "above q = 1, filling the order is worth the lost plywood value",
    "",
)
def progress_fraction(value):
    return Fraction(str(value)).limit_denominator(10000)


def display_number(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else (
        f"{float(value):.1f}".removesuffix(".0")
    )


def penalty_frame(i):
    stage, s = STAGES(i)
    if stage == 0:
        q = BREAK_Q * progress_fraction(s)
    elif stage == 1:
        q = BREAK_Q
    elif stage == 2:
        q = BREAK_Q + (MAX_Q - BREAK_Q) * progress_fraction(s)
    else:
        q = MAX_Q
    if i == STAGES.total - 1:
        q = MAX_Q
    return stage, q


def shortfall_gif():
    fig, ax = figure(7.1, 6.6)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.84, bottom=0.2)
    note = margin_note(fig, y=0.025, size=8.8)

    def update(i):
        i = min(i, STAGES.total - 1)
        stage, q = penalty_frame(i)
        lp = shortfall(q)
        point, kept = best_by_enumeration(lp)
        t, f, u = point
        tied = (q == BREAK_Q)

        ax.clear()
        draw_axes(ax)
        draw_region(ax, alpha=0.09)
        draw_wall(ax, 0, color=TEXT_DIM, lw=1.25)
        draw_wall(ax, 1, color=TEXT_DIM, lw=1.25)
        line_where(ax, (0, 1), SHORTFALL_ORDER, color=TEXT_DIM, linewidth=1.1,
                   dashes=(4, 3), zorder=2)
        tag(ax, 14.5, float(SHORTFALL_ORDER) + 0.55,
            f"order f = {SHORTFALL_ORDER}",
            color=TEXT_DIM, size=8.7)

        if tied:
            ends = sorted({(p[0], p[1]) for p in vertices(lp)
                           if lp.value(p) == kept}, key=lambda p: p[1])
            assert len(ends) == 2
            ax.plot([float(p[0]) for p in ends], [float(p[1]) for p in ends],
                    color=SURFACE, linewidth=8, zorder=5)
            ax.plot([float(p[0]) for p in ends], [float(p[1]) for p in ends],
                    color=PLAN, linewidth=4.8, zorder=6)
            for p in ends:
                ax.plot([float(p[0])], [float(p[1])], "o", color=PLAN,
                        markeredgecolor=SURFACE, markeredgewidth=1.4,
                        markersize=7.5, zorder=7)
            plan_text = f"({ends[0][0]}, {ends[0][1]}) to ({ends[1][0]}, {ends[1][1]}), tied"
            plywood_text = f"{mill.MILL.value(ends[0])} to {mill.MILL.value(ends[1])}"
            penalty_text = (f"{SHORTFALL_ORDER - ends[0][1]} to "
                            f"{SHORTFALL_ORDER - ends[1][1]}")
            kept_text = display_number(kept)
            penalty_amount = q * (SHORTFALL_ORDER - ends[0][1])
        else:
            ax.plot([float(t)], [float(f)], "o", color=PLAN,
                    markeredgecolor=SURFACE, markeredgewidth=1.6,
                    markersize=9, zorder=7)
            tag(ax, float(t) + 0.55, float(f) + 0.55,
                f"({t}, {f})", color=PLAN, size=9.2)
            plan_text = f"({t}, {f})"
            plywood_text = f"{mill.MILL.value((t, f))}"
            penalty_text = display_number(q * u)
            kept_text = display_number(kept)
            penalty_amount = q * u

        max_penalty = BREAK_Q * (SHORTFALL_ORDER - mill.BEST[1])
        bar_start = 0.7
        bar_width = 5.0 * float(penalty_amount / max_penalty) if max_penalty else 0
        ax.add_patch(Rectangle((bar_start, 17.25), 5.0, 0.38,
                               facecolor=SURFACE, edgecolor=TEXT_DIM,
                               linewidth=0.8, zorder=5))
        ax.add_patch(Rectangle((bar_start, 17.25), bar_width, 0.38,
                               facecolor=PRICE_FILL, edgecolor="none", zorder=6))
        ax.text(bar_start, 17.72, f"penalty bar: {display_number(penalty_amount)}",
                color=TEXT_DIM, fontsize=8.2, ha="left", va="bottom",
                bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                          edgecolor="none"), zorder=7)

        claim(ax, TITLE, SUBTITLES[stage])
        if i == STAGES.total - 1:
            ax.text(0, 1.025,
                    f"({t}, {f}), no shortfall; the mill keeps {mill.money(kept)}",
                    transform=ax.transAxes, fontsize=8.8,
                    color=TEXT_DIM, ha="left", va="bottom")
        note.set_text(
            f"q = {display_number(q)}   best plan: {plan_text}\n"
            f"plywood: {plywood_text}   penalty: {penalty_text}   keeps: {kept_text}"
        )
        return []

    animate(fig, update, STAGES.total, OUT / "shortfall.gif", fps=12, hold=3.0)


if __name__ == "__main__":
    shortfall_gif()
