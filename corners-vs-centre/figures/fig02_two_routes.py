"""The central figure: the same problem, solved along the edge and through the middle.

Both routes start from nothing and end at 9 tables and 4 chairs. One of them
never leaves the boundary; the other never touches it. Drawing them on one copy
of the region is the entire argument of the guide, and everything else is
consequences of the difference.
"""

import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, animate, chapter_dir, figure, heading,
                             margin_note, save, tag)
from twopaths.barrier import Region, analytic_centre, central_path, centre_for
from twopaths.simplex import dantzig, solve

OUT = chapter_dir("02-two-routes")

A = [[4, 2], [2, 3], [3, 1]]
B = [44, 30, 32]
PROFIT = [30, 20]
REGION = Region.build(A, B, PROFIT)
START = np.array([1.0, 1.0])
WINDOW = (0, 12.6, 0, 11.6)
CORNERS = [(0, 0), (32 / 3, 0), (10, 2), (9, 4), (0, 10)]


def draw_region(ax):
    ax.set_xlim(*WINDOW[:2])
    ax.set_ylim(*WINDOW[2:])
    ax.set_xlabel("tables built", fontsize=10, color=TEXT_DIM, labelpad=6)
    ax.set_ylabel("chairs built", fontsize=10, color=TEXT_DIM, labelpad=6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)
    shape = sorted(CORNERS, key=lambda p: np.arctan2(
        p[1] - np.mean([q[1] for q in CORNERS]),
        p[0] - np.mean([q[0] for q in CORNERS])))
    ax.fill([p[0] for p in shape], [p[1] for p in shape], color=TEXT_FAINT,
            alpha=0.10, zorder=1, linewidth=0)
    ax.plot([p[0] for p in shape] + [shape[0][0]],
            [p[1] for p in shape] + [shape[0][1]],
            color=TEXT, linewidth=1.4, zorder=3)
    ax.plot([9], [4], "o", color=OK, markersize=10, zorder=9,
            markeredgecolor=SURFACE, markeredgewidth=2)
    return ax


def routes():
    walk = solve(PROFIT, A, B, rule=dantzig)
    vertices = np.array([[float(v) for v in p] for p in walk.visited])
    path = central_path(REGION, START, mu_from=8000.0, mu_to=1e-9, points=110)
    return vertices, path


def two_routes_png():
    vertices, path = routes()
    fig, ax = figure(7.6, 5.2)
    fig.subplots_adjust(top=0.86, bottom=0.13, left=0.11, right=0.97)
    heading(ax, "along the edge, and through the middle")
    draw_region(ax)

    ax.plot(path[:, 0], path[:, 1], color=PRICE, linewidth=2.2, zorder=6)
    ax.plot(vertices[:, 0], vertices[:, 1], color=PLAN, linewidth=2.2,
            zorder=7, marker="o", markersize=7, markeredgecolor=SURFACE,
            markeredgewidth=1.8)

    centre = analytic_centre(REGION, START)
    ax.plot([centre[0]], [centre[1]], "o", color=PRICE, markersize=6, zorder=8,
            markeredgecolor=SURFACE, markeredgewidth=1.6)

    ax.text(0.45, 6.9, f"{len(vertices) - 1} hops along the boundary,\n"
            "every one of them a corner", color=PLAN, fontsize=9.5, zorder=9,
            bbox=dict(boxstyle="square,pad=0.3", facecolor=SURFACE, edgecolor="none"))
    ax.text(3.4, 1.1, "a smooth curve through the inside,\n"
            "never touching a wall", color=PRICE, fontsize=9.5, zorder=9,
            bbox=dict(boxstyle="square,pad=0.3", facecolor=SURFACE, edgecolor="none"))
    ax.text(0.45, 2.55, "it starts here, the point\nfurthest from every wall",
            color=PRICE, fontsize=8.5, zorder=9,
            bbox=dict(boxstyle="square,pad=0.28", facecolor=SURFACE, edgecolor="none"))
    ax.annotate("both stop here", xy=(9, 4), xytext=(10.4, 6.6), fontsize=9.5,
                color=OK, ha="center",
                arrowprops=dict(arrowstyle="-", color=OK, linewidth=0.9,
                                shrinkA=4, shrinkB=8), zorder=9)
    save(fig, OUT / "two-routes.png", tight=False)


def two_routes_gif(fps=11):
    """Race them, so the difference in *kind* is unmissable."""
    vertices, path = routes()
    frames = 64

    fig, ax = figure(7.6, 5.2)
    fig.subplots_adjust(top=0.84, bottom=0.24, left=0.11, right=0.97)
    heading(ax, "the same problem, two ways of getting there")
    draw_region(ax)

    edge, = ax.plot([], [], color=PLAN, linewidth=2.2, zorder=7, marker="o",
                    markersize=7, markeredgecolor=SURFACE, markeredgewidth=1.8)
    inside, = ax.plot([], [], color=PRICE, linewidth=2.2, zorder=6)
    head, = ax.plot([], [], "o", color=PRICE, markersize=7, zorder=8,
                    markeredgecolor=SURFACE, markeredgewidth=1.8)
    note = margin_note(fig, x=0.04, size=10.5)

    hops = len(vertices) - 1
    per_hop = frames // (hops + 1)

    def update(i):
        i = min(i, frames - 1)
        taken = min(hops, i // per_hop)
        edge.set_data(vertices[:taken + 1, 0], vertices[:taken + 1, 1])
        k = min(len(path) - 1, int((i / (frames - 1)) * (len(path) - 1)))
        inside.set_data(path[:k + 1, 0], path[:k + 1, 1])
        head.set_data([path[k, 0]], [path[k, 1]])
        along = float(PROFIT[0] * vertices[taken, 0] + PROFIT[1] * vertices[taken, 1])
        through = float(PROFIT[0] * path[k, 0] + PROFIT[1] * path[k, 1])
        note.set_text(f"along the edge   corner {taken} of {hops}   ${along:,.2f}\n"
                      f"through the middle                ${through:,.2f}")
        note.set_color(TEXT)
        return []

    animate(fig, update, frames, OUT / "two-routes.gif", fps=fps, hold=3.2)


if __name__ == "__main__":
    two_routes_png()
    two_routes_gif()
