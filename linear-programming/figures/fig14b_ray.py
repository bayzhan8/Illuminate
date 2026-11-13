"""Show the unbounded edge revealed by a missing machine constraint."""

from fractions import Fraction as Q
import math

from matplotlib.patches import Polygon

from illuminate.draw import (PLAN, PRICE, SURFACE, TEXT, TEXT_DIM, save,
                             chapter_dir, figure, style)
from linprog.lp import LP, vertices
from linprog.simplex import simplex

OUT = chapter_dir("14-simplex")
TITLE = "A positive reduced cost with no limiting row"
VARIABLES = ("t", "f", "s")
A = ((Q(-1), Q(1), Q(1)),)
B = (Q(4),)
C = (Q(3), Q(5), Q(0))
BASIS = (1,)
RESULT = simplex(A, B, C, BASIS)
BASE_POINT = RESULT.steps[0].x[:2]
RAY_DIRECTION = RESULT.certificate[:2]
RAY_LABEL_ANCHOR = tuple(
    BASE_POINT[i] + 4 * RAY_DIRECTION[i] for i in range(2)
)
WALL_LABEL_ANCHOR = RAY_LABEL_ANCHOR
RAY_END = tuple(BASE_POINT[i] + 8 * RAY_DIRECTION[i] for i in range(2))
REDUCED_COST_T = RESULT.steps[0].dictionary.reduced_costs[0]
COLUMN_T = RESULT.steps[0].dictionary.rows[0][0]


def _region():
    lp = LP.build(
        c=(0, 0),
        A=((Q(-1), Q(1)), (Q(1), Q(0)), (Q(0), Q(1))),
        b=(Q(4), Q(10), Q(14)),
    )
    points = [(float(t), float(f)) for t, f in vertices(lp)]
    center = (sum(t for t, _ in points) / len(points),
              sum(f for _, f in points) / len(points))
    return sorted(points, key=lambda point: math.atan2(
        point[1] - center[1], point[0] - center[0]
    ))


REGION = _region()


def dictionary_text():
    step = RESULT.steps[0]
    state = step.dictionary
    variables = ("t", "f", "s")
    nonbasic = tuple(index for index in range(len(variables))
                     if index not in step.basis)

    def terms(coefficients):
        out = ""
        for variable, coefficient in zip(
                (variables[index] for index in nonbasic), coefficients):
            if coefficient == 0:
                continue
            sign = "+" if coefficient > 0 else "−"
            amount = abs(coefficient)
            prefix = "" if amount == 1 else str(amount)
            out += f" {sign} {prefix}{variable}"
        return out

    basic_lines = tuple(
        f"{variables[basic]} = {step.dictionary.x_B[row]}"
        + terms(tuple(-state.rows[row][column] for column in nonbasic))
        for row, basic in enumerate(step.basis)
    )
    return "\n".join(
        basic_lines + (
            f"z = {step.value}"
            + terms(tuple(state.reduced_costs[column]
                          for column in nonbasic)),
        )
    )


def ray_figure():
    fig, empty_ax = figure(10.4, 5.6)
    fig.delaxes(empty_ax)
    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.16, top=0.81)
    ax = fig.add_axes((0.08, 0.18, 0.47, 0.59))
    panel = fig.add_axes((0.62, 0.22, 0.32, 0.51))
    fig.text(0.08, 0.96, TITLE, fontsize=11, color=TEXT,
             fontweight="semibold", ha="left")

    style(ax, xlabel="3-ply batches t", ylabel="5-ply batches f")
    ax.set_xlim(-0.7, 10)
    ax.set_ylim(-0.7, 14)
    ax.set_aspect("equal", adjustable="box")
    ax.add_patch(Polygon(REGION, closed=True, facecolor=PLAN, alpha=0.12,
                         edgecolor="none", zorder=1))
    ax.plot([0, 10], [4, 14], color=TEXT_DIM, linewidth=1.1, zorder=2)
    ax.axhline(0, color=TEXT_DIM, linewidth=0.9, zorder=2)
    ax.axvline(0, color=TEXT_DIM, linewidth=0.9, zorder=2)
    ax.annotate(
        "f − t = 4", xy=tuple(map(float, WALL_LABEL_ANCHOR)),
        xytext=(9, -17), textcoords="offset points", color=TEXT_DIM,
        fontsize=7.4,
        bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                  edgecolor=TEXT_DIM, linewidth=0.4), zorder=7,
    )
    ax.plot([0, float(BASE_POINT[0])], [0, float(BASE_POINT[1])],
            color=PLAN, linewidth=1.8, zorder=4)
    ax.annotate(
        "", xy=tuple(map(float, RAY_END)), xytext=tuple(map(float, BASE_POINT)),
        arrowprops=dict(arrowstyle="-|>", color=PRICE, linewidth=2.0,
                        mutation_scale=15), zorder=6,
    )
    ax.plot([float(BASE_POINT[0])], [float(BASE_POINT[1])], "o",
            color=PLAN, markersize=8, markeredgecolor=SURFACE,
            markeredgewidth=1.2, zorder=8)
    ax.annotate(
        "(0, 4)", xy=tuple(map(float, BASE_POINT)), xytext=(8, 7),
        textcoords="offset points", color=PLAN, fontsize=7.4,
        bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                  edgecolor=PLAN, linewidth=0.4), zorder=9,
    )
    ax.annotate(
        "extreme ray: (1, 1), +8 per unit",
        xy=tuple(map(float, RAY_LABEL_ANCHOR)), xytext=(11, 11),
        textcoords="offset points", color=PRICE, fontsize=7.4,
        arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.6),
        bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                  edgecolor=PRICE, linewidth=0.4), zorder=9,
    )

    panel.axis("off")
    panel.text(0, 1, "DICTIONARY AT (0, 4)", transform=panel.transAxes,
               va="top", fontsize=8, color=TEXT_DIM, family="monospace")
    panel.text(
        0, 0.83, dictionary_text(),
        transform=panel.transAxes, va="top", fontsize=10,
        color=PRICE, family="monospace",
        bbox=dict(boxstyle="square,pad=0.5", facecolor=SURFACE,
                  edgecolor=PRICE, linewidth=0.7),
    )
    panel.text(0, 0.58, "entering column of t", transform=panel.transAxes,
               va="top", fontsize=8, color=TEXT_DIM)
    panel.text(
        0, 0.42, f"B⁻¹Aₜ = {COLUMN_T}",
        transform=panel.transAxes, va="top", fontsize=10,
        color=PRICE if COLUMN_T <= 0 else TEXT, family="monospace",
        bbox=dict(boxstyle="square,pad=0.45", facecolor=SURFACE,
                  edgecolor=PRICE if COLUMN_T <= 0 else TEXT_DIM,
                  linewidth=0.7),
    )
    panel.text(
        0, 0.18,
        f"reduced cost = +{REDUCED_COST_T}; no positive ratio",
        transform=panel.transAxes, va="top", fontsize=7.7, color=TEXT_DIM,
    )
    fig.text(0.62, 0.10, "No row stops the ray.", fontsize=9.0, color=PRICE,
             fontweight="semibold")
    save(fig, OUT / "ray.png", tight=False)


if __name__ == "__main__":
    ray_figure()
