"""Animate an artificial variable out, then optimize from the true corner."""

from fractions import Fraction as Q
import math

from matplotlib.patches import Polygon, Rectangle

from illuminate.draw import (PLAN, PRICE, SURFACE, TEXT, TEXT_DIM, WARN,
                             animate, chapter_dir, figure, style)
from linprog.lp import LP, vertices
from linprog.simplex import two_phase

OUT = chapter_dir("14-simplex")
VARIABLES = ("t", "f", "s₁", "s₂", "e")
PHASE1_VARIABLES = VARIABLES + ("a",)
A = (
    (Q(1), Q(2), Q(1), Q(0), Q(0)),
    (Q(1), Q(1), Q(0), Q(1), Q(0)),
    (Q(0), Q(1), Q(0), Q(0), Q(-1)),
)
B = (Q(32), Q(20), Q(14))
C = (Q(3), Q(5), Q(0), Q(0), Q(0))
RESULT = two_phase(A, B, C)
PHASE1_POINTS = tuple(step.x[:2] for step in RESULT.phase1.steps)
PHASE2_POINTS = tuple(step.x[:2] for step in RESULT.phase2.steps)
PHASE1_RATIOS = tuple(zip(
    ("lathe", "press", "order"), RESULT.phase1.steps[0].pivot.ratios
))
PHASE2_FIRST_RATIOS = tuple(
    (name, ratio)
    for name, ratio in zip(
        ("lathe", "press", "order"), RESULT.phase2.steps[0].pivot.ratios
    )
    if ratio is not None
)
PHASE2_SECOND_RATIOS = tuple(
    (name, ratio)
    for name, ratio in zip(
        ("order e", "press", "f"), RESULT.phase2.steps[1].pivot.ratios
    )
    if ratio is not None
)
TITLE = "A fake variable finds a feasible corner"
SUBTITLES = (
    "Phase I: the fake plan starts with a = 14",
    "Phase I: f enters; the artificial variable falls to zero",
    "Phase I ends at (0, 14): a = 0",
    "Phase II: restart at (0, 14), value 70",
    "e enters: relax the order, ratios 2 and 6",
    "at (0, 16), value 80",
    "t enters: ratios 4 and 8, the order binds",
    "at (4, 14), value 82; z = 82 − 3s₁ − e",
)
HOLD_FRAMES = 18
MOVE_FRAMES = 18
TOTAL_FRAMES = 5 * HOLD_FRAMES + 3 * MOVE_FRAMES
HOLD_INDICES = (
    HOLD_FRAMES - 1,
    HOLD_FRAMES + MOVE_FRAMES + HOLD_FRAMES - 1,
    2 * HOLD_FRAMES + MOVE_FRAMES + HOLD_FRAMES - 1,
    3 * HOLD_FRAMES + 2 * MOVE_FRAMES + HOLD_FRAMES - 1,
    TOTAL_FRAMES - 1,
)
CORNER_LABEL_ANCHORS = (
    PHASE1_POINTS[0], PHASE1_POINTS[-1],
    PHASE2_POINTS[1], PHASE2_POINTS[-1],
)
ORDER_LABEL_ANCHOR = (Q(4), Q(14))
LATHE_LABEL_ANCHOR = (Q(2), Q(15))
PRESS_LABEL_ANCHOR = (Q(14), Q(6))


def _ease(index, count):
    p = Q(index, max(1, count - 1))
    return p * p * (3 - 2 * p)


def frame_state(index):
    index = max(0, min(index, TOTAL_FRAMES - 1))
    chunks = (HOLD_FRAMES, MOVE_FRAMES, HOLD_FRAMES, HOLD_FRAMES,
              MOVE_FRAMES, HOLD_FRAMES, MOVE_FRAMES, HOLD_FRAMES)
    stage = 0
    for chunk_index, length in enumerate(chunks):
        if index < length:
            if chunk_index in (1, 4, 6):
                return chunk_index, _ease(index, length)
            return chunk_index, Q(0 if chunk_index in (0, 2, 3, 5) else 1)
        index -= length
        stage = chunk_index + 1
    return 7, Q(1)


def subtitle_for_frame(index):
    return SUBTITLES[frame_state(index)[0]]


def _region(rows, bounds):
    points = vertices(LP.build(c=(0, 0), A=rows, b=bounds))
    coords = [(float(t), float(f)) for t, f in points]
    center = (sum(t for t, _ in coords) / len(coords),
              sum(f for _, f in coords) / len(coords))
    return sorted(coords, key=lambda p: math.atan2(p[1] - center[1],
                                                    p[0] - center[0]))


MILL_REGION = _region(
    ((Q(1), Q(2)), (Q(1), Q(1)), (Q(1), Q(0)), (Q(0), Q(1))),
    (Q(32), Q(20), Q(21), Q(20)),
)
ORDER_REGION = _region(
    ((Q(1), Q(2)), (Q(1), Q(1)), (Q(0), Q(-1)),
     (Q(1), Q(0)), (Q(0), Q(1))),
    (Q(32), Q(20), Q(-14), Q(18), Q(20)),
)


def _format(value):
    value = Q(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _terms(variables, coefficients):
    text = ""
    for variable, coefficient in zip(variables, coefficients):
        if coefficient == 0:
            continue
        sign = "+" if coefficient > 0 else "−"
        magnitude = abs(coefficient)
        amount = "" if magnitude == 1 else _format(magnitude)
        text += f" {sign} {amount}{variable}"
    return text


def dictionary_text(iteration, variables, objective):
    state = iteration.dictionary
    basis = iteration.basis
    nonbasic = tuple(index for index in range(len(variables))
                     if index not in basis)
    lines = [
        f"{variables[basis[row]]} = {_format(state.x_B[row])}"
        + _terms(
            tuple(variables[index] for index in nonbasic),
            tuple(-state.rows[row][index] for index in nonbasic),
        )
        for row in range(len(basis))
    ]
    value = sum((objective[basis[row]] * state.x_B[row]
                 for row in range(len(basis))), Q(0))
    lines.append(
        f"z = {_format(value)}"
        + _terms(
            tuple(variables[index] for index in nonbasic),
            tuple(state.reduced_costs[index] for index in nonbasic),
        )
    )
    return "\n".join(lines)


def _phase_data(stage):
    if stage <= 2:
        return RESULT.phase1.steps[0 if stage <= 1 else 1], \
            PHASE1_VARIABLES, (Q(0),) * 5 + (Q(-1),), "PHASE I"
    if stage <= 4:
        return RESULT.phase2.steps[0], VARIABLES, C, "PHASE II"
    if stage <= 6:
        return RESULT.phase2.steps[1], VARIABLES, C, "PHASE II"
    return RESULT.phase2.steps[2], VARIABLES, C, "PHASE II"


def _interpolate(start, end, progress):
    return tuple(start[i] + progress * (end[i] - start[i])
                 for i in range(2))


def _frame_point(stage, progress):
    if stage == 0:
        return PHASE1_POINTS[0], (PHASE1_POINTS[0],)
    if stage == 1:
        point = _interpolate(PHASE1_POINTS[0], PHASE1_POINTS[-1], progress)
        return point, (PHASE1_POINTS[0], point)
    if stage in (2, 3):
        return PHASE1_POINTS[-1], PHASE1_POINTS
    if stage == 4:
        point = _interpolate(PHASE2_POINTS[0], PHASE2_POINTS[1], progress)
        return point, (PHASE2_POINTS[0], point)
    if stage == 5:
        return PHASE2_POINTS[1], PHASE2_POINTS[:2]
    if stage == 6:
        point = _interpolate(PHASE2_POINTS[1], PHASE2_POINTS[2], progress)
        return point, PHASE2_POINTS[:2] + (point,)
    return PHASE2_POINTS[2], PHASE2_POINTS


def phase_gif():
    fig, empty_ax = figure(12.0, 6.2)
    fig.delaxes(empty_ax)
    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.15, top=0.83)
    ax = fig.add_axes((0.08, 0.19, 0.49, 0.61))
    panel = fig.add_axes((0.62, 0.40, 0.34, 0.39))
    ratios = fig.add_axes((0.64, 0.16, 0.30, 0.18))
    fig.text(0.08, 0.96, TITLE, fontsize=11, color=TEXT,
             fontweight="semibold", ha="left")
    subtitle = fig.text(0.08, 0.90, "", fontsize=8.8, color=TEXT_DIM,
                        ha="left")

    def update(index):
        stage, progress = frame_state(index)
        subtitle.set_text(SUBTITLES[stage])
        point, path = _frame_point(stage, progress)
        ax.clear()
        panel.clear()
        ratios.clear()
        style(ax, xlabel="3-ply batches t", ylabel="5-ply batches f")
        ax.set_xlim(-0.8, 21)
        ax.set_ylim(-0.8, 20)
        ax.set_aspect("equal", adjustable="box")
        ax.add_patch(Polygon(MILL_REGION, closed=True, facecolor=PLAN,
                             alpha=0.055, edgecolor="none", zorder=1))
        ax.add_patch(Polygon(ORDER_REGION, closed=True, facecolor=PLAN,
                             alpha=0.13, edgecolor="none", zorder=2))
        ax.plot([0, 21], [16, 5.5], color=TEXT_DIM, linewidth=1.0, zorder=3)
        ax.plot([0, 21], [20, -1], color=TEXT_DIM, linewidth=1.0, zorder=3)
        ax.axhline(14, color=WARN, linewidth=1.7, zorder=4)
        ax.axhline(0, color=TEXT_DIM, linewidth=0.9, zorder=3)
        ax.axvline(0, color=TEXT_DIM, linewidth=0.9, zorder=3)
        ax.annotate(
            "order f = 14", xy=tuple(map(float, ORDER_LABEL_ANCHOR)),
            xytext=(9, -17), textcoords="offset points", color=WARN,
            fontsize=7.2,
            bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                      edgecolor=WARN, linewidth=0.4), zorder=8,
        )
        for anchor, label in ((LATHE_LABEL_ANCHOR, "lathe"),
                              (PRESS_LABEL_ANCHOR, "press")):
            ax.annotate(
                label, xy=tuple(map(float, anchor)), xytext=(7, 5),
                textcoords="offset points", color=TEXT_DIM, fontsize=7.0,
                bbox=dict(boxstyle="square,pad=0.10", facecolor=SURFACE,
                          edgecolor=TEXT_DIM, linewidth=0.4), zorder=8,
            )
        if len(path) > 1:
            ax.plot([float(p[0]) for p in path],
                    [float(p[1]) for p in path], color=PLAN, linewidth=2.0,
                    zorder=5)
        ax.plot([float(point[0])], [float(point[1])], "o", color=PLAN,
                markeredgecolor=SURFACE, markeredgewidth=1.2, markersize=7.5,
                zorder=7)
        label = f"({ _format(point[0]) }, { _format(point[1]) })"
        ax.annotate(
            label, xy=tuple(map(float, point)), xytext=(8, 8),
            textcoords="offset points", color=PLAN, fontsize=7.2,
            bbox=dict(boxstyle="square,pad=0.11", facecolor=SURFACE,
                      edgecolor=PLAN, linewidth=0.4), zorder=9,
        )

        iteration, variables, objective, phase_name = _phase_data(stage)
        panel.axis("off")
        panel.text(0, 1, phase_name, transform=panel.transAxes, va="top",
                   fontsize=9.5, color=TEXT_DIM, family="monospace")
        panel.text(
            0, 0.83, dictionary_text(iteration, variables, objective),
            transform=panel.transAxes, va="top", fontsize=10.5,
            color=PRICE if stage == 7 else TEXT, family="monospace",
            linespacing=1.55,
            bbox=dict(boxstyle="square,pad=0.48", facecolor=SURFACE,
                      edgecolor=PRICE if stage == 7 else TEXT_DIM,
                      linewidth=0.65),
        )
        if stage <= 2:
            artificial = RESULT.phase1.steps[0].x[-1] \
                if stage == 0 else RESULT.phase1.steps[-1].x[-1]
            if stage == 1:
                artificial = Q(14) * (1 - progress)
            panel.text(
                0.02, 0.03, f"fake part: a = {_format(artificial)}",
                transform=panel.transAxes, fontsize=7.8, color=WARN,
            )
        else:
            panel.text(0.02, 0.03, "artificial variable removed",
                       transform=panel.transAxes, fontsize=7.4,
                       color=TEXT_DIM)

        ratios.axis("off")
        if stage in (0, 1):
            values = PHASE1_RATIOS
        elif stage in (3, 4):
            values = PHASE2_FIRST_RATIOS
        elif stage in (5, 6):
            values = PHASE2_SECOND_RATIOS
        else:
            values = ()
        if values:
            ratios.text(0, 1, "ratio test", transform=ratios.transAxes,
                        fontsize=7.3, color=TEXT_DIM, va="top")
            max_value = max(float(value) for _, value in values)
            for row, (name, value) in enumerate(values):
                y = 0.72 - row * 0.30
                ratios.text(0, y, name, transform=ratios.transAxes,
                            va="center", fontsize=7.1, color=TEXT_DIM)
                ratios.add_patch(
                    Rectangle(
                        (0.34, y - 0.07), 0.47 * float(value) / max_value,
                        0.14, transform=ratios.transAxes, color=PLAN, alpha=0.82,
                    )
                )
                ratios.text(0.83, y, _format(value),
                            transform=ratios.transAxes, va="center",
                            fontsize=7.1, color=TEXT)
        return []

    animate(fig, update, TOTAL_FRAMES, OUT / "phase.gif", fps=12, hold=3.0,
            preserve_colors=(WARN, PRICE))


if __name__ == "__main__":
    phase_gif()
