"""Animate a dual-simplex repair of the mill's broken plan."""

from fractions import Fraction as Q
import math

from matplotlib.patches import Polygon

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             WARN, animate, chapter_dir, figure, style)
from linprog.lp import LP, vertices
from linprog.simplex import add_row, dual_simplex

OUT = chapter_dir("16-dual-simplex")
VARIABLES = ("t", "f", "s₁", "s₂", "s₃")
BASE_A = (
    (Q(1), Q(2), Q(1), Q(0)),
    (Q(1), Q(1), Q(0), Q(1)),
)
BASE_B = (Q(32), Q(20))
BASE_C = (Q(3), Q(5), Q(0), Q(0))
START_BASIS = (0, 1)
GLUE_ROW = (Q(2), Q(3), Q(0), Q(0))
GLUE_STOCK = Q(50)
A, B, C, BASIS = add_row(
    BASE_A, BASE_B, BASE_C, START_BASIS, GLUE_ROW, GLUE_STOCK
)
RESULT = dual_simplex(A, B, C, BASIS, max_pivots=10)


def fraction_text(value):
    value = Q(value)
    sign = "−" if value < 0 else ""
    numerator = abs(value.numerator)
    if value.denominator == 1:
        return f"{sign}{numerator}"
    return f"{sign}{numerator}/{value.denominator}"


START = RESULT.steps[0].x[:2]
FINAL = RESULT.x[:2]
START_GLUE = sum((a * x for a, x in zip(GLUE_ROW[:2], START)), Q(0))
FINAL_GLUE = sum((a * x for a, x in zip(GLUE_ROW[:2], FINAL)), Q(0))
START_VALUE = sum((a * x for a, x in zip(BASE_C[:2], START)), Q(0))
FINAL_VALUE = RESULT.value
START_EXCESS = START_GLUE - GLUE_STOCK
RATIO_VALUES = tuple(
    RESULT.steps[0].pivot.ratios[index] for index in (2, 3)
)
PRICE_VECTOR = RESULT.steps[-1].dictionary.y
BILL_TERMS = (
    BASE_B[0] * PRICE_VECTOR[0],
    BASE_B[1] * PRICE_VECTOR[1],
    GLUE_STOCK * PRICE_VECTOR[2],
)
PRICE_BILL_TEXT = (
    f"prices y = ({', '.join(fraction_text(value) for value in PRICE_VECTOR)})"
    f"    bill {' + '.join(fraction_text(value) for value in BILL_TERMS if value)}"
    f" = {fraction_text(sum(BILL_TERMS, Q(0)))}"
)
TITLE = "Keep the prices fair; repair the plan"
SUBTITLES = (
    "the new glue row breaks the old optimum by 2 tonnes",
    "idle press costs 1 per tonne freed, so s₂ enters and s₃ leaves",
    "the plan slides up the lathe wall toward the glue limit",
    "at (4, 14) the plan is feasible and the prices are (1, 0, 1)",
)
START_HOLD = 18
RATIO_HOLD = 18
MOVE_FRAMES = 30
FINAL_HOLD = 24
TOTAL_FRAMES = START_HOLD + RATIO_HOLD + MOVE_FRAMES + FINAL_HOLD
HOLD_INDICES = (
    START_HOLD - 1,
    START_HOLD + RATIO_HOLD - 1,
    START_HOLD + RATIO_HOLD + MOVE_FRAMES - 1,
    TOTAL_FRAMES - 1,
)
LATHE_ROW = (Q(1), Q(2))
PRESS_ROW = (Q(1), Q(1))
GLUE_WALL_ANCHOR = (Q(12), Q(26, 3))
LATHE_WALL_ANCHOR = (Q(2), Q(15))
PRESS_WALL_ANCHOR = (Q(15), Q(5))
START_LABEL_ANCHOR = START
FINAL_LABEL_ANCHOR = FINAL
RATIO_ROW_ANCHORS = ((Q(1, 2), Q(1)), (Q(1, 2), Q(0)))
RATIO_LABEL_ANCHORS = ((Q(9, 20), Q(1)), (Q(1, 4), Q(0)))


def coefficient_text(variable, value):
    value = Q(value)
    if value == 1:
        return variable
    if value.denominator == 1:
        return f"{value.numerator}{variable}"
    if value.numerator == 1:
        return f"{variable}/{value.denominator}"
    return f"({value.numerator}/{value.denominator}){variable}"


def _terms(variables, coefficients):
    text = ""
    for variable, coefficient in zip(variables, coefficients):
        if coefficient == 0:
            continue
        sign = "+" if coefficient > 0 else "−"
        text += f" {sign} {coefficient_text(variable, abs(coefficient))}"
    return text


def basis_text(iteration):
    return f"basis: {', '.join(VARIABLES[i] for i in iteration.basis)}"


def dictionary_text(iteration):
    state = iteration.dictionary
    nonbasic = tuple(index for index in range(len(VARIABLES))
                     if index not in iteration.basis)
    lines = [
        f"{VARIABLES[iteration.basis[row]]} = "
        f"{fraction_text(state.x_B[row])}"
        + _terms(
            tuple(VARIABLES[index] for index in nonbasic),
            tuple(-state.rows[row][index] for index in nonbasic),
        )
        for row in range(len(iteration.basis))
    ]
    lines.append(
        f"z = {fraction_text(iteration.value)}"
        + _terms(
            tuple(VARIABLES[index] for index in nonbasic),
            tuple(state.reduced_costs[index] for index in nonbasic),
        )
    )
    return "\n".join(lines)


def frame_state(index):
    index = max(0, min(index, TOTAL_FRAMES - 1))
    if index < START_HOLD:
        return 0, Q(0)
    index -= START_HOLD
    if index < RATIO_HOLD:
        return 1, Q(0)
    index -= RATIO_HOLD
    if index < MOVE_FRAMES:
        progress = Q(index, max(1, MOVE_FRAMES - 1))
        return 2, progress * progress * (3 - 2 * progress)
    return 3, Q(1)


def point_at(progress):
    progress = Q(progress)
    return tuple(
        START[index] + progress * (FINAL[index] - START[index])
        for index in range(2)
    )


def subtitle_for_frame(index):
    return SUBTITLES[frame_state(index)[0]]


def _region():
    rows = (
        LATHE_ROW, PRESS_ROW, (Q(-1), Q(0)), (Q(0), Q(-1)),
        (Q(2), Q(3)),
    )
    bounds = (Q(32), Q(20), Q(0), Q(0), GLUE_STOCK)
    points = vertices(LP.build(c=(0, 0), A=rows, b=bounds))
    center = (
        sum((point[0] for point in points), Q(0)) / len(points),
        sum((point[1] for point in points), Q(0)) / len(points),
    )
    return tuple(sorted(
        points,
        key=lambda point: math.atan2(
            float(point[1] - center[1]), float(point[0] - center[0])
        ),
    ))


REGION = _region()
START_DICTIONARY = RESULT.steps[0]
FINAL_DICTIONARY = RESULT.steps[-1]


def repair_gif():
    fig, empty_ax = figure(12.0, 6.6)
    fig.delaxes(empty_ax)
    fig.text(0.07, 0.96, TITLE, fontsize=11, color=TEXT,
             fontweight="semibold", ha="left")
    subtitle = fig.text(0.07, 0.90, "", fontsize=8.8, color=TEXT_DIM,
                        ha="left")
    ax = fig.add_axes((0.08, 0.20, 0.43, 0.64))
    ratio_ax = fig.add_axes((0.58, 0.56, 0.37, 0.22))
    panel = fig.add_axes((0.58, 0.15, 0.37, 0.34))
    readout = fig.text(0.08, 0.11, "", fontsize=8.4, color=TEXT,
                       ha="left", family="monospace")

    def update(index):
        stage, progress = frame_state(index)
        point = point_at(progress)
        subtitle.set_text(SUBTITLES[stage])
        ax.clear()
        ratio_ax.clear()
        panel.clear()

        style(ax, xlabel="3-ply batches t", ylabel="5-ply batches f")
        ax.set_xlim(-0.8, 21)
        ax.set_ylim(-0.8, 19)
        ax.set_xticks(range(0, 21, 4))
        ax.set_yticks(range(0, 19, 4))
        ax.set_aspect("equal", adjustable="box")
        coordinates = [(float(t), float(f)) for t, f in REGION]
        ax.add_patch(Polygon(
            coordinates, closed=True, facecolor=PLAN, alpha=0.12,
            edgecolor="none", zorder=1,
        ))
        closed = coordinates + [coordinates[0]]
        ax.plot([t for t, _ in closed], [f for _, f in closed],
                color=PLAN, linewidth=1.0, zorder=2)
        ax.axhline(0, color=TEXT_DIM, linewidth=0.9, zorder=2)
        ax.axvline(0, color=TEXT_DIM, linewidth=0.9, zorder=2)

        for row, bound, color in (
            (LATHE_ROW, Q(32), TEXT_DIM),
            (PRESS_ROW, Q(20), TEXT_DIM),
            ((Q(2), Q(3)), GLUE_STOCK, WARN),
        ):
            t_values = (Q(-1), Q(22))
            f_values = tuple((bound - row[0] * t) / row[1]
                             for t in t_values)
            ax.plot([float(t) for t in t_values],
                    [float(f) for f in f_values], color=color,
                    linewidth=1.15 if color == WARN else 0.95,
                    zorder=3)

        for text, anchor, offset, color in (
            ("lathe wall", LATHE_WALL_ANCHOR, (-26, 8), TEXT_DIM),
            ("press wall", PRESS_WALL_ANCHOR, (8, -12), TEXT_DIM),
            ("glue wall", GLUE_WALL_ANCHOR, (26, 9), WARN),
        ):
            ax.annotate(
                text, xy=tuple(float(value) for value in anchor),
                xytext=offset, textcoords="offset points", color=color,
                fontsize=6.8,
                arrowprops=dict(arrowstyle="-", color=color, linewidth=0.5),
                bbox=dict(boxstyle="square,pad=0.10", facecolor=SURFACE,
                          edgecolor=color, linewidth=0.4),
                zorder=8,
            )

        ax.plot(float(FINAL[0]), float(FINAL[1]), "o",
                color=PLAN, alpha=0.6, markeredgecolor=SURFACE,
                markeredgewidth=1.0, markersize=7.0, zorder=6)
        if stage >= 2:
            ax.annotate(
                "", xy=tuple(float(value) for value in point),
                xytext=tuple(float(value) for value in START),
                arrowprops=dict(arrowstyle="-|>", color=WARN,
                                linewidth=1.7, mutation_scale=11),
                zorder=5,
            )
        current_color = PLAN if stage == 3 else WARN
        ax.plot(float(point[0]), float(point[1]), "o",
                color=current_color, markeredgecolor=SURFACE,
                markeredgewidth=1.2, markersize=8.0, zorder=7)
        ax.annotate(
            f"{fraction_text(START_GLUE)} tonnes of glue,\n"
            f"{fraction_text(START_EXCESS)} over",
            xy=tuple(float(value) for value in START), xytext=(12, 14),
            textcoords="offset points", color=WARN, fontsize=7.0,
            arrowprops=dict(arrowstyle="-", color=WARN, linewidth=0.55),
            bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                      edgecolor=WARN, linewidth=0.45),
            zorder=9,
        )
        if stage == 3:
            ax.annotate(
                f"({fraction_text(FINAL[0])}, {fraction_text(FINAL[1])})",
                xy=tuple(float(value) for value in FINAL), xytext=(-30, -23),
                textcoords="offset points", color=PLAN, fontsize=7.1,
                arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.55),
                bbox=dict(boxstyle="square,pad=0.10", facecolor=SURFACE,
                          edgecolor=PLAN, linewidth=0.4),
                zorder=9,
            )

        ratio_ax.set_xlim(0, 1)
        ratio_ax.set_ylim(-0.55, 1.55)
        ratio_ax.axis("off")
        ratio_ax.text(
            0.0, 1.43, "dual ratio: price per tonne of glue freed",
            color=TEXT_DIM, fontsize=7.4, ha="left", va="top",
        )
        ratio_scale = Q(19, 50) / max(RATIO_VALUES)
        ratio_ax.barh(1, float(RATIO_VALUES[0] * ratio_scale), left=0.02,
                      height=0.28,
                      color=TEXT_DIM, alpha=0.7, zorder=2)
        ratio_ax.barh(0, float(RATIO_VALUES[1] * ratio_scale), left=0.02,
                      height=0.28,
                      color=PLAN, alpha=0.9, zorder=2)
        ratio_ax.text(
            float(RATIO_LABEL_ANCHORS[0][0]), 1,
            f"idle lathe: {fraction_text(RATIO_VALUES[0])} per tonne",
            color=TEXT_DIM, fontsize=7.1,
            ha="left", va="center",
        )
        ratio_ax.text(
            float(RATIO_LABEL_ANCHORS[1][0]), 0,
            f"idle press: {fraction_text(RATIO_VALUES[1])} per tonne "
            "← enters",
            color=PLAN, fontsize=7.1,
            ha="left", va="center",
        )

        panel.axis("off")
        iteration = FINAL_DICTIONARY if stage == 3 else START_DICTIONARY
        panel.text(
            0.0, 0.98, basis_text(iteration),
            transform=panel.transAxes, va="top", fontsize=8.0,
            color=TEXT_DIM, family="monospace",
        )
        panel.text(
            0.0, 0.79, dictionary_text(iteration),
            transform=panel.transAxes, va="top", fontsize=8.8,
            color=TEXT, family="monospace", linespacing=1.45,
            bbox=dict(boxstyle="square,pad=0.4", facecolor=SURFACE,
                      edgecolor=HAIRLINE, linewidth=0.6),
        )
        if stage == 3:
            panel.text(
                0.0, 0.05, PRICE_BILL_TEXT,
                transform=panel.transAxes, va="bottom", fontsize=8.1,
                color=PRICE, family="monospace", fontweight="semibold",
            )

        readout.set_text(
            f"glue {fraction_text(START_GLUE)} → {fraction_text(FINAL_GLUE)}"
            f"     value {fraction_text(START_VALUE)} → "
            f"{fraction_text(FINAL_VALUE)}"
        )
        return []

    animate(fig, update, TOTAL_FRAMES, OUT / "repair.gif", fps=12, hold=3.0,
            preserve_colors=(PLAN, PRICE, WARN))


if __name__ == "__main__":
    repair_gif()
