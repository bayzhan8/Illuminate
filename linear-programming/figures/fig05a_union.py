"""A contract's allowed plans are two pieces, not one region."""

from matplotlib.patches import Polygon

from illuminate.draw import (PLAN, PLAN_FILL, SURFACE, TEXT_DIM, WARN,
                             chapter_dir, figure, margin_note, save, tag)
from linprog import mill as mill
from linprog.lp import best_by_enumeration, vertices
from linprog.modeling import CONTRACT_MIN, semicontinuous, solve_binary
from scene import (claim, clip, draw_axes, fill, ordered)

OUT = chapter_dir("05-yes-or-no")
CONTRACT = CONTRACT_MIN


def point_mark(ax, point, label, color, dx, dy, marker="o"):
    ax.plot([float(point[0])], [float(point[1])], marker=marker, color=color,
            markersize=9, markeredgecolor=SURFACE, markeredgewidth=1.5,
            linestyle="none", zorder=8)
    tag(ax, float(point[0]) + dx, float(point[1]) + dy, label,
        color=color, size=8.5)


def union_still():
    feasible_poly = ordered(mill.MILL)
    cap = clip(feasible_poly, (0, 1), CONTRACT, keep_le=False)
    branches = semicontinuous()
    _, real_plan, real_value = solve_binary(branches)
    real_lp_value = mill.MILL.value(real_plan)
    relaxed_plan, relaxed_value = best_by_enumeration(mill.MILL)
    midpoint_source = next(point for point in vertices(mill.MILL)
                          if point[1] == 0 and point[0] > 0)
    midpoint = ((midpoint_source[0] + real_plan[0]) / 2,
                (midpoint_source[1] + real_plan[1]) / 2)

    fig, ax = figure(7.8, 6.5)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.83, bottom=0.19)
    draw_axes(ax)
    fill(ax, feasible_poly, TEXT_DIM, 0.08, z=1)
    ax.plot([p[0] for p in feasible_poly] + [feasible_poly[0][0]],
            [p[1] for p in feasible_poly] + [feasible_poly[0][1]],
            color=TEXT_DIM, linewidth=1.0, zorder=2)
    ax.add_patch(Polygon(cap, closed=True, facecolor=PLAN_FILL,
                         edgecolor=PLAN, alpha=0.22, linewidth=1.7, zorder=3))
    bottom = sorted((p for p in vertices(mill.MILL) if p[1] == 0),
                    key=lambda p: p[0])
    ax.plot([float(p[0]) for p in bottom], [0] * len(bottom),
            color=PLAN, linewidth=3.0, zorder=5)
    tag(ax, 8.5, 0.75, "f = 0: allowed", color=PLAN, size=8.7)
    tag(ax, 0.6, float(CONTRACT) + 0.5, "f ≥ 14: allowed",
        color=PLAN, size=8.7)

    ax.plot([float(midpoint_source[0]), float(real_plan[0])],
            [float(midpoint_source[1]), float(real_plan[1])],
            color=TEXT_DIM, linewidth=1.2, dashes=(4, 3), zorder=4)
    point_mark(ax, midpoint, "midpoint, not allowed", WARN,
               dx=0.6, dy=-0.45, marker="x")
    point_mark(ax, relaxed_plan, f"relaxation: {relaxed_value}, not real",
               WARN, dx=0.65, dy=0.7)
    point_mark(ax, real_plan, f"best real plan: {real_lp_value}",
               PLAN, dx=0.65, dy=0.7)

    claim(ax, "the contract divides the plans into two pieces",
          "the midpoint of two allowed plans need not be allowed")
    note = margin_note(fig, y=0.025, size=9.0)
    note.set_text(f"f = 0 or f ≥ {CONTRACT}     real optimum = {real_value}")
    return save(fig, OUT / "union.png", tight=False)


if __name__ == "__main__":
    union_still()
