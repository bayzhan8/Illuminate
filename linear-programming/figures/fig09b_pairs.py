"""Watch the t bounds meet, and disappear, as f crosses the shadow."""

from fractions import Fraction as Q
from pathlib import Path

from illuminate.draw import (PLAN, PRICE, SURFACE, TEXT, TEXT_DIM, WARN,
                             animate, figure, margin_note, style)
from linprog import mill

try:
    from .fig09a_shadow import SHADOW_POLYGON, SHADOW_ROWS
    from .scene import Stages
except ImportError:
    from fig09a_shadow import SHADOW_POLYGON, SHADOW_ROWS
    from scene import Stages

OUT = Path(__file__).resolve().parents[1] / "chapters/09-shadows"
V_FIXED = Q(78)
VALUE = tuple(mill.MILL.c)


def _fraction(value):
    return value if isinstance(value, Q) else Q(
        str(value) if isinstance(value, float) else value
    )


def _intersection_f(first, second):
    """The f coordinate where two boundary rows meet."""
    a1, b1 = first.coeffs
    a2, b2 = second.coeffs
    determinant = a1 * b2 - a2 * b1
    return (first.rhs * b2 - second.rhs * b1) / determinant


_f_limit = next(row for row in SHADOW_ROWS
                if row.coeffs[0] > 0 and row.coeffs[1] == 0
                and row.mult[0] > 0)
_value_upper = next(row for row in SHADOW_ROWS
                    if row.coeffs[0] > 0 and row.coeffs[1] > 0)
_value_press = next(row for row in SHADOW_ROWS
                    if row.coeffs[0] < 0 and row.coeffs[1] > 0)
HOLD_VALUES = (
    (mill.MILL.b[1] * VALUE[0]
     - mill.MILL.A[1][0] * V_FIXED)
    / (VALUE[0] * mill.MILL.A[1][1]
       - mill.MILL.A[1][0] * VALUE[1]),
    _intersection_f(_value_upper, _value_press),
    _f_limit.rhs / _f_limit.coeffs[0],
)
HOLD_VALUES = tuple(map(Q, HOLD_VALUES))
HOLD_VALUES += (HOLD_VALUES[-1] + 1,)
END_F = HOLD_VALUES[-1] + 1

STAGES = Stages((20, 0), (0, 12), (12, 0), (0, 12), (16, 0),
                (0, 12), (4, 0), (0, 12), (4, 8))


def pair_marker_anchors(f):
    f = _fraction(f)
    lower_value = (V_FIXED - VALUE[1] * f) / VALUE[0]
    upper_lathe = (mill.MILL.b[0] - mill.MILL.A[0][1] * f) / \
        mill.MILL.A[0][0]
    upper_press = (mill.MILL.b[1] - mill.MILL.A[1][1] * f) / \
        mill.MILL.A[1][0]
    return Q(0), lower_value, upper_lathe, upper_press


def bounds_for_f(f):
    anchors = pair_marker_anchors(f)
    return max(anchors[:2]), min(anchors[2:])


def shadow_point_anchor(f):
    return _fraction(f), V_FIXED


def _interpolated_f(frame):
    stage, progress = STAGES(frame)
    progress = Q(str(progress))
    if stage == 0:
        return HOLD_VALUES[0] * progress
    if stage == 1:
        return HOLD_VALUES[0]
    if stage == 2:
        return HOLD_VALUES[0] + (HOLD_VALUES[1] - HOLD_VALUES[0]) * progress
    if stage == 3:
        return HOLD_VALUES[1]
    if stage == 4:
        return HOLD_VALUES[1] + (HOLD_VALUES[2] - HOLD_VALUES[1]) * progress
    if stage == 5:
        return HOLD_VALUES[2]
    if stage == 6:
        return HOLD_VALUES[2] + (HOLD_VALUES[3] - HOLD_VALUES[2]) * progress
    if stage == 7:
        return HOLD_VALUES[3]
    return HOLD_VALUES[3] + (END_F - HOLD_VALUES[3]) * progress


def f_at(frame):
    return _interpolated_f(min(frame, STAGES.total - 1))


def _fmt(value):
    value = _fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{float(value):.1f}"


def _is_in_shadow(point):
    f, v = point
    return f >= 0 and all(
        row.coeffs[0] * f + row.coeffs[1] * v <= row.rhs
        for row in SHADOW_ROWS
    )


def _draw_bounds(ax, f, lower, upper):
    ax.clear()
    style(ax, xlabel="possible 3-ply batches t", grid=False)
    ax.set_xlim(-5, 33)
    ax.set_ylim(-0.92, 0.9)
    ax.set_yticks([])
    ax.set_xticks(range(-5, 34, 5))
    ax.spines["left"].set_visible(False)
    ax.hlines(0, -5, 33, color=TEXT_DIM, linewidth=1.05, zorder=1)

    marker_anchors = pair_marker_anchors(f)
    lanes = (0.53, 0.28, -0.28, -0.53)
    labels = (
        f"lower: t ≥ 0 = {_fmt(marker_anchors[0])}",
        f"lower: value = {_fmt(marker_anchors[1])}",
        f"upper: lathe = {_fmt(marker_anchors[2])}",
        f"upper: press = {_fmt(marker_anchors[3])}",
    )
    for anchor, lane, label in zip(marker_anchors, lanes, labels):
        ax.vlines(anchor, 0, lane, color=TEXT_DIM, linewidth=0.75,
                  linestyle=(0, (2, 2)), zorder=2)
        ax.plot([anchor], [lane], "o", color=TEXT, markersize=4.3,
                markeredgecolor=SURFACE, markeredgewidth=0.75, zorder=5)
        ax.text(anchor, lane + (0.07 if lane > 0 else -0.07), label,
                color=TEXT_DIM, fontsize=6.6,
                ha="center", va="bottom" if lane > 0 else "top",
                bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                          edgecolor="none"), zorder=7)

    if lower <= upper:
        if lower == upper:
            ax.plot([lower], [-0.79], "o", color=PLAN, markersize=7,
                    markeredgecolor=SURFACE, markeredgewidth=1.0, zorder=8)
        else:
            ax.plot([lower, upper], [-0.79, -0.79], color=PLAN,
                    linewidth=5.0, solid_capstyle="round", zorder=7)
        ax.text((lower + upper) / 2, -0.86,
                f"feasible t: [{_fmt(lower)}, {_fmt(upper)}]",
                color=PLAN, fontsize=7.2, ha="center", va="top",
                bbox=dict(boxstyle="square,pad=0.1", facecolor=SURFACE,
                          edgecolor="none"), zorder=9)
    else:
        ax.plot([(lower + upper) / 2], [-0.79], marker="x",
                color=WARN, markersize=8, markeredgewidth=1.8, zorder=8)
        ax.text((lower + upper) / 2, -0.86, "no t fits",
                color=WARN, fontsize=7.2, ha="center", va="top",
                bbox=dict(boxstyle="square,pad=0.1", facecolor=SURFACE,
                          edgecolor="none"), zorder=9)


def _draw_shadow(ax, point, feasible):
    ax.clear()
    style(ax, xlabel="5-ply batches f", ylabel="value v")
    ax.set_xlim(-2, 19)
    ax.set_ylim(-3, 100)
    ax.set_xticks((0, 4, 8, 12, 16))
    ax.set_yticks((0, 20, 40, 60, 80, 100))
    polygon = [(float(f), float(v)) for f, v in SHADOW_POLYGON]
    ax.fill([p[0] for p in polygon], [p[1] for p in polygon],
            color=PRICE, alpha=0.15, zorder=1)
    closed = polygon + [polygon[0]]
    ax.plot([p[0] for p in closed], [p[1] for p in closed],
            color=PRICE, linewidth=1.3, zorder=3)
    ax.plot([0, 18], [float(V_FIXED), float(V_FIXED)],
            color=TEXT_DIM, linewidth=1.1, linestyle=(0, (4, 3)), zorder=4)
    color = PLAN if feasible else WARN
    ax.plot([float(point[0])], [float(point[1])], "o", color=color,
            markeredgecolor=SURFACE, markeredgewidth=1.3,
            markersize=9, zorder=8)
    label_offset = ((8, -18) if point[0] < 2 else
                    (-8, 9) if point[0] > 14 else (8, 9))
    ax.annotate(
        f"({ _fmt(point[0])}, {_fmt(point[1])})",
        xy=tuple(map(float, point)), xytext=label_offset,
        textcoords="offset points", color=color, fontsize=7.3,
        ha="right" if label_offset[0] < 0 else "left",
        bbox=dict(boxstyle="square,pad=0.13", facecolor=SURFACE,
                  edgecolor=color, linewidth=0.45),
        zorder=9,
    )
    ax.text(1.5, float(V_FIXED) + 1, f"v = {V_FIXED}",
            color=TEXT_DIM, fontsize=7.5, ha="left", va="bottom",
            bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                      edgecolor="none"), zorder=7)


def pairs_gif():
    fig, blank = figure(9.4, 5.7)
    fig.delaxes(blank)
    left = fig.add_axes((0.08, 0.22, 0.41, 0.60))
    right = fig.add_axes((0.56, 0.20, 0.39, 0.64))
    fig.text(0.07, 0.94, "A point is in the shadow when t can fit",
             fontsize=11, color=TEXT, fontweight="semibold", ha="left")
    fig.text(0.07, 0.89, "at v = 78, compare the largest lower bound with the smallest upper bound",
             fontsize=8.7, color=TEXT_DIM, ha="left")
    note = margin_note(fig, y=0.05, size=8.5)

    def update(i):
        i = min(i, STAGES.total - 1)
        f = f_at(i)
        point = shadow_point_anchor(f)
        lower, upper = bounds_for_f(f)
        feasible = lower <= upper
        assert feasible == _is_in_shadow(point)
        _draw_bounds(left, f, lower, upper)
        _draw_shadow(right, point, feasible)
        status = (f"t interval [{_fmt(lower)}, {_fmt(upper)}]"
                  if feasible else f"no t: {_fmt(lower)} > {_fmt(upper)}")
        note.set_text(f"f = {_fmt(f)}   {status}")
        return [note]

    animate(fig, update, STAGES.total, OUT / "pairs.gif", fps=12, hold=3.0,
            preserve_colors=(WARN,))


if __name__ == "__main__":
    pairs_gif()
