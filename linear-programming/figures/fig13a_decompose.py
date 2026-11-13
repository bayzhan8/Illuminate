"""Draw the buyer offer as a corner mixture and an escape route."""

from fractions import Fraction as Q
import math

from matplotlib.patches import Polygon

from illuminate.draw import (PRICE, SURFACE, TEXT, TEXT_DIM, animate,
                             chapter_dir, figure, margin_note, style)
from linprog import mill
from linprog.lp import LP, vertices
from linprog.representation import decompose

if __package__:
    from .fig11c_crash import BUYER, BUYER_RHS
else:
    from fig11c_crash import BUYER, BUYER_RHS

OUT = chapter_dir("13-corners-and-escape")
START = (Q(4), Q(4))
OBJECTIVE = mill.MILL.b
CHOSEN_DIRECTIONS = ((Q(-1), Q(-1)), (Q(1), Q(-2)))
TITLE = "Corners plus escape routes"
SUBTITLES = (
    "start with the feasible offer (4, 4)",
    "blocked move e = (−1, −1) reaches (5/3, 5/3)",
    "the free direction (1, 1) supplies the escape",
    "the one-row point lies between two buyer corners",
    "the corner mixture and escape reconstruct (4, 4)",
)
START_HOLD = 18
BLOCKED_MOVE = 24
MIDDLE_HOLD = 18
SEGMENT_MOVE = 24
FINAL_HOLD = 30
TOTAL_FRAMES = START_HOLD + BLOCKED_MOVE + MIDDLE_HOLD + SEGMENT_MOVE + FINAL_HOLD
HOLD_INDICES = (
    START_HOLD - 1,
    START_HOLD + BLOCKED_MOVE + MIDDLE_HOLD - 1,
    TOTAL_FRAMES - 1,
)
BUYER_WINDOW = (Q(8), Q(8))


def _direction_picker(directions):
    selected = iter(directions)
    return lambda basis: next(selected)


(WEIGHTS, ESCAPE), STEP_LOG = decompose(
    BUYER, BUYER_RHS, START, choose=_direction_picker(CHOSEN_DIRECTIONS)
)
BLOCKED_STEP, MIX_STEP = STEP_LOG
MIDDLE = BLOCKED_STEP.positive_point
CORNER_01 = MIX_STEP.negative_point
CORNER_10 = MIX_STEP.positive_point
ESCAPE_ENDPOINT = tuple(MIDDLE[i] + ESCAPE[i] for i in range(2))
CORNER_LABEL_ANCHORS = (CORNER_01, CORNER_10)
WEIGHT_LABEL_ANCHORS = (CORNER_01, CORNER_10)
ESCAPE_LABEL_ANCHOR = tuple((MIDDLE[i] + ESCAPE_ENDPOINT[i]) / 2
                            for i in range(2))
ROW_LABEL_ANCHORS = ((Q(1), Q(2)), (Q(1), Q(3)))

_plot_A = BUYER + ((Q(1), Q(0)), (Q(0), Q(1)))
_plot_b = BUYER_RHS + BUYER_WINDOW
_plot_lp = LP.build(c=(0, 0), A=_plot_A, b=_plot_b)
_points = [(float(x), float(y)) for x, y in vertices(_plot_lp)]
_center = (sum(x for x, _ in _points) / len(_points),
           sum(y for _, y in _points) / len(_points))
BUYER_REGION = tuple(sorted(
    _points, key=lambda point: math.atan2(point[1] - _center[1],
                                          point[0] - _center[0])
))


def _ease(step, steps):
    progress = Q(step, max(1, steps - 1))
    return progress * progress * (3 - 2 * progress)


def frame_state(index):
    index = max(0, min(index, TOTAL_FRAMES - 1))
    if index < START_HOLD:
        return 0, Q(0)
    index -= START_HOLD
    if index < BLOCKED_MOVE:
        return 1, _ease(index, BLOCKED_MOVE)
    index -= BLOCKED_MOVE
    if index < MIDDLE_HOLD:
        return 2, Q(1)
    index -= MIDDLE_HOLD
    if index < SEGMENT_MOVE:
        return 3, _ease(index, SEGMENT_MOVE)
    return 4, Q(1)


def subtitle_for_frame(index):
    return SUBTITLES[frame_state(index)[0]]


def format_amount(value):
    value = Q(value)
    if value.denominator == 1:
        return str(value.numerator)
    scaled = value * 100 + Q(1, 2)
    cents = scaled.numerator // scaled.denominator
    return f"{cents // 100}.{cents % 100:02d}"


def bill_split():
    corner_terms = tuple(
        WEIGHTS[point] * sum((OBJECTIVE[i] * point[i] for i in range(2)), Q(0))
        for point in (CORNER_10, CORNER_01)
    )
    escape_term = sum((OBJECTIVE[i] * ESCAPE[i] for i in range(2)), Q(0))
    total = sum(corner_terms, Q(0)) + escape_term
    return corner_terms + (escape_term,), total


def _annotate(ax, label, anchor, offset, color=PRICE, leader=True):
    ax.annotate(
        label, xy=tuple(float(value) for value in anchor),
        xytext=offset, textcoords="offset points", color=color, fontsize=7.3,
        arrowprops=(dict(arrowstyle="-", color=color, linewidth=0.55)
                    if leader else None),
        bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                  edgecolor=color, linewidth=0.4),
        zorder=10,
    )


def decomposition_gif():
    fig, ax = figure(8.4, 6.4)
    fig.subplots_adjust(left=0.13, right=0.97, bottom=0.20, top=0.81)
    fig.text(0.08, 0.96, TITLE, fontsize=11, color=TEXT,
             fontweight="semibold", ha="left")
    subtitle = fig.text(0.08, 0.90, "", fontsize=8.9, color=TEXT_DIM,
                        ha="left")
    note = margin_note(fig, y=0.025, size=8.7)

    def update(index):
        phase, progress = frame_state(index)
        subtitle.set_text(SUBTITLES[phase])
        ax.clear()
        style(ax, xlabel="3-ply price y₁", ylabel="5-ply price y₂")
        ax.set_xlim(-0.7, 8)
        ax.set_ylim(-0.7, 8)
        ax.set_aspect("equal", adjustable="box")
        ax.add_patch(Polygon(BUYER_REGION, closed=True, facecolor=PRICE,
                             alpha=0.13, edgecolor=PRICE, linewidth=1.1,
                             zorder=1))
        ax.plot([0, 8], [3, -5], color=TEXT_DIM, linewidth=1.0, zorder=2)
        ax.plot([0, 8], [5, -11], color=TEXT_DIM, linewidth=1.0, zorder=2)
        ax.axhline(0, color=TEXT_DIM, linewidth=0.9, zorder=2)
        ax.axvline(0, color=TEXT_DIM, linewidth=0.9, zorder=2)
        for anchor, label, offset in (
                (ROW_LABEL_ANCHORS[0], "3-ply row", (-52, -12)),
                (ROW_LABEL_ANCHORS[1], "5-ply row", (-56, 8))):
            _annotate(ax, label, anchor, offset, color=TEXT_DIM)

        current = START
        if phase == 1:
            current = tuple(
                START[i] + progress * (MIDDLE[i] - START[i])
                for i in range(2)
            )
        elif phase >= 2:
            current = MIDDLE

        if phase >= 1:
            ax.annotate(
                "", xy=tuple(float(value) for value in current),
                xytext=tuple(float(value) for value in START),
                arrowprops=dict(arrowstyle="-|>", color=PRICE, linewidth=1.8,
                                mutation_scale=12),
                zorder=5,
            )
            if phase == 1:
                _annotate(
                    ax, "e = (−1, −1)",
                    tuple((START[i] + current[i]) / 2 for i in range(2)),
                    (-45, -14),
                )
            else:
                _annotate(ax, "(5/3, 5/3)", MIDDLE, (-54, -16))

        if phase >= 2:
            ax.annotate(
                "", xy=tuple(float(value) for value in ESCAPE_ENDPOINT),
                xytext=tuple(float(value) for value in MIDDLE),
                arrowprops=dict(arrowstyle="-|>", color=PRICE, linewidth=1.6,
                                linestyle=(0, (4, 3)), mutation_scale=12),
                zorder=6,
            )
            _annotate(
                ax, "+ 7/3 · (1, 1), escape", ESCAPE_LABEL_ANCHOR, (10, 10)
            )

        if phase >= 3:
            segment_start = tuple(
                MIDDLE[i] + progress * (CORNER_01[i] - MIDDLE[i])
                for i in range(2)
            )
            segment_end = tuple(
                MIDDLE[i] + progress * (CORNER_10[i] - MIDDLE[i])
                for i in range(2)
            )
            ax.plot([float(segment_start[0]), float(segment_end[0])],
                    [float(segment_start[1]), float(segment_end[1])],
                    color=PRICE, linewidth=2.2, zorder=7)
            ax.plot([float(MIDDLE[0])], [float(MIDDLE[1])], "o",
                    color=PRICE, markeredgecolor=SURFACE, markeredgewidth=1.1,
                    markersize=6.5, zorder=8)

        if phase == 4:
            for point, label, offset in (
                    (CORNER_01, "(0, 5), weight 1/6", (8, 10)),
                    (CORNER_10, "(2, 1), weight 5/6", (10, -20))):
                ax.plot([float(point[0])], [float(point[1])], "o", color=PRICE,
                        markeredgecolor=SURFACE, markeredgewidth=1.1,
                        markersize=6.5, zorder=8)
                _annotate(ax, label, point, offset)

        ax.plot([float(START[0])], [float(START[1])], "o", color=PRICE,
                markeredgecolor=SURFACE, markeredgewidth=1.2, markersize=7.3,
                zorder=9)
        _annotate(ax, "offer (4, 4), bill 208", START, (10, 8))

        value = sum((OBJECTIVE[i] * START[i] for i in range(2)), Q(0))
        x_values = (Q(0), Q(8))
        y_values = tuple(
            (value - OBJECTIVE[0] * t) / OBJECTIVE[1] for t in x_values
        )
        ax.plot([float(x) for x in x_values],
                [float(y) for y in y_values], color=PRICE, linewidth=0.9,
                linestyle=(0, (4, 3)), alpha=0.75, zorder=3)

        if phase == 4:
            terms, total = bill_split()
            split = " + ".join(format_amount(term) for term in terms)
            note.set_text(f"bill split: {split} = {format_amount(total)}")
        else:
            note.set_text("weighted corner bills + the cost of the escape route")
        return []

    animate(fig, update, TOTAL_FRAMES, OUT / "decompose.gif", fps=12, hold=3.0,
            preserve_colors=(PRICE,))


if __name__ == "__main__":
    decomposition_gif()
