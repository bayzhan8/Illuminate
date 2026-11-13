"""Animate a bounded-variable simplex flip and pivot in the plywood mill."""

from fractions import Fraction as Q
import math

from matplotlib.patches import Polygon

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             WARN, animate, chapter_dir, figure, style)
from linprog.lp import LP, vertices
from linprog.simplex import bounded_simplex, dictionary

OUT = chapter_dir("18-bounds")
VARIABLES = ("t", "f", "s₁", "s₂")
MILL_A = (
    (Q(1), Q(2), Q(1), Q(0)),
    (Q(1), Q(1), Q(0), Q(1)),
)
MILL_B = (Q(32), Q(20))
MILL_C = (Q(3), Q(5), Q(0), Q(0))
LOWER = (Q(0),) * 4
UPPER = (None, Q(10), None, None)
BASIS = (2, 3)
RESULT = bounded_simplex(
    MILL_A, MILL_B, MILL_C, LOWER, UPPER, BASIS, max_pivots=10
)
START_STEP = RESULT.steps[0]
FLIP_STEP = RESULT.steps[1]
START_POINT = START_STEP.x[:2]
FLIP_POINT = FLIP_STEP.x[:2]
FINAL_POINT = RESULT.x[:2]


def _dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Q(0))


def fraction_text(value):
    value = Q(value)
    sign = "−" if value < 0 else ""
    numerator = abs(value.numerator)
    if value.denominator == 1:
        return f"{sign}{numerator}"
    return f"{sign}{numerator}/{value.denominator}"


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


def _transition_point(step):
    state = dictionary(MILL_A, MILL_B, MILL_C, step.basis)
    theta = min(step.limits.values())
    point = list(step.x)
    point[step.entering] += theta * step.direction
    for row, basic in enumerate(step.basis):
        point[basic] -= (
            theta * step.direction * state.rows[row][step.entering]
        )
    return tuple(point)


FLIP_TARGET = _transition_point(START_STEP)
FINAL_TARGET = _transition_point(FLIP_STEP)
assert FLIP_TARGET[:2] == FLIP_POINT
assert FINAL_TARGET[:2] == FINAL_POINT

_LIMITS = START_STEP.limits
LIMITS = (
    _LIMITS["basic x_2 lower"],
    _LIMITS["basic x_3 lower"],
    _LIMITS["entering x_1 own bound"],
)
TITLE = "A bound can flip without a row"
SUBTITLES = (
    "start at (0, 0), with 5-ply rising from its floor",
    "lathe, press and ceiling limits compete as f rises",
    "bound flip: no basis change, basis still s₁, s₂",
    "the plan runs along the cap until the press wall goes tight",
    "at (10, 10), the press costs 3 and the cap costs 2",
)
START_HOLD = 15
FLIP_MOVE_FRAMES = 24
FLIP_HOLD = 18
CAP_MOVE_FRAMES = 30
FINAL_HOLD = 24
TOTAL_FRAMES = (
    START_HOLD + FLIP_MOVE_FRAMES + FLIP_HOLD
    + CAP_MOVE_FRAMES + FINAL_HOLD
)
HOLD_INDICES = (
    START_HOLD - 1,
    START_HOLD + FLIP_MOVE_FRAMES + FLIP_HOLD - 1,
    TOTAL_FRAMES - 1,
)
LIMIT_LABELS = ("lathe", "press", "own ceiling")
FINAL_PRICE_VECTOR = RESULT.y
CAP_PRICE = dictionary(
    MILL_A, MILL_B, MILL_C, RESULT.basis
).reduced_costs[1]
FINAL_BILL = (
    MILL_B[0] * FINAL_PRICE_VECTOR[0]
    + MILL_B[1] * FINAL_PRICE_VECTOR[1]
    + UPPER[1] * CAP_PRICE
)
FINAL_PRICE_TEXT = (
    f"press {fraction_text(FINAL_PRICE_VECTOR[1])}, "
    f"cap {fraction_text(CAP_PRICE)}, bill {fraction_text(FINAL_BILL)}"
)
REGION_ROWS = (
    (Q(1), Q(2)), (Q(1), Q(1)), (Q(0), Q(1)),
    (Q(-1), Q(0)), (Q(0), Q(-1)),
)
REGION_BOUNDS = (Q(32), Q(20), UPPER[1], Q(0), Q(0))
START_LABEL_ANCHOR = START_POINT
FLIP_LABEL_ANCHOR = FLIP_POINT
FINAL_LABEL_ANCHOR = FINAL_POINT
LATHE_WALL_ANCHOR = (Q(8), Q(12))
PRESS_WALL_ANCHOR = (Q(12), Q(8))
CAP_LINE_ANCHOR = (Q(15), Q(10))
LIMIT_BAR_ANCHORS = ((Q(0), Q(2)), (Q(0), Q(1)), (Q(0), Q(0)))


def _region():
    points = vertices(LP.build(c=(0, 0), A=REGION_ROWS, b=REGION_BOUNDS))
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


def frame_state(index):
    index = max(0, min(index, TOTAL_FRAMES - 1))
    if index < START_HOLD:
        return 0, Q(0)
    index -= START_HOLD
    if index < FLIP_MOVE_FRAMES:
        return 1, Q(index, max(1, FLIP_MOVE_FRAMES - 1))
    index -= FLIP_MOVE_FRAMES
    if index < FLIP_HOLD:
        return 2, Q(1)
    index -= FLIP_HOLD
    if index < CAP_MOVE_FRAMES:
        return 3, Q(index, max(1, CAP_MOVE_FRAMES - 1))
    return 4, Q(1)


def subtitle_for_frame(index):
    return SUBTITLES[frame_state(index)[0]]


def point_at(index):
    stage, progress = frame_state(index)
    if stage == 0:
        return START_POINT
    if stage in {1, 2}:
        start, end = START_POINT, FLIP_POINT
    elif stage in {3, 4}:
        start, end = FLIP_POINT, FINAL_POINT
    return tuple(
        start[column] + progress * (end[column] - start[column])
        for column in range(2)
    )


def _state_dictionary(basis, at_upper, point):
    state = dictionary(MILL_A, MILL_B, MILL_C, basis)
    basis_set = set(basis)
    nonbasic = tuple(
        column for column in range(len(VARIABLES))
        if column not in basis_set and column not in at_upper
    ) + tuple(
        column for column in range(len(VARIABLES))
        if column not in basis_set and column in at_upper
    )
    constant = tuple(
        state.x_B[row] - sum(
            (state.rows[row][column] * point[column]
             for column in nonbasic),
            Q(0),
        )
        for row in range(len(basis))
    )
    lines = []
    for basic in sorted(basis):
        row = basis.index(basic)
        variables = tuple(
            "f̄" if column in at_upper and column == 1
            else VARIABLES[column]
            for column in nonbasic
        )
        coefficients = tuple(
            state.rows[row][column] if column in at_upper
            else -state.rows[row][column]
            for column in nonbasic
        )
        lines.append(
            f"{VARIABLES[basic]} = {fraction_text(constant[row])}"
            + _terms(variables, coefficients)
        )
    objective_constant = (
        sum((MILL_C[basis[row]] * state.x_B[row]
             for row in range(len(basis))), Q(0))
        + sum((state.reduced_costs[column] * point[column]
               for column in nonbasic), Q(0))
    )
    objective_variables = tuple(
        "f̄" if column in at_upper and column == 1
        else VARIABLES[column]
        for column in nonbasic
    )
    objective_coefficients = tuple(
        -state.reduced_costs[column] if column in at_upper
        else state.reduced_costs[column]
        for column in nonbasic
    )
    lines.append(
        f"z = {fraction_text(objective_constant)}"
        + _terms(objective_variables, objective_coefficients)
    )
    return "\n".join(lines)


def dictionary_text(stage):
    if stage in {"start", 0, 1}:
        return _state_dictionary(
            START_STEP.basis, START_STEP.at_upper, START_STEP.x
        )
    if stage in {"flip", 2}:
        return _state_dictionary(
            FLIP_STEP.basis, FLIP_STEP.at_upper, FLIP_STEP.x
        )
    return _state_dictionary(RESULT.basis, RESULT.at_upper, RESULT.x)


START_DICTIONARY_TEXT = dictionary_text("start")
FLIP_DICTIONARY_TEXT = dictionary_text("flip")
FINAL_DICTIONARY_TEXT = dictionary_text("final")


def _plot_region(ax, point, stage):
    style(ax, xlabel="3-ply batches t", ylabel="5-ply batches f")
    ax.set_xlim(-0.8, 21)
    ax.set_ylim(-0.8, 18)
    ax.set_xticks(range(0, 21, 4))
    ax.set_yticks(range(0, 19, 2))
    ax.set_aspect("equal", adjustable="box")
    coordinates = [(float(t), float(f)) for t, f in REGION]
    ax.add_patch(Polygon(
        coordinates, closed=True, facecolor=PLAN, alpha=0.12,
        edgecolor="none", zorder=1,
    ))
    closed = coordinates + [coordinates[0]]
    ax.plot([t for t, _ in closed], [f for _, f in closed],
            color=PLAN, linewidth=1.0, zorder=2)
    ax.plot((0, 21), (16, 11.5), color=TEXT_DIM, linewidth=1.0, zorder=3)
    ax.plot((2, 20), (18, 0), color=TEXT_DIM, linewidth=1.0, zorder=3)
    ax.plot((0, 20), (10, 10), color=TEXT_DIM, linewidth=1.05,
            linestyle=(0, (4, 2)), zorder=3)
    ax.axhline(0, color=TEXT_DIM, linewidth=0.8, zorder=2)
    ax.axvline(0, color=TEXT_DIM, linewidth=0.8, zorder=2)
    ax.annotate(
        "lathe: t + 2f = 32",
        xy=tuple(map(float, LATHE_WALL_ANCHOR)), xytext=(-48, 8),
        textcoords="offset points", color=TEXT_DIM, fontsize=6.7,
        arrowprops=dict(arrowstyle="-", color=TEXT_DIM, linewidth=0.45),
    )
    ax.annotate(
        "press: t + f = 20",
        xy=tuple(map(float, PRESS_WALL_ANCHOR)), xytext=(9, -14),
        textcoords="offset points", color=TEXT_DIM, fontsize=6.7,
        arrowprops=dict(arrowstyle="-", color=TEXT_DIM, linewidth=0.45),
    )
    ax.annotate(
        "cap f = 10", xy=tuple(map(float, CAP_LINE_ANCHOR)),
        xytext=(8, -17),
        textcoords="offset points", color=TEXT_DIM, fontsize=6.7,
        arrowprops=dict(arrowstyle="-", color=TEXT_DIM, linewidth=0.45),
    )
    ax.plot(float(FINAL_POINT[0]), float(FINAL_POINT[1]), "o",
            color=PLAN, alpha=0.5, markeredgecolor=SURFACE,
            markeredgewidth=0.8, markersize=6.5, zorder=5)
    if stage in {1, 2}:
        start = START_POINT
    elif stage in {3, 4}:
        start = FLIP_POINT
    else:
        start = point
    if point != start:
        ax.annotate(
            "", xy=tuple(float(value) for value in point),
            xytext=tuple(float(value) for value in start),
            arrowprops=dict(arrowstyle="-|>", color=PLAN, linewidth=1.7,
                            mutation_scale=10),
            zorder=6,
        )
    ax.plot(float(point[0]), float(point[1]), "o", color=PLAN,
            markeredgecolor=SURFACE, markeredgewidth=1.2,
            markersize=7.5, zorder=7)
    if stage == 0:
        ax.annotate(
            "start (0, 0)", xy=tuple(map(float, START_LABEL_ANCHOR)),
            xytext=(10, 10), textcoords="offset points", color=PLAN,
            fontsize=6.8,
            arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.5),
            bbox=dict(boxstyle="square,pad=0.1", facecolor=SURFACE,
                      edgecolor=PLAN, linewidth=0.35),
            zorder=8,
        )
    if stage == 2:
        ax.annotate(
            "(0, 10)", xy=tuple(map(float, FLIP_LABEL_ANCHOR)), xytext=(10, 10),
            textcoords="offset points", color=PLAN, fontsize=6.8,
            arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.5),
            bbox=dict(boxstyle="square,pad=0.1", facecolor=SURFACE,
                      edgecolor=PLAN, linewidth=0.35),
            zorder=8,
        )
    if stage == 4:
        ax.annotate(
            "(10, 10)", xy=tuple(map(float, FINAL_LABEL_ANCHOR)),
            xytext=(9, -17),
            textcoords="offset points", color=PLAN, fontsize=6.8,
            arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.5),
            bbox=dict(boxstyle="square,pad=0.1", facecolor=SURFACE,
                      edgecolor=PLAN, linewidth=0.35),
            zorder=8,
        )


def flip_gif():
    fig, empty_ax = figure(12.0, 6.6)
    fig.delaxes(empty_ax)
    fig.text(0.07, 0.96, TITLE, fontsize=11, color=TEXT,
             fontweight="semibold", ha="left")
    subtitle = fig.text(0.07, 0.90, "", fontsize=8.8, color=TEXT_DIM,
                        ha="left")
    ax = fig.add_axes((0.08, 0.20, 0.43, 0.64))
    ratio_ax = fig.add_axes((0.57, 0.56, 0.37, 0.29))
    panel = fig.add_axes((0.57, 0.14, 0.37, 0.34))
    readout = fig.text(0.08, 0.10, "", fontsize=8.2, color=TEXT,
                       ha="left", family="monospace")

    def update(index):
        stage, progress = frame_state(index)
        point = point_at(index)
        subtitle.set_text(SUBTITLES[stage])
        ax.clear()
        ratio_ax.clear()
        panel.clear()
        _plot_region(ax, point, stage)

        ratio_ax.set_xlim(0, 1.6)
        ratio_ax.set_ylim(-0.7, 3.4)
        ratio_ax.axis("off")
        if stage <= 2:
            ratio_ax.text(
                0.0, 3.25, "first step: distance to each limit",
                color=TEXT_DIM, fontsize=7.4, ha="left", va="top",
            )
            for row, (label, limit, color) in enumerate(zip(
                    LIMIT_LABELS, LIMITS, (TEXT_DIM, TEXT_DIM, PLAN))):
                y = 2 - row
                ratio_ax.text(
                    0.0, y, label, color=color, fontsize=7.1,
                    ha="left", va="center",
                )
                ratio_ax.barh(
                    y, float(limit / max(LIMITS) * Q(9, 20)),
                    left=Q(13, 20), height=0.28, color=color,
                    alpha=0.78, zorder=2,
                )
                ratio_ax.text(
                    1.18, y, fraction_text(limit), color=color,
                    fontsize=7.1, ha="right", va="center",
                )
                if row == 2:
                    ratio_ax.text(
                        1.25, y, "← flips", color=PLAN,
                        fontsize=7.1, ha="left", va="center",
                    )

        panel.axis("off")
        if stage in {0, 1}:
            panel_dictionary = START_DICTIONARY_TEXT
        elif stage == 2:
            panel_dictionary = FLIP_DICTIONARY_TEXT
        else:
            panel_dictionary = FINAL_DICTIONARY_TEXT
        panel.text(
            0.0, 0.98, "dictionary",
            transform=panel.transAxes, va="top", fontsize=7.8,
            color=TEXT_DIM,
        )
        panel.text(
            0.0, 0.83, panel_dictionary,
            transform=panel.transAxes, va="top", fontsize=8.5,
            color=TEXT, family="monospace", linespacing=1.4,
            bbox=dict(boxstyle="square,pad=0.35", facecolor=SURFACE,
                      edgecolor=HAIRLINE, linewidth=0.6),
        )
        if stage == 4:
            panel.text(
                0.0, 0.04, FINAL_PRICE_TEXT,
                transform=panel.transAxes, va="bottom", fontsize=8.0,
                color=PRICE, family="monospace", fontweight="semibold",
            )

        value = _dot(MILL_C[:2], point)
        readout.set_text(
            f"plan = ({fraction_text(point[0])}, "
            f"{fraction_text(point[1])})"
            f"     value = {fraction_text(value)}"
        )
        return []

    animate(fig, update, TOTAL_FRAMES, OUT / "flip.gif", fps=12, hold=3.0,
            preserve_colors=(PLAN, PRICE, WARN))


if __name__ == "__main__":
    flip_gif()
