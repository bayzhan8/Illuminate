"""A small off-bound deletes the true best plan."""

from matplotlib.patches import Polygon

from illuminate.draw import (PLAN, PLAN_FILL, SURFACE, TEXT_DIM, WARN,
                             chapter_dir, figure, margin_note, save, tag)
from linprog import mill as mill
from linprog.lp import best_by_enumeration
from linprog.modeling import EITHER_OR_LIMIT, either_or, solve_binary
from scene import claim, clip, draw_axes, fill, ordered

OUT = chapter_dir("05-yes-or-no")
M1 = max(point[0] for point in mill.CORNERS) - EITHER_OR_LIMIT
M2 = max(point[1] for point in mill.CORNERS) - EITHER_OR_LIMIT
BAD_M2 = EITHER_OR_LIMIT


def mark(ax, point, label, color, dx, dy, marker="o"):
    ax.plot([float(point[0])], [float(point[1])], marker=marker, color=color,
            markersize=9, markeredgecolor=SURFACE, markeredgewidth=1.5,
            linestyle="none", zorder=8)
    tag(ax, float(point[0]) + dx, float(point[1]) + dy, label,
        color=color, size=8.2)


def either_or_still():
    valid_branches = either_or(M1, M2)
    _, best_left, left_value = solve_binary(valid_branches)
    _, best_bottom, bottom_value = (
        valid_branches[1], *best_by_enumeration(valid_branches[1].lp)
    )
    bad_branch = either_or(M1, BAD_M2)[0]
    bad_point, bad_value = best_by_enumeration(bad_branch.lp)
    left_poly = ordered(valid_branches[0].lp)
    bottom_poly = ordered(valid_branches[1].lp)
    removed = clip(left_poly, (0, 1), BAD_M2 + 6, keep_le=False)

    fig, ax = figure(8.0, 6.6)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.83, bottom=0.19)
    draw_axes(ax)
    mill_poly = ordered(mill.MILL)
    fill(ax, mill_poly, TEXT_DIM, 0.07, z=1)
    ax.add_patch(Polygon(left_poly, closed=True, facecolor=PLAN_FILL,
                         edgecolor=PLAN, alpha=0.2, linewidth=1.5, zorder=3))
    ax.add_patch(Polygon(bottom_poly, closed=True, facecolor=PLAN_FILL,
                         edgecolor=PLAN, alpha=0.2, linewidth=1.5, zorder=3))

    wrong_level = BAD_M2 + 6
    ax.axhline(float(wrong_level), color=WARN, linewidth=1.8,
               dashes=(5, 3), zorder=4)
    ax.add_patch(Polygon(removed, closed=True, facecolor="none",
                         edgecolor=WARN, hatch="////", linewidth=0.9, zorder=5))
    tag(ax, 7.1, float(wrong_level) + 0.65,
        f"M2 = {BAD_M2}: f ≤ {wrong_level} when switched off",
        color=WARN, size=8.1)

    mark(ax, best_left, f"left rule: ({best_left[0]}, {best_left[1]}), {left_value}",
         PLAN, dx=0.7, dy=1.1)
    mark(ax, best_bottom,
         f"bottom rule: ({best_bottom[0]}, {best_bottom[1]}), {bottom_value}",
         PLAN, dx=0.7, dy=-1.05)
    mark(ax, bad_point, f"wrong model: ({bad_point[0]}, {bad_point[1]}), {bad_value}",
         WARN, dx=0.7, dy=-0.8)

    claim(ax, "the wrong M cuts off the best plan",
          "the switched-off row must be loose enough for every mill plan")
    note = margin_note(fig, y=0.025, size=8.9)
    note.set_text(f"valid M1 = {M1}, M2 = {M2}     too-small M2 = {BAD_M2}")
    return save(fig, OUT / "either_or.png", tight=False)


if __name__ == "__main__":
    either_or_still()
