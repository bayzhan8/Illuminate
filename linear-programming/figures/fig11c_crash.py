"""Crash through the buyer region until both price rows are tight."""

from fractions import Fraction as Q

from matplotlib.patches import Polygon
from illuminate.draw import (PLAN, PRICE, SURFACE, TEXT, TEXT_DIM, animate,
                             chapter_dir, figure, margin_note, style)
from linprog.corners import crash, tight
from linprog.lp import LP, vertices

try:
    from .fig11b_lines import BUYER_A, BUYER_B, BUYER_WINDOW
    from .scene import ease
except ImportError:
    from fig11b_lines import BUYER_A, BUYER_B, BUYER_WINDOW
    from scene import ease

OUT = chapter_dir("11-corners-by-algebra")
OBJECTIVE = (Q(32), Q(20))
START = (Q(4), Q(4))
DIRECTIONS = ((Q(-1), Q(-1)), (Q(1), Q(-2)))
BUYER = (
    (Q(-1), Q(-1)), (Q(-2), Q(-1)), (Q(-1), Q(0)), (Q(0), Q(-1))
)
BUYER_RHS = (Q(-3), Q(-5), Q(0), Q(0))
WALL_LABEL_ANCHORS = ((Q(0), Q(3)), (Q(0), Q(5)))
STOP_LABEL_ANCHORS = (START, (Q(5, 3), Q(5, 3)), (Q(2), Q(1)))
STOPS = ((24, 24), (30, 24), (30, 36))
TOTAL_FRAMES = sum(move + hold for move, hold in STOPS)
HOLD_FRAMES = tuple(hold for _, hold in STOPS)
_choices = iter(DIRECTIONS)
CRASH_PATH, CRASH_STATUS = crash(
    BUYER, BUYER_RHS, OBJECTIVE, START, choose=lambda basis, c: next(_choices)
)
assert CRASH_STATUS == "bfs"


def _dot(a, x):
    return sum((u * v for u, v in zip(a, x)), Q(0))


def _region():
    A = BUYER_A + ((1, 0), (0, 1))
    b = BUYER_B + BUYER_WINDOW
    lp = LP.build(c=(0, 0), A=A, b=b)
    points = [(float(x), float(y)) for x, y in vertices(lp)]
    center = (sum(x for x, _ in points) / len(points),
              sum(y for _, y in points) / len(points))
    import math
    return sorted(points,
                  key=lambda p: math.atan2(p[1] - center[1], p[0] - center[0]))


def _frame(i):
    lengths = (STOPS[0][1], STOPS[1][0], STOPS[1][1],
               STOPS[2][0], STOPS[2][1])
    boundaries = []
    total = 0
    for length in lengths:
        total += length
        boundaries.append(total)
    if i < boundaries[0]:
        return 0, START
    if i < boundaries[1]:
        p = Q(ease((i - boundaries[0]) / max(1, lengths[1] - 1)))
        return 1, tuple(START[j] + p * (STOP_LABEL_ANCHORS[1][j] - START[j])
                        for j in range(2))
    if i < boundaries[2]:
        return 2, STOP_LABEL_ANCHORS[1]
    if i < boundaries[3]:
        p = Q(ease((i - boundaries[2]) / max(1, lengths[3] - 1)))
        return 3, tuple(STOP_LABEL_ANCHORS[1][j] + p *
                        (STOP_LABEL_ANCHORS[2][j] - STOP_LABEL_ANCHORS[1][j])
                        for j in range(2))
    return 4, STOP_LABEL_ANCHORS[2]


def _fmt(value):
    value = Q(value)
    return str(value.numerator) if value.denominator == 1 \
        else f"{float(value):.2f}".rstrip("0").rstrip(".")


def crash_gif():
    fig, ax = figure(8.4, 6.4)
    fig.subplots_adjust(left=0.13, right=0.97, bottom=0.20, top=0.80)
    note = margin_note(fig, y=0.025, size=9.0)
    polygon = _region()

    def update(i):
        i = min(i, TOTAL_FRAMES - 1)
        stage, point = _frame(i)
        ax.clear()
        style(ax, xlabel="3-ply price y₁", ylabel="5-ply price y₂")
        ax.set_xlim(-0.6, 8)
        ax.set_ylim(-0.6, 8)
        ax.set_aspect("equal", adjustable="box")
        ax.add_patch(Polygon(polygon, closed=True, facecolor=PRICE, alpha=0.12,
                             edgecolor="none", zorder=1))
        tight_rows = tight(BUYER, BUYER_RHS, point)
        for j, (intercept, slope) in enumerate(((Q(3), Q(-1)),
                                                 (Q(5), Q(-2)))):
            ax.plot([0, 8], [float(intercept), float(intercept + 8 * slope)],
                    color=TEXT_DIM, linewidth=2.0 if j in tight_rows else 1.1,
                    zorder=3)
        ax.axhline(0, color=TEXT_DIM, linewidth=1.0, zorder=2)
        ax.axvline(0, color=TEXT_DIM, linewidth=1.0, zorder=2)
        for anchor, label, offset in zip(
                WALL_LABEL_ANCHORS, ("3-ply row", "5-ply row"),
                ((8, 8), (8, 8))):
            ax.annotate(label, xy=tuple(map(float, anchor)), xytext=offset,
                        textcoords="offset points", color=TEXT_DIM, fontsize=7.4,
                        bbox=dict(boxstyle="square,pad=0.13", facecolor=SURFACE,
                                  edgecolor=TEXT_DIM, linewidth=0.4), zorder=8)
        middle, final = STOP_LABEL_ANCHORS[1:]
        segments = []
        if stage == 1:
            segments.append((START, point))
        elif stage >= 2:
            segments.append((START, middle))
        if stage == 3:
            segments.append((middle, point))
        elif stage >= 4:
            segments.append((middle, final))
        for start, end in segments:
            ax.plot([float(start[0]), float(end[0])],
                    [float(start[1]), float(end[1])], color=PLAN,
                    linewidth=1.4, alpha=0.65, zorder=5)
        ax.plot([float(point[0])], [float(point[1])], "o", color=PLAN,
                markersize=8, markeredgecolor=SURFACE, markeredgewidth=1.3,
                zorder=9)
        for stop, label, offset in zip(
                STOP_LABEL_ANCHORS, ("(4, 4)", "(5/3, 5/3)", "(2, 1)"),
                ((8, 8), (-58, 8), (9, 8))):
            if stage >= (0 if stop == START else 2 if stop == STOP_LABEL_ANCHORS[1] else 4):
                ax.annotate(label, xy=tuple(map(float, stop)), xytext=offset,
                            textcoords="offset points", color=PLAN, fontsize=7.6,
                            bbox=dict(boxstyle="square,pad=0.13",
                                      facecolor=SURFACE, edgecolor=PLAN,
                                      linewidth=0.4), zorder=10)
        if stage in (0, 1):
            direction = DIRECTIONS[0]
        elif stage in (2, 3):
            direction = DIRECTIONS[1]
        else:
            direction = None
        if direction is not None:
            end = STOP_LABEL_ANCHORS[1] if stage in (0, 1) \
                else STOP_LABEL_ANCHORS[2]
            ax.annotate("", xy=tuple(map(float, end)),
                        xytext=tuple(map(float, point)),
                        arrowprops=dict(arrowstyle="-|>", color=PLAN,
                                        linewidth=1.8, mutation_scale=12),
                        zorder=8)
            direction_offsets = ((-46, -13), (8, -9))
            ax.annotate(
                f"d = ({_fmt(direction[0])}, {_fmt(direction[1])})",
                xy=tuple(map(float, end)), xytext=direction_offsets[0 if stage < 2 else 1],
                textcoords="offset points", color=PLAN, fontsize=7.1,
                arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.6),
                    bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                              edgecolor=PLAN, linewidth=0.4), zorder=10)
        value = _dot(OBJECTIVE, point)
        ax.plot([0, 8], [float(value / OBJECTIVE[1]),
                          float((value - 8 * OBJECTIVE[0]) / OBJECTIVE[1])],
                color=PRICE, linewidth=1.0, linestyle=(0, (4, 3)), zorder=4)
        ax.annotate(
            f"bill = {_fmt(value)}", xy=tuple(map(float, point)),
            xytext=((-55, -17) if stage in (2, 3) else (10, -17)),
            textcoords="offset points", color=PRICE,
            fontsize=7.2, bbox=dict(boxstyle="square,pad=0.12",
                                    facecolor=SURFACE, edgecolor=PRICE,
                                    linewidth=0.4), zorder=11)
        labels = ("none", "5-ply", "5-ply", "5-ply", "3-ply and 5-ply")
        ranks = (0, 0, 1, 1, 2)
        note.set_text(f"tight rows: {labels[stage]}   rank = {ranks[stage]}\n"
                      f"bill = {_fmt(value)}")
        return []

    animate(fig, update, TOTAL_FRAMES, OUT / "crash.gif", fps=12, hold=3.0)


if __name__ == "__main__":
    crash_gif()
