"""The mill's value roof and its Fourier–Motzkin shadow."""

from fractions import Fraction as Q
from math import atan2
from pathlib import Path

from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             animate, figure, margin_note, style)
from linprog import mill
from linprog.elimination import Row, project
from linprog.lp import LP, vertices

try:
    from .scene import Stages
except ImportError:
    from scene import Stages

OUT = Path(__file__).resolve().parents[1] / "chapters/09-shadows"
TITLE = "A roof casts a shadow"
VALUE = tuple(mill.MILL.c)
WALL_T = max(point[0] for point in vertices(mill.MILL)) + Q(3)


def _basis(index, size=5):
    return tuple(Q(int(index == j)) for j in range(size))


SOURCE_ROWS = (
    Row((mill.MILL.A[0][0], mill.MILL.A[0][1], Q(0)),
        mill.MILL.b[0], _basis(0)),
    Row((mill.MILL.A[1][0], mill.MILL.A[1][1], Q(0)),
        mill.MILL.b[1], _basis(1)),
    Row((Q(-1), Q(0), Q(0)), Q(0), _basis(2)),
    Row((Q(0), Q(-1), Q(0)), Q(0), _basis(3)),
    Row((-VALUE[0], -VALUE[1], Q(1)), Q(0), _basis(4)),
)
SHADOW_ROWS = tuple(project(SOURCE_ROWS, (1, 2)))
SHADOW_LP = LP.build(
    (0, 0), [row.coeffs for row in SHADOW_ROWS],
    [row.rhs for row in SHADOW_ROWS],
)
SHADOW_CORNERS = tuple(vertices(SHADOW_LP))


def _fmt(value):
    value = Q(value)
    return str(value.numerator) if value.denominator == 1 else str(value)


def _row_with_multipliers(mult):
    return next(row for row in SHADOW_ROWS if row.mult == mult)


def _line_anchor(row):
    endpoints = [
        point for point in SHADOW_CORNERS
        if sum((a * x for a, x in zip(row.coeffs, point)), Q(0)) == row.rhs
    ]
    assert len(endpoints) == 2
    return tuple((a + b) / 2 for a, b in zip(*endpoints))


def _formula(row):
    f_coefficient, v_coefficient = row.coeffs
    if v_coefficient == 0:
        return f"f = {_fmt(row.rhs / f_coefficient)}"
    f_ratio = f_coefficient / v_coefficient
    right = row.rhs / v_coefficient
    if f_ratio == 0:
        expression = "v"
    else:
        sign = "+" if f_ratio > 0 else "−"
        magnitude = abs(f_ratio)
        term = "f" if magnitude == 1 else f"{_fmt(magnitude)}f"
        expression = f"v {sign} {term}"
    return f"{expression} = {_fmt(right)}"


def _certificate(row):
    names = ("lathe", "press", "t ≥ 0", "f ≥ 0", "value")
    terms = []
    for multiplier, name in zip(row.mult, names):
        if multiplier:
            terms.append(name if multiplier == 1
                         else f"{_fmt(multiplier)} × {name}")
    return " + ".join(terms)


_basis0 = _basis(0)
_basis1 = _basis(1)
_basis2 = _basis(2)
_basis3 = _basis(3)
_basis4 = _basis(4)
_boundary_rows = (
    _row_with_multipliers(_basis3),
    _row_with_multipliers(tuple(a + b for a, b in
                                zip(_basis0, _basis2))),
    _row_with_multipliers(tuple(3 * a + b for a, b in
                                zip(_basis0, _basis4))),
    _row_with_multipliers(tuple(3 * a + b for a, b in
                                zip(_basis1, _basis4))),
)
SHADOW_BOUNDARY_SEGMENTS = tuple(
    tuple(point for point in SHADOW_CORNERS
          if sum((a * x for a, x in zip(row.coeffs, point)), Q(0)) == row.rhs)
    for row in _boundary_rows
)
SHADOW_BOUNDARY_LABELS = tuple(
    (f"{_formula(row)}\n{_certificate(row)}", row, _line_anchor(row))
    for row in _boundary_rows
)

PLAN_POINT, PLAN_VALUE = mill.BEST, mill.BEST_VALUE
SHADOW_TOP = (PLAN_POINT[1], PLAN_VALUE)
ROOF_LABEL_ANCHOR = (Q(10), Q(2), mill.MILL.value((Q(10), Q(2))))


def _ordered(points):
    cx = sum((point[0] for point in points), Q(0)) / len(points)
    cy = sum((point[1] for point in points), Q(0)) / len(points)
    return tuple(sorted(points, key=lambda point: atan2(
        float(point[1] - cy), float(point[0] - cx)
    )))


SHADOW_POLYGON = _ordered(SHADOW_CORNERS)
MILL_POLYGON = _ordered(vertices(mill.MILL))
STAGES = Stages((0, 12), (36, 0), (0, 12), (0, 24))


def point_label(point):
    return f"({point[0]}, {point[1]})"


def _poly3(points):
    return [(float(t), float(f), float(v)) for t, f, v in points]


def _draw_3d(ax, elevation, azimuth):
    ax.clear()
    ax.set_xlim(0, float(WALL_T + 1))
    ax.set_ylim(0, float(max(f for _, f in MILL_POLYGON) + 2))
    ax.set_zlim(0, float(max(v for _, v in SHADOW_CORNERS) + 16))
    ax.set_box_aspect((1.35, 1, 0.95))
    ax.set_proj_type("ortho")
    ax.view_init(elev=elevation, azim=azimuth)
    ax.set_xlabel("3-ply batches t", color=TEXT_DIM, labelpad=5, fontsize=8)
    ax.set_ylabel("5-ply batches f", color=TEXT_DIM, labelpad=5, fontsize=8)
    ax.set_zlabel("value v", color=TEXT_DIM, labelpad=4, fontsize=8)
    ax.set_xticks((0, 8, 16, 24))
    ax.set_yticks((0, 8, 16))
    ax.set_zticks((0, 40, 80))
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.set_facecolor(SURFACE)
        axis.pane.set_edgecolor(HAIRLINE)
        axis._axinfo["grid"]["color"] = HAIRLINE

    base = [(t, f, Q(0)) for t, f in MILL_POLYGON]
    roof = [(t, f, mill.MILL.value((t, f))) for t, f in MILL_POLYGON]
    faces = [base, roof]
    for i in range(len(base)):
        j = (i + 1) % len(base)
        faces.append([base[i], base[j], roof[j], roof[i]])
    ax.add_collection3d(Poly3DCollection(
        [_poly3(face) for face in faces],
        facecolors=PLAN, edgecolors=PLAN, linewidths=0.75, alpha=0.12,
    ))
    ax.add_collection3d(Poly3DCollection(
        [_poly3(roof)], facecolors=PLAN, edgecolors=PLAN,
        linewidths=1.25, alpha=0.22,
    ))
    for i in range(len(roof)):
        j = (i + 1) % len(roof)
        ax.plot([float(roof[i][0]), float(roof[j][0])],
                [float(roof[i][1]), float(roof[j][1])],
                [float(roof[i][2]), float(roof[j][2])],
                color=PLAN, linewidth=1.0, zorder=6)

    wall = [(WALL_T, f, v) for f, v in SHADOW_POLYGON]
    ax.add_collection3d(Poly3DCollection(
        [_poly3(wall)], facecolors=PRICE, edgecolors=PRICE,
        linewidths=1.0, alpha=0.18,
    ))
    for endpoints in SHADOW_BOUNDARY_SEGMENTS:
        ax.plot([float(WALL_T), float(WALL_T)],
                [float(endpoints[0][0]), float(endpoints[1][0])],
                [float(endpoints[0][1]), float(endpoints[1][1])],
                color=PRICE, linewidth=1.55, zorder=8)

    plan_t, plan_f = PLAN_POINT
    ax.plot([float(plan_t)], [float(plan_f)], [float(PLAN_VALUE)], "o",
            color=PLAN, markeredgecolor=SURFACE, markeredgewidth=1.1,
            markersize=7.5, zorder=10)
    ax.plot([float(plan_t), float(WALL_T)],
            [float(plan_f), float(plan_f)],
            [float(PLAN_VALUE), float(PLAN_VALUE)],
            color=PRICE, linewidth=1.15, linestyle=(0, (3, 3)), zorder=7)
    ax.plot([float(WALL_T)], [float(plan_f)], [float(PLAN_VALUE)], "o",
            color=PRICE, markeredgecolor=SURFACE, markeredgewidth=1.0,
            markersize=7, zorder=10)
    ax.text(float(plan_t) + 0.3, float(plan_f) + 0.7,
            float(PLAN_VALUE) + 2,
            f"plan {point_label(PLAN_POINT)}",
            color=PLAN, fontsize=8, zorder=11)
    ax.text(float(WALL_T), float(plan_f) + 0.7, float(PLAN_VALUE) + 2,
            point_label(SHADOW_TOP), color=PRICE, fontsize=8, zorder=11)

    roof_t, roof_f, roof_v = ROOF_LABEL_ANCHOR
    ax.text(float(roof_t), float(roof_f), float(roof_v),
            f"roof v = {VALUE[0]}t + {VALUE[1]}f",
            color=PLAN, fontsize=8, zorder=8)
    ax.quiver(1, 17, 35, 19, 0, 0, color=TEXT_DIM,
              arrow_length_ratio=0.09, linewidth=1.0, zorder=9)
    ax.text(8, 17, 38, "light along t", color=TEXT_DIM, fontsize=7.5)


def _draw_shadow(ax):
    ax.clear()
    style(ax, xlabel="5-ply batches f", ylabel="value v")
    ax.set_xlim(-3, 20)
    ax.set_ylim(-4, 101)
    ax.set_xticks((0, 4, 8, 12, 16, 20))
    ax.set_yticks((0, 20, 40, 60, 80, 100))
    polygon = [(float(f), float(v)) for f, v in SHADOW_POLYGON]
    ax.fill([p[0] for p in polygon], [p[1] for p in polygon],
            color=PRICE, alpha=0.16, zorder=1)
    closed = polygon + [polygon[0]]
    ax.plot([p[0] for p in closed], [p[1] for p in closed],
            color=PRICE, linewidth=1.45, zorder=3)

    offsets = ((12, 0), (-12, 0), (9, -30), (-7, -31))
    alignments = ("left", "right", "left", "right")
    for (text, _, anchor), offset, alignment in zip(
            SHADOW_BOUNDARY_LABELS, offsets, alignments):
        ax.annotate(
            text, xy=tuple(map(float, anchor)), xytext=offset,
            textcoords="offset points", color=PRICE, fontsize=7.1,
            ha=alignment, va="center",
            bbox=dict(boxstyle="square,pad=0.16", facecolor=SURFACE,
                      edgecolor=PRICE, linewidth=0.55),
            arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.65),
            zorder=9,
        )

    ax.plot([float(SHADOW_TOP[0])], [float(SHADOW_TOP[1])], "o",
            color=PRICE, markeredgecolor=SURFACE, markeredgewidth=1.4,
            markersize=8, zorder=10)
    ax.annotate(
        f"top {point_label(SHADOW_TOP)}",
        xy=tuple(map(float, SHADOW_TOP)), xytext=(18, 10),
        textcoords="offset points", color=PRICE, fontsize=8,
        bbox=dict(boxstyle="square,pad=0.16", facecolor=SURFACE,
                  edgecolor=PRICE, linewidth=0.55),
        arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.65),
        zorder=11,
    )


def _draw_plan(ax):
    ax.clear()
    ax.set_xlim(-0.5, 22)
    ax.set_ylim(-0.5, 18)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks((0, 8, 16))
    ax.set_yticks((0, 8, 16))
    ax.tick_params(labelsize=7, colors=TEXT_DIM)
    ax.set_xlabel("t", color=TEXT_DIM, fontsize=8, labelpad=2)
    ax.set_ylabel("f", color=TEXT_DIM, fontsize=8, labelpad=2)
    ax.set_title("source plan", loc="left", color=TEXT, fontsize=8.5, pad=5)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color(TEXT_DIM)
    ax.grid(True, color=HAIRLINE, linewidth=0.6, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)

    polygon = [(float(t), float(f)) for t, f in MILL_POLYGON]
    closed = polygon + [polygon[0]]
    ax.fill([p[0] for p in polygon], [p[1] for p in polygon],
            color=PLAN, alpha=0.13, zorder=1)
    ax.plot([p[0] for p in closed], [p[1] for p in closed],
            color=PLAN, linewidth=1.25, zorder=3)
    ax.plot([float(PLAN_POINT[0])], [float(PLAN_POINT[1])], "o",
            color=PLAN, markeredgecolor=SURFACE, markeredgewidth=1.2,
            markersize=7, zorder=5)
    ax.annotate(
        f"({PLAN_POINT[0]}, {PLAN_POINT[1]})\nvalue {PLAN_VALUE}",
        xy=tuple(map(float, PLAN_POINT)), xytext=(8, 9),
        textcoords="offset points", color=PLAN, fontsize=7.2,
        bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE,
                  edgecolor=PLAN, linewidth=0.55),
        arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.6),
        zorder=7,
    )


def shadow_gif():
    fig, blank = figure(9.2, 6.8)
    fig.delaxes(blank)
    ax3d = fig.add_axes((0.08, 0.14, 0.84, 0.74), projection="3d")
    ax2d = fig.add_axes((0.32, 0.17, 0.64, 0.68))
    ax_plan = fig.add_axes((0.065, 0.32, 0.22, 0.38))
    ax2d.set_visible(False)
    ax_plan.set_visible(False)
    title = fig.text(0.07, 0.94, TITLE, fontsize=11, color=TEXT,
                     fontweight="semibold", ha="left")
    subtitle = fig.text(0.07, 0.895, "", fontsize=9.5, color=TEXT_DIM,
                        ha="left")
    note = margin_note(fig, y=0.045, size=8.5)

    def update(i):
        i = min(i, STAGES.total - 1)
        stage, progress = STAGES(i)
        if stage == 0:
            elevation, azimuth = 24, -55
            subtitle.set_text("the blue plans sit below the roof")
        elif stage == 1:
            elevation = 24 * (1 - progress)
            azimuth = -55 * (1 - progress)
            subtitle.set_text("turning the view along the t axis")
        elif stage == 2:
            elevation, azimuth = 0, 0
            subtitle.set_text("looking along t projects plans onto (f, v)")
        else:
            subtitle.set_text("the rust region is the shadow, cut at v = 0")

        if stage < 3:
            ax2d.set_visible(False)
            ax_plan.set_visible(False)
            ax3d.set_visible(True)
            _draw_3d(ax3d, elevation, azimuth)
            note.set_text(
                f"roof value at plan {point_label(PLAN_POINT)} = {PLAN_VALUE}"
            )
        else:
            ax3d.set_visible(False)
            ax2d.set_visible(True)
            ax_plan.set_visible(True)
            _draw_shadow(ax2d)
            _draw_plan(ax_plan)
            note.set_text("plan value and shadow height agree at the marked corner")
        return [title, subtitle, note]

    animate(fig, update, STAGES.total, OUT / "shadow.gif",
            fps=12, hold=3.0)


if __name__ == "__main__":
    shadow_gif()
