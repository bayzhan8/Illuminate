"""The central path, drawn as the thing it is: a family of answers.

Every point on this curve is the exact optimum of a slightly different
problem, the one where walls repel you with strength mu. The method does not
approximate the LP and refine it. It solves a nearby problem exactly, then
makes the problem less nearby, and the trail of exact answers walks itself to
the one you asked for.
"""

import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, animate, chapter_dir, figure, heading,
                             margin_note, plate, save, tag)
from twopaths.barrier import Region, analytic_centre, central_path, centre_for

OUT = chapter_dir("11-the-central-path")

A = [[4, 2], [2, 3], [3, 1]]
B = [44, 30, 32]
PROFIT = [30, 20]
REGION = Region.build(A, B, PROFIT)
START = np.array([1.0, 1.0])
CORNERS = [(0, 0), (32 / 3, 0), (10, 2), (9, 4), (0, 10)]
WINDOW = (0, 12.6, 0, 11.6)
MU_FROM, MU_TO, POINTS = 8000.0, 1e-9, 110
MARKS = (1000.0, 100.0, 10.0, 1.0, 0.1)


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
    ax.plot([9], [4], "o", color=OK, markersize=9, zorder=9,
            markeredgecolor=SURFACE, markeredgewidth=2)


def path():
    return central_path(REGION, START, mu_from=MU_FROM, mu_to=MU_TO, points=POINTS)


def path_png():
    curve = path()
    centre = analytic_centre(REGION, START)
    fig, ax = figure(7.6, 5.2)
    fig.subplots_adjust(top=0.86, bottom=0.13, left=0.10, right=0.97)
    heading(ax, "one exact answer per setting of the repulsion")
    draw_region(ax)
    ax.plot(curve[:, 0], curve[:, 1], color=PRICE, linewidth=2.2, zorder=6)
    ax.plot([centre[0]], [centre[1]], "o", color=PRICE, markersize=7, zorder=8,
            markeredgecolor=SURFACE, markeredgewidth=1.6)
    plate(ax, centre[0] - 1.5, centre[1] - 1.15, "mu enormous: the point\n"
          "furthest from every wall", color=PRICE, size=9.5)
    # Each label sits beside the point it names. Placing them by eye put the
    # "mu = 10" caption next to the dot for mu = 100.
    labelled = {1000.0: (-1.15, 0.42), 10.0: (0.15, -0.95), 0.1: (0.3, 0.55)}
    for mu in MARKS:
        point = centre_for(REGION, mu, START)
        ax.plot([point[0]], [point[1]], "o", color=PRICE, markersize=5.5,
                zorder=8, markeredgecolor=SURFACE, markeredgewidth=1.4)
        if mu in labelled:
            dx, dy = labelled[mu]
            plate(ax, point[0] + dx, point[1] + dy, f"mu = {mu:g}", color=PRICE,
                  size=9.5)
    tag(ax, 2.6, 8.6, "the walls push, and the push weakens\n"
        "as mu shrinks towards nothing", color=TEXT_DIM, size=10)
    ax.annotate("mu = 0 would be here,\nand it never arrives", xy=(9, 4),
                xytext=(10.6, 7.4), fontsize=9.5, color=OK, ha="center",
                arrowprops=dict(arrowstyle="-", color=OK, linewidth=0.9,
                                shrinkA=4, shrinkB=8), zorder=9)
    save(fig, OUT / "the-path.png", tight=False)


def path_gif(fps=12):
    curve = path()
    mus = np.geomspace(MU_FROM, MU_TO, POINTS)

    fig, ax = figure(7.6, 5.4)
    fig.subplots_adjust(top=0.84, bottom=0.24, left=0.10, right=0.97)
    heading(ax, "turning the repulsion down")
    draw_region(ax)
    trail, = ax.plot([], [], color=PRICE, linewidth=2.2, zorder=6)
    head, = ax.plot([], [], "o", color=PRICE, markersize=8, zorder=8,
                    markeredgecolor=SURFACE, markeredgewidth=1.8)
    note = margin_note(fig, x=0.035, size=10.5)

    def update(i):
        at = min(i, POINTS - 1)
        trail.set_data(curve[:at + 1, 0], curve[:at + 1, 1])
        head.set_data([curve[at, 0]], [curve[at, 1]])
        worth = float(PROFIT[0] * curve[at, 0] + PROFIT[1] * curve[at, 1])
        room = REGION.slack(curve[at]).min()
        note.set_text(f"mu = {mus[at]:10.4g}    worth ${worth:8.2f}\n"
                      f"closest wall is still {room:.3g} away")
        note.set_color(TEXT)
        return []

    animate(fig, update, POINTS + 2, OUT / "the-path.gif", fps=fps, hold=3.2)


if __name__ == "__main__":
    path_png()
    path_gif()
