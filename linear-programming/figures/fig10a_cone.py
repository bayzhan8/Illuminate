"""The mill's nonnegative plans fill a cone."""

from fractions import Fraction as Q
from pathlib import Path

from matplotlib.patches import Polygon

from illuminate.draw import (PLAN, PRICE, SURFACE, TEXT, TEXT_DIM, WARN,
                             animate, figure, margin_note, style)

OUT = Path(__file__).resolve().parents[1] / "chapters/10-plan-or-proof"

COLUMN_T = (Q(1), Q(1))
COLUMN_F = (Q(2), Q(1))
CERTIFICATE_NORMAL = (Q(-1), Q(2))
TARGET_START = (Q(32), Q(20))
TARGET_END = (Q(32), Q(10))
TARGET_CONTROL = (Q(36), Q(15))
MAX_LATHE = Q(48)
MAX_PRESS = Q(32)
CONE_POLYGON = ((Q(0), Q(0)), (MAX_LATHE, MAX_LATHE / 2),
                (MAX_PRESS, MAX_PRESS))
COLUMN_LABEL_SCALES = (Q(16), Q(15))
COLUMN_LABEL_ANCHORS = tuple(
    tuple(scale * value for value in column)
    for scale, column in zip(COLUMN_LABEL_SCALES, (COLUMN_T, COLUMN_F))
)
WALL_LABEL_SCALE = Q(12)
WALL_LABEL_ANCHOR = tuple(WALL_LABEL_SCALE * value for value in COLUMN_F)
NORMAL_SCALE = Q(7)
NORMAL_ARROW_ANCHOR = tuple(NORMAL_SCALE * value
                            for value in CERTIFICATE_NORMAL)

HOLD_FRAMES = 36
MOVE_FRAMES = 48
FRAME_COUNT = 2 * HOLD_FRAMES + MOVE_FRAMES
OUTSIDE_HOLD_START = HOLD_FRAMES + MOVE_FRAMES


def _progress(frame):
    frame = max(0, min(int(frame), FRAME_COUNT - 1))
    if frame < HOLD_FRAMES:
        return Q(0)
    if frame < OUTSIDE_HOLD_START:
        u = Q(frame - HOLD_FRAMES, MOVE_FRAMES)
        return u * u * (3 - 2 * u)
    return Q(1)


def target_at(frame):
    s = _progress(frame)
    complement = 1 - s
    return tuple(
        complement ** 2 * start
        + 2 * complement * s * control
        + s ** 2 * end
        for start, control, end in
        zip(TARGET_START, TARGET_CONTROL, TARGET_END)
    )


def decomposition_at(frame):
    lathe, press = target_at(frame)
    return 2 * press - lathe, lathe - press


def target_is_in_cone(frame):
    t, f = decomposition_at(frame)
    return t >= 0 and f >= 0


def parallelogram_vertices(frame):
    t, f = decomposition_at(frame)
    return ((Q(0), Q(0)), (t, t),
            (t + 2 * f, t + f), (2 * f, f))


def target_label_anchor(frame):
    return target_at(frame)


def _fmt(value):
    value = Q(value)
    return str(value.numerator) if value.denominator == 1 else f"{float(value):.1f}"


def _arrow(ax, end, color, linewidth=1.7, mutation_scale=12):
    ax.annotate(
        "", xy=tuple(map(float, end)), xytext=(0, 0),
        arrowprops=dict(arrowstyle="-|>", color=color, linewidth=linewidth,
                        mutation_scale=mutation_scale, shrinkA=0, shrinkB=0),
        zorder=6,
    )


def _draw(ax, frame):
    ax.clear()
    style(ax, xlabel="lathe hours L", ylabel="press hours P")
    ax.set_xlim(-18, 50)
    ax.set_ylim(-14, 34)
    ax.set_xticks((-10, 0, 10, 20, 30, 40, 50))
    ax.set_yticks((-10, 0, 10, 20, 30))
    ax.set_aspect("equal", adjustable="box")

    cone = [(float(x), float(y)) for x, y in CONE_POLYGON]
    ax.add_patch(Polygon(cone, closed=True, facecolor=PLAN, alpha=0.12,
                         edgecolor="none", zorder=1))
    for end in (CONE_POLYGON[2], CONE_POLYGON[1]):
        _arrow(ax, end, PLAN, linewidth=1.6)
    for anchor, column in zip(COLUMN_LABEL_ANCHORS, (COLUMN_T, COLUMN_F)):
        label = f"column ({_fmt(column[0])}, {_fmt(column[1])})"
        ax.annotate(
            label, xy=tuple(map(float, anchor)), xytext=(7, 6),
            textcoords="offset points", color=PLAN, fontsize=7.6,
            bbox=dict(boxstyle="square,pad=0.16", facecolor=SURFACE,
                      edgecolor=PLAN, linewidth=0.45),
            zorder=9,
        )
    b = target_at(frame)
    t, f = decomposition_at(frame)
    feasible = t >= 0 and f >= 0
    color = PLAN if feasible else WARN
    vertices = [(float(x), float(y)) for x, y in parallelogram_vertices(frame)]
    ax.add_patch(Polygon(vertices, closed=True, facecolor=color, alpha=0.18,
                         edgecolor=color, linewidth=1.7, zorder=4))

    ax.annotate(
        "", xy=tuple(map(float, b)), xytext=(0, 0),
        arrowprops=dict(arrowstyle="-|>", color=TEXT_DIM, linewidth=1.1,
                        mutation_scale=12, shrinkA=0, shrinkB=0),
        zorder=7,
    )
    ax.plot([float(b[0])], [float(b[1])], "o", color=TEXT,
            markeredgecolor=SURFACE, markeredgewidth=1.2, markersize=7,
            zorder=11)
    offset = (8, 8) if b[1] >= 15 else (8, -16)
    ax.annotate(
        f"b = ({_fmt(b[0])}, {_fmt(b[1])})",
        xy=tuple(map(float, target_label_anchor(frame))), xytext=offset,
        textcoords="offset points", color=TEXT, fontsize=8,
        bbox=dict(boxstyle="square,pad=0.16", facecolor=SURFACE,
                  edgecolor=TEXT_DIM, linewidth=0.45),
        zorder=12,
    )

    if not feasible:
        wall_end = (float(CONE_POLYGON[1][0]), float(CONE_POLYGON[1][1]))
        ax.plot([0, wall_end[0]], [0, wall_end[1]], color=PRICE,
                linewidth=2.1, linestyle=(0, (5, 3)), zorder=8)
        ax.annotate(
            "certificate wall", xy=tuple(map(float, WALL_LABEL_ANCHOR)),
            xytext=(-7, 18), textcoords="offset points", color=PRICE,
            fontsize=7.6, ha="right",
            bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                      edgecolor=PRICE, linewidth=0.45),
            zorder=12,
        )
        _arrow(ax, NORMAL_ARROW_ANCHOR, PRICE, linewidth=1.7,
               mutation_scale=13)
        ax.annotate(
            f"y = ({_fmt(CERTIFICATE_NORMAL[0])}, "
            f"{_fmt(CERTIFICATE_NORMAL[1])})",
            xy=tuple(map(float, NORMAL_ARROW_ANCHOR)),
            xytext=(-4, 7), textcoords="offset points", color=PRICE,
            fontsize=7.6, ha="right",
            bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                      edgecolor=PRICE, linewidth=0.45),
            zorder=12,
        )


def cone_gif():
    fig, ax = figure(9.2, 6.2)
    fig.subplots_adjust(left=0.12, right=0.98, bottom=0.21, top=0.82)
    fig.text(0.07, 0.95, "A target is a plan exactly when it lies in the cone",
             fontsize=11, color=TEXT, fontweight="semibold", ha="left")
    fig.text(0.07, 0.90, "The columns are (1, 1) and (2, 1); cross the second ray and t becomes negative",
             fontsize=8.1, color=TEXT_DIM, ha="left")
    fig.text(0.07, 0.86, "Inside the cone: P ≤ L ≤ 2P",
             fontsize=7.7, color=PLAN, ha="left")
    note = margin_note(fig, x=0.08, y=0.035, size=8.1)

    def update(i):
        frame = min(i, FRAME_COUNT - 1)
        b = target_at(frame)
        t, f = decomposition_at(frame)
        _draw(ax, frame)
        if target_is_in_cone(frame):
            note.set_text(
                f"b = ({_fmt(b[0])}, {_fmt(b[1])})    "
                f"plan: t = {_fmt(t)}, f = {_fmt(f)} (both nonnegative)"
            )
        else:
            column_products = tuple(
                sum((a * value for a, value
                     in zip(CERTIFICATE_NORMAL, column)), Q(0))
                for column in (COLUMN_T, COLUMN_F)
            )
            yb = sum((a * value for a, value
                      in zip(CERTIFICATE_NORMAL, b)), Q(0))
            products = ", ".join(
                f"y·({_fmt(column[0])}, {_fmt(column[1])}) = "
                f"{_fmt(product)}"
                for column, product in zip((COLUMN_T, COLUMN_F),
                                           column_products)
            )
            note.set_text(
                f"b = ({_fmt(b[0])}, {_fmt(b[1])})    "
                f"t = {_fmt(t)}, f = {_fmt(f)}: not a plan\n"
                f"{products}, "
                f"y·b = {_fmt(yb)} < 0"
            )
        return [note]

    animate(fig, update, FRAME_COUNT, OUT / "cone.gif", fps=12, hold=3.0,
            preserve_colors=(WARN,))


if __name__ == "__main__":
    cone_gif()
