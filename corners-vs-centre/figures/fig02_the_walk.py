"""The walk itself, with the arithmetic that produces it shown alongside.

A picture of a path along the edge of a shape is pretty and teaches nothing
about why the path goes where it does. What decides each hop is a row of
numbers: how much the objective still improves per unit of each product, and
how far the plan can move before some rule runs out. Putting the numbers next
to the point is the whole lesson of the chapter.
"""

import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, animate, chapter_dir, figure, heading,
                             plate, save)
from twopaths.simplex import dantzig, solve

OUT = chapter_dir("02-along-the-edge")

A = [[4, 2], [2, 3], [3, 1]]
B = [44, 30, 32]
PROFIT = [30, 20]
CORNERS = [(0, 0), (32 / 3, 0), (10, 2), (9, 4), (0, 10)]
WINDOW = (0, 12.6, 0, 11.6)
RULES = ("planks", "labour", "saw")


def walk():
    return solve(PROFIT, A, B, rule=dantzig)


def draw_region(ax):
    ax.set_xlim(*WINDOW[:2])
    ax.set_ylim(*WINDOW[2:])
    ax.set_xlabel("tables", fontsize=10, color=TEXT_DIM, labelpad=5)
    ax.set_ylabel("chairs", fontsize=10, color=TEXT_DIM, labelpad=5)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)
    middle = np.mean(CORNERS, axis=0)
    shape = sorted(CORNERS, key=lambda p: np.arctan2(p[1] - middle[1], p[0] - middle[0]))
    ax.fill([p[0] for p in shape], [p[1] for p in shape], color=TEXT_FAINT,
            alpha=0.10, zorder=1, linewidth=0)
    ax.plot([p[0] for p in shape] + [shape[0][0]],
            [p[1] for p in shape] + [shape[0][1]],
            color=TEXT, linewidth=1.4, zorder=3)
    for point in CORNERS:
        ax.plot([point[0]], [point[1]], "o", color=TEXT_FAINT, markersize=5,
                zorder=4, markeredgecolor=SURFACE, markeredgewidth=1.4)


def _slack(point):
    return [B[i] - A[i][0] * point[0] - A[i][1] * point[1] for i in range(3)]


def _story(point, index, total):
    """What is true at this corner: what is used up, and what it is worth."""
    room = _slack(point)
    tight = [RULES[i] for i, r in enumerate(room) if abs(r) < 1e-9]
    if point[0] < 1e-9 and point[1] < 1e-9:
        tight = ["build nothing"]
    worth = PROFIT[0] * point[0] + PROFIT[1] * point[1]
    lines = [f"corner {index} of {total}",
             f"   {point[0]:.4g} tables, {point[1]:.4g} chairs",
             f"   worth ${worth:,.2f}",
             f"   used up: {', '.join(tight) if tight else 'nothing'}"]
    return "\n".join(lines), worth


def walk_png():
    result = walk()
    points = [(float(a), float(b)) for a, b in result.visited]
    fig, ax = figure(7.6, 5.2)
    fig.subplots_adjust(top=0.86, bottom=0.13, left=0.10, right=0.97)
    heading(ax, "three hops, and it never leaves the boundary")
    draw_region(ax)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.plot(xs, ys, color=PLAN, linewidth=2.2, zorder=7, marker="o",
            markersize=8, markeredgecolor=SURFACE, markeredgewidth=1.8)
    ax.plot([9], [4], "o", color=OK, markersize=10, zorder=9,
            markeredgecolor=SURFACE, markeredgewidth=2)
    for index, point in enumerate(points):
        worth = PROFIT[0] * point[0] + PROFIT[1] * point[1]
        offset = (0.45, 0.45) if index else (0.45, 0.3)
        plate(ax, point[0] + offset[0], point[1] + offset[1],
              f"${worth:,.0f}", color=PLAN if index < len(points) - 1 else OK,
              size=10.5)
    save(fig, OUT / "the-walk.png", tight=False)


def walk_gif(fps=1.5):
    result = walk()
    points = [(float(a), float(b)) for a, b in result.visited]
    hops = len(points) - 1

    fig, ax = figure(7.6, 5.4)
    fig.subplots_adjust(top=0.83, bottom=0.30, left=0.10, right=0.97)
    heading(ax, "what the method knows at each corner")
    draw_region(ax)
    trail, = ax.plot([], [], color=PLAN, linewidth=2.2, zorder=7, marker="o",
                     markersize=8, markeredgecolor=SURFACE, markeredgewidth=1.8)
    here, = ax.plot([], [], "o", color=PLAN, markersize=11, zorder=9,
                    markeredgecolor=SURFACE, markeredgewidth=2)
    caption = fig.text(0.035, 0.035, "", ha="left", va="bottom", fontsize=10.5,
                       color=TEXT, family="monospace", linespacing=1.55)

    def update(i):
        at = min(i, hops)
        trail.set_data([p[0] for p in points[:at + 1]], [p[1] for p in points[:at + 1]])
        here.set_data([points[at][0]], [points[at][1]])
        here.set_color(OK if at == hops else PLAN)
        text, _ = _story(points[at], at, hops)
        if at == hops:
            text += "\n   nothing improves it: this is the answer"
        else:
            text += "\n   something still improves: hop again"
        caption.set_text(text)
        return []

    animate(fig, update, hops + 2, OUT / "the-walk.gif", fps=fps, hold=3.4)


if __name__ == "__main__":
    walk_png()
    walk_gif()
