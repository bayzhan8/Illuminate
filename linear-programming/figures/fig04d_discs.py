"""The inside and outside discs stop at different walls."""

import math

from matplotlib.patches import Circle

from illuminate.draw import (PLAN, PLAN_FILL, PRICE, PRICE_FILL, SURFACE,
                             TEXT_DIM, chapter_dir, figure, margin_note, save,
                             tag)
from linprog import mill as f
from scene import claim, draw_axes, draw_region, draw_wall, norm, unit

OUT = chapter_dir("04-more-rows")
LATHE = tuple(float(v) for v in f.MILL.A[0])
PRESS = tuple(float(v) for v in f.MILL.A[1])
LATHE_LIMIT = float(f.MILL.b[0])
PRESS_LIMIT = float(f.MILL.b[1])
LATHE_NORM = norm(LATHE)
PRESS_NORM = norm(PRESS)
INSIDE_RADIUS = PRESS_LIMIT / (sum(PRESS) + PRESS_NORM)
OUTSIDE_RADIUS = LATHE_LIMIT / (sum(LATHE) + LATHE_NORM)


def add_touch(ax, point, color, marker="o", size=8):
    ax.plot([point[0]], [point[1]], marker, color=color,
            markeredgecolor=SURFACE, markeredgewidth=1.4,
            markersize=size, zorder=10, clip_on=False)


def discs_still():
    fig, ax = figure(8.1, 6.7)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.83, bottom=0.19)
    draw_axes(ax)
    draw_region(ax, alpha=0.08)
    draw_wall(ax, 0, color=TEXT_DIM, lw=1.3)
    draw_wall(ax, 1, color=TEXT_DIM, lw=1.3)
    tag(ax, 20.4, 6.25, "lathe wall", color=TEXT_DIM, size=8.8)
    tag(ax, 2.0, 18.05, "press wall", color=TEXT_DIM, size=8.8)

    inside_center = (INSIDE_RADIUS, INSIDE_RADIUS)
    outside_center = (OUTSIDE_RADIUS, OUTSIDE_RADIUS)
    ax.add_patch(Circle(outside_center, OUTSIDE_RADIUS, facecolor=PRICE_FILL,
                        edgecolor=PRICE, linewidth=2.0, alpha=0.12, zorder=4))
    ax.add_patch(Circle(inside_center, INSIDE_RADIUS, facecolor=PLAN_FILL,
                        edgecolor=PLAN, linewidth=2.0, alpha=0.2, zorder=5))
    for touch in ((0, inside_center[1]), (inside_center[0], 0)):
        add_touch(ax, touch, PLAN, marker="o", size=8)
    for touch in ((0, outside_center[1]), (outside_center[0], 0)):
        add_touch(ax, touch, PRICE, marker="s", size=8)
    add_touch(ax, inside_center, PLAN, marker="o", size=7.5)
    add_touch(ax, outside_center, PRICE, marker="s", size=7.5)

    press_unit = unit(PRESS)
    inside_press_touch = (
        inside_center[0] + INSIDE_RADIUS * press_unit[0],
        inside_center[1] + INSIDE_RADIUS * press_unit[1],
    )
    add_touch(ax, inside_press_touch, PLAN, size=9)

    lathe_unit = unit(LATHE)
    outside_lathe_touch = (
        outside_center[0] + OUTSIDE_RADIUS * lathe_unit[0],
        outside_center[1] + OUTSIDE_RADIUS * lathe_unit[1],
    )
    add_touch(ax, outside_lathe_touch, PRICE, size=9)

    press_foot_scale = (PRESS_LIMIT - sum(PRESS[i] * outside_center[i]
                                          for i in range(2))) / sum(v * v for v in PRESS)
    press_foot = (
        outside_center[0] + press_foot_scale * PRESS[0],
        outside_center[1] + press_foot_scale * PRESS[1],
    )
    ax.plot([outside_center[0], press_foot[0]],
            [outside_center[1], press_foot[1]], color=TEXT_DIM,
            linewidth=1.2, dashes=(3, 2), zorder=8)
    add_touch(ax, press_foot, TEXT_DIM, marker="o", size=5.5)
    press_distance = math.dist(outside_center, press_foot)
    tag(ax, 13.0, 8.4,
        f"press cuts {press_distance:.2f} from centre",
        color=TEXT_DIM, size=8.2)

    tag(ax, 1.0, 11.7, f"inside, r = {INSIDE_RADIUS:.2f}",
        color=PLAN, size=8.7)
    tag(ax, 1.0, 13.3, f"reaching, r = {OUTSIDE_RADIUS:.2f}",
        color=PRICE, size=8.7)
    tag(ax, 13.0, 14.3,
        f"inside centre ({INSIDE_RADIUS:.2f}, {INSIDE_RADIUS:.2f})",
        color=PLAN, size=8.0)
    tag(ax, 13.0, 15.5,
        f"reaching centre ({OUTSIDE_RADIUS:.2f}, {OUTSIDE_RADIUS:.2f})",
        color=PRICE, size=8.0)
    tag(ax, 13.0, 10.3, "inside disc touches press", color=PLAN, size=8.0)
    tag(ax, 13.0, 12.1, "reaching disc touches lathe", color=PRICE, size=8.0)

    claim(ax, "the inside and outside discs stop at different walls",
          "one must avoid every wall; the other must reach every wall")
    note = margin_note(fig, y=0.025, size=8.9)
    note.set_text("blue: largest disc inside     rust: smallest disc reaching all four walls")
    return save(fig, OUT / "two_discs.png", tight=False)


if __name__ == "__main__":
    discs_still()
