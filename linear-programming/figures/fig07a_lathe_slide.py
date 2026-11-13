"""The best corner follows the lathe wall, then stops at the press wall."""

from fractions import Fraction

from illuminate.draw import (PLAN, PRICE, SURFACE, TEXT, TEXT_DIM, animate,
                             chapter_dir, figure, margin_note)
from linprog import mill as f
from linprog.lp import best_by_enumeration
from scene import Stages, claim, draw_axes, draw_region, line_where

OUT = chapter_dir("07-one-more")
START = Fraction(16)
END = Fraction(44)
FIRST_BEND = f.MILL.b[1]
SECOND_BEND = f.MILL.b[0]
THIRD_BEND = 2 * f.MILL.b[1]
SPECS = ((0, 8), (16, 6), (24, 20), (16, 6), (12, 0))
RANGES = (
    (START, START),
    (START, FIRST_BEND),
    (FIRST_BEND, SECOND_BEND),
    (SECOND_BEND, THIRD_BEND),
    (THIRD_BEND, END),
)
STAGES = Stages(*SPECS)
TITLE = "the best corner moves until one wall is enough"
SUBTITLES = (
    "the lathe starts short; the press wall stays fixed",
    "up to 20 hours, each extra lathe hour makes one more 3-ply batch",
    "at 32 hours, the next hour is worth 2 thousand roubles",
    "the best corner climbs the fixed press wall",
    "after 40 hours, the corner stays at (0, 20)",
)


def exact_stage(i):
    stage, _ = STAGES(i)
    start = sum(move + pause for move, pause in SPECS[:stage])
    move, pause = SPECS[stage]
    offset = i - start
    if move == 0 or offset >= move:
        return stage, Fraction(1)
    progress = Fraction(offset, move)
    return stage, progress * progress * (3 - 2 * progress)


def lathe_lp(stock):
    return f.MILL.with_b((Fraction(stock), f.MILL.b[1]))


def display(value):
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{float(value):.1f}".rstrip("0").rstrip(".")


def lathe_slide():
    fig, ax = figure(8.0, 6.6)
    fig.subplots_adjust(left=0.1, right=0.96, top=0.81, bottom=0.2)
    note = margin_note(fig, y=0.025, size=9.1)
    frames = STAGES.total
    path = [
        best_by_enumeration(lathe_lp(b))[0]
        for b in range(int(START), int(THIRD_BEND) + 1)
    ]
    path_t = [float(point[0]) for point in path]
    path_f = [float(point[1]) for point in path]

    def update(i):
        i = min(i, frames - 1)
        stage, progress = exact_stage(i)
        if i == frames - 1:
            progress = Fraction(1)
        b = RANGES[stage][0] + (RANGES[stage][1] - RANGES[stage][0]) * progress
        lp = lathe_lp(b)
        point, value = best_by_enumeration(lp)
        _, next_value = best_by_enumeration(lathe_lp(b + 1))
        worth = next_value - value

        ax.clear()
        draw_axes(ax)
        ax.set_ylim(0, 22)
        ax.set_yticks(range(0, 23, 4))
        draw_region(ax, lp, alpha=0.08)
        line_where(ax, f.MILL.A[0], b, color=TEXT, linewidth=1.35, zorder=4)
        line_where(ax, f.MILL.A[1], f.MILL.b[1],
                   color=TEXT, linewidth=1.35, zorder=4)
        ax.plot(path_t, path_f, color=PLAN, linewidth=1.8, alpha=0.68, zorder=5)
        for knot in (path[4], path[16], path[24]):
            ax.plot([float(knot[0])], [float(knot[1])], "o", color=PLAN,
                    markeredgecolor=SURFACE, markeredgewidth=1.2,
                    markersize=6, zorder=7)
        ax.plot([float(point[0])], [float(point[1])], "o", color=PLAN,
                markeredgecolor=SURFACE, markeredgewidth=1.8,
                markersize=9, zorder=8)

        lathe_label_x = max(Fraction(2), min(Fraction(9), b - 36))
        lathe_label_y = (b - lathe_label_x) / 2 - Fraction(4, 5)
        ax.text(float(lathe_label_x), float(lathe_label_y), "lathe wall",
                color=TEXT_DIM, fontsize=8.6, ha="left", va="top", zorder=9,
                bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                          edgecolor="none"))
        ax.text(0.6, 21.15, "press wall", color=TEXT_DIM, fontsize=8.6,
                ha="left", va="center", zorder=9,
                bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                          edgecolor="none"))

        if b == SECOND_BEND:
            ax.text(float(point[0]) + 0.9, float(point[1]) + 0.8,
                    "one more hour: +2", color=PRICE, fontsize=8.8,
                    ha="left", va="bottom", zorder=10,
                    bbox=dict(boxstyle="square,pad=0.18", facecolor=SURFACE,
                              edgecolor="none"))

        if i == frames - 1:
            claim(ax, TITLE)
            ax.text(0, 1.025,
                    f"at b = {b}: extra lathe hours add no value",
                    transform=ax.transAxes, fontsize=8.7, color=TEXT_DIM,
                    ha="left", va="bottom")
        else:
            claim(ax, TITLE, SUBTITLES[stage])
        note.set_text(
            f"lathe hours b = {display(b)}   best plan = "
            f"({display(point[0])}, {display(point[1])})\n"
            f"value = {display(value)} thousand roubles   "
            f"one more hour = +{display(worth)}"
        )
        return []

    animate(fig, update, frames, OUT / "lathe_slide.gif", fps=12, hold=3.0)


if __name__ == "__main__":
    lathe_slide()
