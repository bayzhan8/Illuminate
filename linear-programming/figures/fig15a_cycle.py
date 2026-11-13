"""Draw the six-pivot cycle and the branch taken by Bland's rule."""

from fractions import Fraction as Q
import math

from matplotlib.patches import Circle, FancyArrowPatch

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             WARN, animate, chapter_dir, figure)
from linprog.simplex import simplex

OUT = chapter_dir("15-cycling")

A = (
    (Q(1, 2), Q(-11, 2), Q(-5, 2), Q(9), Q(1), Q(0), Q(0)),
    (Q(1, 2), Q(-3, 2), Q(-1, 2), Q(1), Q(0), Q(1), Q(0)),
    (Q(1), Q(0), Q(0), Q(0), Q(0), Q(0), Q(1)),
)
B = (Q(0), Q(0), Q(1))
C = (Q(10), Q(-57), Q(-9), Q(-24), Q(0), Q(0), Q(0))
START_BASIS = (4, 5, 6)
VARIABLE_LABELS = ("x₁", "x₂", "x₃", "x₄", "x₅", "x₆", "x₇")
BASIS_LABELS = ("B₀", "B₁", "B₂", "B₃", "B₄", "B₅")
TITLE = "Walking in circles, and the rule that stops it"
SUBTITLES = (
    "six bases describe the same point: x = 0, z = 0",
    "pivot 1: x₁ enters, x₅ leaves; theta = 0",
    "pivot 2: x₂ enters, x₆ leaves; theta = 0",
    "pivot 3: x₃ enters, x₁ leaves; theta = 0",
    "pivot 4: x₄ enters, x₂ leaves; theta = 0",
    "pivot 5: x₅ enters, x₃ leaves; theta = 0",
    "pivot 6 closes the same basis set; theta = 0",
    "Bland breaks at node 6: x₁ enters instead of x₆",
    "Bland's seventh pivot reaches z = 1",
)
STAGE_DURATIONS = (18, 10, 10, 10, 10, 10, 18, 18, 30)
TOTAL_FRAMES = sum(STAGE_DURATIONS)
_ends = []
_total = 0
for _duration in STAGE_DURATIONS:
    _total += _duration
    _ends.append(_total - 1)
HOLD_INDICES = tuple(_ends)

CYCLE_RESULT = simplex(A, B, C, START_BASIS, rule="dantzig")
BLAND_RESULT = simplex(A, B, C, START_BASIS, rule="bland")
CYCLE = CYCLE_RESULT.cycle
BLAND_BRANCH = BLAND_RESULT.steps[5:7]
CYCLE_ARROW_LABELS = tuple(
    f"{VARIABLE_LABELS[step.pivot.entering]} in, "
    f"{VARIABLE_LABELS[step.pivot.leaving]} out"
    for step in CYCLE
)
BLAND_ARROW_LABELS = tuple(
    f"{VARIABLE_LABELS[step.pivot.entering]} in\n"
    f"{VARIABLE_LABELS[step.pivot.leaving]} out"
    for step in BLAND_BRANCH
)
CYCLE_BASES = tuple(step.basis for step in CYCLE)
BLAND_BASIS = BLAND_RESULT.steps[6].basis
FINAL_POINT = BLAND_RESULT.x[:4]
FINAL_VALUE = BLAND_RESULT.value

CENTER = (3.25, 3.45)
RADIUS = 2.0
_angles = (-60, -120, -180, -240, -300, -360)
NODE_POSITIONS = tuple(
    (CENTER[0] + RADIUS * math.cos(math.radians(angle)),
     CENTER[1] + RADIUS * math.sin(math.radians(angle)))
    for angle in _angles
)
BRANCH_NODE_POSITION = (7.15, NODE_POSITIONS[5][1])
FINAL_NODE_POSITION = (9.45, NODE_POSITIONS[5][1])
FINAL_NODE_RADIUS = 0.82


def _midpoint(start, end):
    return ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)


CYCLE_ARROW_ANCHORS = tuple(
    _midpoint(NODE_POSITIONS[index],
              NODE_POSITIONS[(index + 1) % len(NODE_POSITIONS)])
    for index in range(len(NODE_POSITIONS))
)
BLAND_ARROW_ANCHORS = (
    _midpoint(NODE_POSITIONS[5], BRANCH_NODE_POSITION),
    _midpoint(BRANCH_NODE_POSITION, FINAL_NODE_POSITION),
)
_cycle_label_offsets = (
    (0, 0.31), (-0.38, -0.08), (-0.38, 0.08),
    (0, -0.31), (0.38, 0.08), (0.38, -0.08),
)


def frame_stage(index):
    index = max(0, min(index, TOTAL_FRAMES - 1))
    for stage, end in enumerate(HOLD_INDICES):
        if index <= end:
            return stage
    return len(HOLD_INDICES) - 1


def subtitle_for_frame(index):
    return SUBTITLES[frame_stage(index)]


def _arrow(ax, start, end, color, lw=1.4, rad=0):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=11,
        connectionstyle=f"arc3,rad={rad}", color=color, linewidth=lw,
        shrinkA=19, shrinkB=19, zorder=3,
    ))


def _tag(ax, text, anchor, offset=(0, 0), color=TEXT_DIM, size=7.0):
    ax.annotate(
        text, xy=anchor, xytext=offset, textcoords="offset points",
        ha="center", va="center", color=color, fontsize=size,
        bbox=dict(boxstyle="square,pad=0.18", facecolor=SURFACE,
                  edgecolor=HAIRLINE, linewidth=0.45),
        zorder=8,
    )


def _draw_cycle_node(ax, index):
    x, y = NODE_POSITIONS[index]
    ax.add_patch(Circle(
        (x, y), 0.49, facecolor=SURFACE, edgecolor=TEXT_DIM,
        linewidth=1.0, zorder=5,
    ))
    basis = CYCLE_BASES[index]
    ax.text(x, y + 0.10, BASIS_LABELS[index], ha="center", va="center",
            color=TEXT, fontsize=7.6, fontweight="semibold", zorder=6)
    ax.text(x, y - 0.10,
            ", ".join(VARIABLE_LABELS[column] for column in basis),
            ha="center", va="center", color=TEXT_DIM, fontsize=6.6, zorder=6)
    ax.text(x, y - 0.66, "point 0, z = 0", ha="center", va="center",
            color=TEXT_DIM, fontsize=6.7, zorder=6)


def cycle_gif():
    fig, ax = figure(11.2, 7.0)
    fig.subplots_adjust(left=0.015, right=0.985, bottom=0.035, top=0.84)
    fig.text(0.045, 0.96, TITLE, fontsize=11, color=TEXT,
             fontweight="semibold", ha="left")
    subtitle = fig.text(0.045, 0.90, "", fontsize=8.8, color=TEXT_DIM,
                        ha="left")

    def update(index):
        stage = frame_stage(index)
        subtitle.set_text(SUBTITLES[stage])
        ax.clear()
        ax.set_xlim(0.15, 10.55)
        ax.set_ylim(0.32, 6.55)
        ax.set_aspect("equal", adjustable="box")
        ax.axis("off")
        ax.add_patch(Circle(
            CENTER, RADIUS, fill=False, edgecolor=HAIRLINE,
            linewidth=0.8, linestyle=(0, (2, 3)), zorder=1,
        ))

        visible_cycle_arrows = min(stage, 5)
        for edge in range(visible_cycle_arrows):
            start = NODE_POSITIONS[edge]
            end = NODE_POSITIONS[(edge + 1) % len(NODE_POSITIONS)]
            _arrow(ax, start, end, TEXT_DIM, rad=0.08)
            anchor = CYCLE_ARROW_ANCHORS[edge]
            _tag(
                ax, CYCLE_ARROW_LABELS[edge], anchor,
                _cycle_label_offsets[edge], size=6.8,
            )
        if stage >= 6:
            _arrow(ax, NODE_POSITIONS[5], NODE_POSITIONS[0], WARN,
                   lw=1.9, rad=0.12)
            _tag(ax, "cycle", CYCLE_ARROW_ANCHORS[5], (13, -9),
                 color=WARN, size=7.1)

        for index in range(len(NODE_POSITIONS)):
            _draw_cycle_node(ax, index)

        if stage >= 7:
            _arrow(ax, NODE_POSITIONS[5], BRANCH_NODE_POSITION, PRICE,
                   lw=1.9)
            _tag(ax, f"Bland: {BLAND_ARROW_LABELS[0]}",
                 BLAND_ARROW_ANCHORS[0], (0, 18), color=PRICE, size=6.9)
            bx, by = BRANCH_NODE_POSITION
            ax.add_patch(Circle(
                (bx, by), 0.48, facecolor=SURFACE, edgecolor=PRICE,
                linewidth=1.2, zorder=5,
            ))
            ax.text(bx, by + 0.10, "Bland 6", ha="center", va="center",
                    color=PRICE, fontsize=7.2, fontweight="semibold", zorder=6)
            ax.text(bx, by - 0.10,
                    ", ".join(VARIABLE_LABELS[column]
                              for column in BLAND_BASIS),
                    ha="center", va="center", color=PRICE, fontsize=6.3,
                    zorder=6)
            ax.text(bx, by - 0.66, "point 0, z = 0", ha="center",
                    va="center", color=TEXT_DIM, fontsize=6.7, zorder=6)

        if stage >= 8:
            _arrow(ax, BRANCH_NODE_POSITION, FINAL_NODE_POSITION, PRICE,
                   lw=1.9)
            _tag(ax, BLAND_ARROW_LABELS[1], BLAND_ARROW_ANCHORS[1],
                 (0, 18), color=PRICE, size=6.9)
            fx, fy = FINAL_NODE_POSITION
            ax.add_patch(Circle(
                (fx, fy), FINAL_NODE_RADIUS, facecolor="#1B4F9C18",
                edgecolor=PLAN, linewidth=1.4, zorder=5,
            ))
            ax.text(fx, fy + 0.15, f"z = {FINAL_VALUE}", ha="center",
                    va="center", color=PLAN, fontsize=8.2,
                    fontweight="semibold", zorder=6)
            ax.text(fx, fy - 0.17,
                    "x = (1, 0, 1, 0)", ha="center", va="center",
                    color=PLAN, fontsize=7.0, zorder=6)
        return []

    animate(fig, update, TOTAL_FRAMES, OUT / "cycle.gif", fps=12, hold=2.5,
            preserve_colors=(PLAN, PRICE, WARN))


if __name__ == "__main__":
    cycle_gif()
