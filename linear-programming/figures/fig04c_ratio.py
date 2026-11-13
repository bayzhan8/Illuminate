"""A proportion rule is a wall through the origin."""

from matplotlib.patches import Polygon

from illuminate.draw import (HAIRLINE, PLAN, PLAN_FILL, SURFACE, TEXT_DIM,
                             WARN, chapter_dir, figure, margin_note, save, tag)
from linprog import mill as mill
from linprog.lp import best_by_enumeration
from linprog.modeling import ratio
from scene import claim, clip, draw_axes, draw_wall, fill, line_where, ordered

OUT = chapter_dir("04-more-rows")


def mark(ax, point, label, color, dx, dy, marker="o"):
    x, y = float(point[0]), float(point[1])
    cross = marker.lower() in {"x", "+"}
    ax.plot([x], [y], marker=marker, color=color,
            markersize=12 if cross else 9,
            markeredgecolor=color if cross else SURFACE,
            markeredgewidth=2.4 if cross else 1.5,
            linestyle="none", zorder=7)
    ax.text(x + dx, y + dy, label, color=color, fontsize=8.7,
            ha="left", va="center",
            bbox=dict(boxstyle="square,pad=0.18", facecolor=SURFACE,
                      edgecolor=HAIRLINE, linewidth=0.6),
            zorder=9)


def ratio_still():
    lp = ratio()
    best, value = best_by_enumeration(lp)
    fig, ax = figure(7.5, 6.5)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.83, bottom=0.19)
    draw_axes(ax)
    mill_poly = ordered(mill.MILL)
    fill(ax, mill_poly, TEXT_DIM, 0.07, z=1)
    cut = clip(mill_poly, lp.A[-1], lp.b[-1], keep_le=False)
    ax.add_patch(Polygon(cut, closed=True, facecolor=WARN, edgecolor=WARN,
                         alpha=0.12, hatch="////", linewidth=0.8, zorder=2))
    valid = clip(mill_poly, lp.A[-1], lp.b[-1])
    ax.add_patch(Polygon(valid, closed=True, facecolor=PLAN_FILL,
                         edgecolor=PLAN, alpha=0.18, linewidth=1.7, zorder=3))
    draw_wall(ax, 0, color=TEXT_DIM, lw=1.1)
    draw_wall(ax, 1, color=TEXT_DIM, lw=1.1)
    line_where(ax, lp.A[-1], lp.b[-1], color=TEXT_DIM, linewidth=1.5, zorder=4)
    ax.text(18.0, 14.7, f"{lp.A[-1][1]}f = {-lp.A[-1][0]}t",
            color=TEXT_DIM, fontsize=8.8, ha="left", va="center",
            bbox=dict(boxstyle="square,pad=0.18", facecolor=SURFACE,
                      edgecolor=HAIRLINE, linewidth=0.6),
            zorder=9)

    mark(ax, best, f"best ({best[0]}, {best[1]}): {value}",
         PLAN, dx=1.1, dy=2.8)
    old = mill.BEST
    mark(ax, old, f"cut off ({old[0]}, {old[1]}): {mill.MILL.value(old)}",
         WARN, dx=0.65, dy=1.1, marker="x")
    ax.plot([0], [0], "o", color=TEXT_DIM, markersize=5.5, zorder=7)
    tag(ax, 1.1, 2.5, "0 of 0: passes; ratio undefined", color=TEXT_DIM, size=8.2)

    claim(ax, "the proportion wall cuts off the old best plan",
          "at least three in five must be 3-ply")
    note = margin_note(fig, y=0.025, size=9.0)
    note.set_text(f"3f − 2t ≤ 0     best value = {value}")
    return save(fig, OUT / "ratio.png", tight=False)


if __name__ == "__main__":
    ratio_still()
