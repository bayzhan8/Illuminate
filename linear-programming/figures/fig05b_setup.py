"""A loose upper bound makes the setup relaxation too hopeful."""

from fractions import Fraction

from illuminate.draw import (HAIRLINE, PLAN, PRICE, PRICE_FILL, SURFACE,
                             TEXT_DIM, animate, chapter_dir, figure,
                             margin_note)
from linprog.modeling import (SETUP_MOVE_STEPS, setup, setup_bound_at,
                              SETUP_EXAMPLE_COST, SETUP_U_END, SETUP_U_START,
                              setup_relaxation, solve_binary)
from linprog.lp import best_by_enumeration
from scene import Stages, claim

OUT = chapter_dir("05-yes-or-no")
SETUP_COST = SETUP_EXAMPLE_COST
U_START = SETUP_U_START
U_END = SETUP_U_END
STAGES = Stages((SETUP_MOVE_STEPS, 18), (0, 30))
TITLE = "the setup relaxation weakens as U grows"


def one_decimal(value):
    return f"{float(value):.1f}".removesuffix(".0")


def display_fraction(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else (
        f"{value.numerator}/{value.denominator}"
    )


def setup_gif():
    branches = setup(SETUP_COST, U_START)
    true_best = solve_binary(branches)[2]
    plan_at_start = best_by_enumeration(setup_relaxation(SETUP_COST, U_START))[0][:2]
    plan_text = "(" + ", ".join(display_fraction(value) for value in plan_at_start) + ")"
    subtitles = (
        f"increase U; the relaxation's plan remains {plan_text}",
        "",
    )
    fig, ax = figure(7.4, 6.4)
    fig.subplots_adjust(left=0.12, right=0.96, top=0.83, bottom=0.2)
    note = margin_note(fig, y=0.025, size=8.9)
    frames = STAGES.total

    def update(i):
        i = min(i, frames - 1)
        stage, _ = STAGES(i)
        if stage == 0 and i < SETUP_MOVE_STEPS:
            U = setup_bound_at(i)
        else:
            U = U_END
        lp = setup_relaxation(SETUP_COST, U)
        plan, value = best_by_enumeration(lp)
        t, f, z = plan
        assert (t, f) == (8, 12)
        assert z == Fraction(12, 1) / U
        setup_paid = SETUP_COST * z
        gap = value - true_best
        z_display = str(z) if U in (U_START, U_END) else f"{float(z):.2f}"

        ax.clear()
        ax.set_xlim(0, 3.3)
        ax.set_ylim(0, 90)
        ax.set_xticks((0.8, 1.8), ("true best", "relaxation"))
        ax.set_yticks(range(0, 91, 10))
        ax.set_ylabel("thousand roubles", fontsize=10, color=TEXT_DIM, labelpad=7)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.grid(True, axis="y", color=HAIRLINE, linewidth=0.7,
                linestyle=(0, (1, 3)), zorder=0)
        ax.set_axisbelow(True)

        ax.bar(0.8, float(true_best), width=0.45, color=PLAN,
               alpha=0.86, zorder=3)
        ax.bar(1.8, float(value), width=0.45, color=PRICE_FILL,
               edgecolor=PRICE, linewidth=1.7, zorder=3)
        ax.text(0.8, float(true_best) + 1.2, one_decimal(true_best),
                color=PLAN, fontsize=9.2, ha="center", va="bottom")
        ax.text(1.8, float(value) + 1.2, one_decimal(value),
                color=PRICE, fontsize=9.2, ha="center", va="bottom")
        ax.annotate("", xy=(2.18, float(value)), xytext=(2.18, float(true_best)),
                    arrowprops=dict(arrowstyle="<->", color=TEXT_DIM, linewidth=1.2))
        ax.text(2.26, float((value + true_best) / 2), f"gap {one_decimal(gap)}",
                color=TEXT_DIM, fontsize=8.8, ha="left", va="center")

        claim(ax, TITLE, subtitles[stage])
        if i == frames - 1:
            ax.text(0, 1.025,
                    f"at U = {U_END}: relaxation {one_decimal(value)}; "
                    f"true value {one_decimal(true_best)}",
                    transform=ax.transAxes, fontsize=8.8, color=TEXT_DIM,
                    ha="left", va="bottom")
        note.set_text(
            f"U = {one_decimal(U)}   z = 12 ÷ U = {z_display}\n"
            f"setup paid: {one_decimal(SETUP_COST)} × 12 ÷ U = "
            f"{one_decimal(setup_paid)}   value: {one_decimal(value)}"
        )
        return []

    animate(fig, update, frames, OUT / "setup.gif", fps=12, hold=3.0)


if __name__ == "__main__":
    setup_gif()
