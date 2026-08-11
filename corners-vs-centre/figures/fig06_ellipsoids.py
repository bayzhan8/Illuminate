"""The polynomial method, doing its guaranteed and unimpressive work.

Each frame throws away a little under a quarter of the area and knows nothing
else. There is no sense in which it is closing in on the answer: it is
shrinking a container, and the answer happens to be inside. That is exactly
why the bound is provable and exactly why nobody wanted to run it.
"""

import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, animate, chapter_dir, figure, heading,
                             margin_note, save, tag)
from twopaths.ellipsoid import run, shrink_factor

OUT = chapter_dir("06-polynomial-and-slower")

A = np.array([[4.0, 2.0], [2.0, 3.0], [3.0, 1.0]])
B = np.array([44.0, 30.0, 32.0])
PROFIT = np.array([30.0, 20.0])
TARGET = 349.0
CORNERS = [(0, 0), (32 / 3, 0), (10, 2), (9, 4), (0, 10)]
START = np.array([6.0, 6.0])
RADIUS = 20.0
WINDOW = (-13, 26, -11, 24)


def history():
    walls = np.vstack([A, -np.eye(2), -PROFIT])
    limits = np.concatenate([B, [0.0, 0.0], [-TARGET]])
    return run(walls, limits, START, radius=RADIUS, steps=400)


def _outline(step, points=200):
    angles = np.linspace(0, 2 * np.pi, points)
    circle = np.stack([np.cos(angles), np.sin(angles)])
    root = np.linalg.cholesky(step.shape + np.eye(2) * 1e-15)
    return (step.centre[:, None] + root @ circle).T


def draw_region(ax):
    ax.set_xlim(*WINDOW[:2])
    ax.set_ylim(*WINDOW[2:])
    ax.set_aspect("equal")
    ax.set_xlabel("tables", fontsize=10, color=TEXT_DIM, labelpad=5)
    ax.set_ylabel("chairs", fontsize=10, color=TEXT_DIM, labelpad=5)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.6, linestyle=(0, (1, 4)))
    ax.set_axisbelow(True)
    middle = np.mean(CORNERS, axis=0)
    shape = sorted(CORNERS, key=lambda p: np.arctan2(p[1] - middle[1], p[0] - middle[0]))
    ax.fill([p[0] for p in shape], [p[1] for p in shape], color=TEXT_FAINT,
            alpha=0.12, zorder=2, linewidth=0)
    ax.plot([p[0] for p in shape] + [shape[0][0]],
            [p[1] for p in shape] + [shape[0][1]],
            color=TEXT, linewidth=1.3, zorder=3)
    ax.plot([9], [4], "o", color=OK, markersize=8, zorder=9,
            markeredgecolor=SURFACE, markeredgewidth=1.8)



def ellipsoids_gif(fps=9):
    steps = history()
    guaranteed = shrink_factor(2)

    fig, ax = figure(7.0, 5.8)
    fig.subplots_adjust(top=0.85, bottom=0.20, left=0.10, right=0.97)
    heading(ax, "every cut removes about a fifth, and nothing more")
    draw_region(ax)
    shell, = ax.plot([], [], color=PRICE, linewidth=2.0, zorder=7)
    ghost, = ax.plot([], [], color=PRICE, linewidth=0.8, alpha=0.30, zorder=6)
    middle, = ax.plot([], [], "o", color=PRICE, markersize=6, zorder=8,
                      markeredgecolor=SURFACE, markeredgewidth=1.5)
    note = margin_note(fig, x=0.035, size=10.5)
    trail = []

    def update(i):
        at = min(i, len(steps) - 1)
        curve = _outline(steps[at])
        shell.set_data(curve[:, 0], curve[:, 1])
        middle.set_data([steps[at].centre[0]], [steps[at].centre[1]])
        if at and (at not in trail):
            trail.append(at)
        first = _outline(steps[0])
        ghost.set_data(first[:, 0], first[:, 1])
        ratio = steps[at].volume / steps[0].volume
        done = steps[at].cut is None
        note.set_text(
            f"cut {at} of {len(steps) - 1}    area left: {100 * ratio:6.2f}% of the start\n"
            + ("the centre is finally a legal plan"
               if done else
               f"the centre breaks a rule, so half the ellipsoid goes"))
        note.set_color(OK if done else TEXT)
        middle.set_color(OK if done else PRICE)
        return []

    animate(fig, update, len(steps) + 1, OUT / "ellipsoids.gif", fps=fps, hold=3.2)


if __name__ == "__main__":
    ellipsoids_gif()
