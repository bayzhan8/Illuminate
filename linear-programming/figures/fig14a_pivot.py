"""Animate the mill's two exact simplex pivots."""

from fractions import Fraction as Q
import math

from matplotlib.patches import Polygon

from illuminate.draw import (PLAN, PRICE, SURFACE, TEXT, TEXT_DIM, animate,
                             chapter_dir, figure, style)
from linprog.lp import LP, vertices
from linprog.simplex import simplex

OUT = chapter_dir("14-simplex")
VARIABLES = ("t", "f", "s₁", "s₂")
MILL_A = ((Q(1), Q(2), Q(1), Q(0)),
          (Q(1), Q(1), Q(0), Q(1)))
MILL_B = (Q(32), Q(20))
MILL_C = (Q(3), Q(5), Q(0), Q(0))
START_BASIS = (2, 3)
WALK = simplex(MILL_A, MILL_B, MILL_C, START_BASIS)
POINTS = tuple(step.x[:2] for step in WALK.steps)
START, MIDDLE, FINAL = POINTS
FIRST_PIVOT, SECOND_PIVOT = (
    WALK.steps[0].pivot, WALK.steps[1].pivot
)
TITLE = "Each pivot trades one tight row for another"
SUBTITLES = (
    "start at (0, 0): f has the largest reduced cost, +5",
    "f enters; the ratio test stops at the lathe wall",
    "at (0, 16), t earns +1/2 along the lathe wall",
    "t enters; the press runs out first",
    "at (8, 12), both reduced costs are non-positive",
)
HOLD_FRAMES = 20
MOVE_FRAMES = 20
TOTAL_FRAMES = 3 * HOLD_FRAMES + 2 * MOVE_FRAMES
HOLD_INDICES = (
    HOLD_FRAMES - 1,
    HOLD_FRAMES + MOVE_FRAMES + HOLD_FRAMES - 1,
    TOTAL_FRAMES - 1,
)
CORNER_LABEL_ANCHORS = POINTS
F_EDGE_LABEL_ANCHOR = (Q(0), Q(8))
T_EDGE_LABEL_ANCHOR = (Q(4), Q(14))


def fraction_text(value):
    value = Q(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _ease(index, count):
    p = Q(index, max(1, count - 1))
    return p * p * (3 - 2 * p)


def frame_state(index):
    index = max(0, min(index, TOTAL_FRAMES - 1))
    if index < HOLD_FRAMES:
        return 0, Q(0)
    index -= HOLD_FRAMES
    if index < MOVE_FRAMES:
        return 1, _ease(index, MOVE_FRAMES)
    index -= MOVE_FRAMES
    if index < HOLD_FRAMES:
        return 2, Q(1)
    index -= HOLD_FRAMES
    if index < MOVE_FRAMES:
        return 3, _ease(index, MOVE_FRAMES)
    return 4, Q(1)


def subtitle_for_frame(index):
    return SUBTITLES[frame_state(index)[0]]


def _region():
    constraints = ((Q(1), Q(2)), (Q(1), Q(1)),
                   (Q(1), Q(0)), (Q(0), Q(1)))
    bounds = (Q(32), Q(20), Q(21), Q(20))
    points = vertices(LP.build(c=(0, 0), A=constraints, b=bounds))
    coords = [(float(t), float(f)) for t, f in points]
    center = (sum(t for t, _ in coords) / len(coords),
              sum(f for _, f in coords) / len(coords))
    return sorted(coords, key=lambda p: math.atan2(p[1] - center[1],
                                                    p[0] - center[0]))


REGION = _region()
ROW_LABEL_ANCHORS = ((Q(16), Q(8)), (Q(18), Q(2)))
def _terms(variables, coefficients):
    text = ""
    for variable, coefficient in zip(variables, coefficients):
        if coefficient == 0:
            continue
        sign = "+" if coefficient > 0 else "−"
        magnitude = abs(coefficient)
        amount = "" if magnitude == 1 else fraction_text(magnitude)
        text += f" {sign} {amount}{variable}"
    return text


def dictionary_text(iteration):
    state = iteration.dictionary
    basis = iteration.basis
    nonbasic = tuple(index for index in range(len(VARIABLES))
                     if index not in basis)
    lines = [
        f"{VARIABLES[basis[row]]} = {fraction_text(state.x_B[row])}"
        + _terms(
            tuple(VARIABLES[index] for index in nonbasic),
            tuple(-state.rows[row][index] for index in nonbasic),
        )
        for row in range(len(basis))
    ]
    value = sum((MILL_C[basis[row]] * state.x_B[row]
                 for row in range(len(basis))), Q(0))
    lines.append(
        f"z = {fraction_text(value)}"
        + _terms(
            tuple(VARIABLES[index] for index in nonbasic),
            tuple(state.reduced_costs[index] for index in nonbasic),
        )
    )
    return "\n".join(lines)


def _active_iteration(stage):
    return WALK.steps[0 if stage <= 1 else 1 if stage <= 3 else 2]


def _bar_data(stage):
    pivot = FIRST_PIVOT if stage <= 1 else SECOND_PIVOT if stage <= 3 else None
    iteration = WALK.steps[0 if stage <= 1 else 1]
    if pivot is None:
        return ()
    labels = {
        0: "t ≥ 0", 1: "f ≥ 0", 2: "lathe", 3: "press",
    }
    return tuple(
        (labels[iteration.basis[row]], ratio, pivot.leaving == iteration.basis[row])
        for row, ratio in enumerate(pivot.ratios) if ratio is not None
    )


def pivot_gif():
    fig, empty_ax = figure(12.0, 6.2)
    fig.delaxes(empty_ax)
    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.15, top=0.83)
    ax = fig.add_axes((0.08, 0.19, 0.49, 0.61))
    panel = fig.add_axes((0.62, 0.43, 0.34, 0.34))
    ratio_ax = fig.add_axes((0.64, 0.16, 0.30, 0.19))
    fig.text(0.08, 0.96, TITLE, fontsize=11, color=TEXT,
             fontweight="semibold", ha="left")
    subtitle = fig.text(0.08, 0.90, "", fontsize=8.8, color=TEXT_DIM,
                        ha="left")

    def update(index):
        stage, progress = frame_state(index)
        subtitle.set_text(SUBTITLES[stage])
        ax.clear()
        panel.clear()
        ratio_ax.clear()
        style(ax, xlabel="3-ply batches t", ylabel="5-ply batches f")
        ax.set_xlim(-0.8, 21)
        ax.set_ylim(-0.8, 20)
        ax.set_aspect("equal", adjustable="box")
        ax.add_patch(Polygon(REGION, closed=True, facecolor=PLAN, alpha=0.12,
                             edgecolor="none", zorder=1))
        ax.plot([0, 21], [16, 5.5], color=TEXT_DIM, linewidth=1.1, zorder=2)
        ax.plot([0, 21], [20, -1], color=TEXT_DIM, linewidth=1.1, zorder=2)
        ax.axhline(0, color=TEXT_DIM, linewidth=0.9, zorder=2)
        ax.axvline(0, color=TEXT_DIM, linewidth=0.9, zorder=2)

        if stage == 1:
            point = tuple(START[i] + progress * (MIDDLE[i] - START[i])
                          for i in range(2))
            path = (START, point)
        elif stage == 3:
            point = tuple(MIDDLE[i] + progress * (FINAL[i] - MIDDLE[i])
                          for i in range(2))
            path = (START, MIDDLE, point)
        elif stage == 0:
            point, path = START, (START,)
        elif stage == 2:
            point, path = MIDDLE, (START, MIDDLE)
        else:
            point, path = FINAL, POINTS
        if len(path) > 1:
            ax.plot([float(p[0]) for p in path],
                    [float(p[1]) for p in path], color=PLAN, linewidth=2.0,
                    zorder=5)
        if stage in (1, 2):
            ax.annotate(
                "", xy=tuple(map(float, point)),
                xytext=tuple(map(float, START)),
                arrowprops=dict(arrowstyle="-|>", color=PLAN,
                                linewidth=1.5, mutation_scale=11),
                zorder=6,
            )
            ax.annotate(
                "f enters, +5 per batch",
                xy=tuple(map(float, F_EDGE_LABEL_ANCHOR)),
                xytext=(10, 3), textcoords="offset points", color=PLAN,
                fontsize=6.8,
                arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.55),
                bbox=dict(boxstyle="square,pad=0.10", facecolor=SURFACE,
                          edgecolor=PLAN, linewidth=0.4), zorder=9,
            )
        elif stage in (3, 4):
            ax.annotate(
                "", xy=tuple(map(float, point)),
                xytext=tuple(map(float, MIDDLE)),
                arrowprops=dict(arrowstyle="-|>", color=PLAN,
                                linewidth=1.5, mutation_scale=11),
                zorder=6,
            )
        if stage == 3:
            ax.annotate(
                "t enters, +1/2:\none 3-ply for half a 5-ply",
                xy=tuple(map(float, T_EDGE_LABEL_ANCHOR)),
                xytext=(13, -25), textcoords="offset points", color=PLAN,
                fontsize=6.5,
                arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.55),
                bbox=dict(boxstyle="square,pad=0.10", facecolor=SURFACE,
                          edgecolor=PLAN, linewidth=0.4), zorder=9,
            )
        ax.plot([float(point[0])], [float(point[1])], "o", color=PLAN,
                markeredgecolor=SURFACE, markeredgewidth=1.2, markersize=7.5,
                zorder=7)
        if stage in (0, 1):
            label_anchor = START
            label = "(0, 0)"
        elif stage in (2, 3):
            label_anchor = MIDDLE
            label = "(0, 16), z = 80"
        else:
            label_anchor = FINAL
            label = "(8, 12), z = 84"
        ax.annotate(
            label, xy=tuple(map(float, label_anchor)), xytext=(9, 9),
            textcoords="offset points", color=PLAN, fontsize=7.4,
            bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                      edgecolor=PLAN, linewidth=0.4), zorder=9,
        )
        for anchor, label_text in zip(ROW_LABEL_ANCHORS, ("lathe wall", "press wall")):
            ax.annotate(
                label_text, xy=tuple(map(float, anchor)), xytext=(-8, 7),
                textcoords="offset points", color=TEXT_DIM, fontsize=7.0,
                ha="right",
                bbox=dict(boxstyle="square,pad=0.10", facecolor=SURFACE,
                          edgecolor=TEXT_DIM, linewidth=0.4), zorder=8,
            )

        iteration = _active_iteration(stage)
        panel.axis("off")
        panel.text(
            0.0, 1.0, f"BASIS {tuple(VARIABLES[i] for i in iteration.basis)}",
            transform=panel.transAxes, va="top", fontsize=9.5,
            color=TEXT_DIM, family="monospace",
        )
        panel.text(
            0.0, 0.84, dictionary_text(iteration),
            transform=panel.transAxes, va="top", fontsize=11.5,
            color=PRICE if stage == 4 else TEXT, family="monospace",
            linespacing=1.65,
            bbox=dict(boxstyle="square,pad=0.55", facecolor=SURFACE,
                      edgecolor=PRICE if stage == 4 else TEXT_DIM,
                      linewidth=0.65),
        )

        bars = _bar_data(stage)
        if bars:
            ratio_ax.set_title("ratio test  (slack ÷ use)", loc="left",
                               fontsize=7.2, color=TEXT_DIM, pad=4)
            ratio_ax.set_xlim(
                0, max(float(value) for _, value, _ in bars) * 1.2
            )
            ratio_ax.set_ylim(-0.55, len(bars) - 0.45)
            ratio_ax.set_yticks(range(len(bars)))
            ratio_ax.set_yticklabels(
                [f"{name} — leaves" if leaving else name
                 for name, _, leaving in bars],
                                     fontsize=7.2, color=TEXT_DIM)
            ratio_ax.tick_params(axis="x", labelsize=6.8, colors=TEXT_DIM)
            ratio_ax.grid(axis="x", color=TEXT_DIM, alpha=0.18, linewidth=0.6)
            ratio_ax.set_axisbelow(True)
            for row, (name, value, leaving) in enumerate(bars):
                color = PLAN if leaving else TEXT_DIM
                ratio_ax.barh(row, float(value), color=color, height=0.52,
                              alpha=0.82, zorder=3)
                ratio_ax.text(float(value) + 0.25, row, fraction_text(value),
                              va="center", fontsize=7.3,
                              color=PRICE if leaving else TEXT, zorder=4)
            for spine in ("top", "right", "left"):
                ratio_ax.spines[spine].set_visible(False)
        else:
            ratio_ax.axis("off")
            ratio_ax.text(0, 0.5, "no positive reduced costs",
                          transform=ratio_ax.transAxes, fontsize=8.2,
                          color=PRICE, va="center")
        return []

    animate(fig, update, TOTAL_FRAMES, OUT / "pivot.gif", fps=12, hold=3.0,
            preserve_colors=(PRICE,))


if __name__ == "__main__":
    pivot_gif()
