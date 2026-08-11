"""Chapters 4 and 5: the same iteration, one term apart, drawn as a trajectory.

The toy problem is one variable and one equality, so the whole state is a plan
and a price: two numbers, one plane, one path. That is the only reason this
picture is possible, and it is worth saying in the chapter, because the
behaviour it shows is not special to one dimension.

Left panel: the prices react to where the plan *was*. The path winds outward.
Right panel: the prices react to where the plan is *going*, which is the single
changed term. The path winds inward to the answer.
"""

import numpy as np

from firstorder import story as s
from firstorder.methods import Problem, gradient_descent_ascent, pdhg
from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, animate, chapter_dir, figure, heading,
                             margin_note, save, tag)

OUT_GDA = chapter_dir("07-the-obvious-version")
OUT_PDHG = chapter_dir("08-one-term-different")

# a single equality x = 3, so the state is (plan, price) and lives in a plane
STEP = 0.2
ANSWER = (3.0, 0.0)
START = (2.0, 2.0)
STEPS = 90


def walk(extrapolate: bool):
    """Both methods by hand, so the one differing term is visible in the source."""
    x, y = START
    path = [(x, y)]
    for _ in range(STEPS):
        x_new = x + STEP * y                      # no objective, no clamp needed
        lead = 2 * x_new - x if extrapolate else x
        y = y - STEP * (lead - 3.0)
        x = x_new
        path.append((x, y))
    return np.array(path)


def draw_plane(ax, title, path, colour, limit):
    heading(ax, title)
    ax.set_xlim(3 - limit, 3 + limit)
    ax.set_ylim(-limit, limit)
    ax.set_xlabel("the plan", fontsize=10, color=TEXT_DIM, labelpad=6)
    ax.set_ylabel("the price", fontsize=10, color=TEXT_DIM, labelpad=6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)
    ax.plot([ANSWER[0]], [ANSWER[1]], "o", color=OK, markersize=9, zorder=8,
            markeredgecolor=SURFACE, markeredgewidth=2)
    ax.annotate("the answer", xy=ANSWER, xytext=(3 + limit * 0.30, limit * 0.34),
                fontsize=9.5, color=OK, ha="center",
                arrowprops=dict(arrowstyle="-", color=OK, linewidth=0.9,
                                shrinkA=4, shrinkB=8))
    return ax


def spiral_gif(fps=13):
    import matplotlib.pyplot as plt

    out_path, in_path = walk(False), walk(True)
    limit = 13.0

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.8, 4.7))
    fig.subplots_adjust(left=0.08, right=0.97, bottom=0.24, top=0.84, wspace=0.26)
    draw_plane(axL, "the prices chase where the plan was", out_path, PRICE, limit)
    draw_plane(axR, "the prices anticipate where it is going", in_path, PLAN, limit)

    trail_out, = axL.plot([], [], color=PRICE, linewidth=1.5, zorder=5)
    head_out, = axL.plot([], [], "o", color=PRICE, markersize=6, zorder=7,
                         markeredgecolor=SURFACE, markeredgewidth=1.5)
    trail_in, = axR.plot([], [], color=PLAN, linewidth=1.5, zorder=5)
    head_in, = axR.plot([], [], "o", color=PLAN, markersize=6, zorder=7,
                        markeredgecolor=SURFACE, markeredgewidth=1.5)
    note = margin_note(fig, x=0.05, size=10.5)

    def update(i):
        i = min(i, STEPS)
        trail_out.set_data(out_path[:i + 1, 0], out_path[:i + 1, 1])
        head_out.set_data([out_path[i, 0]], [out_path[i, 1]])
        trail_in.set_data(in_path[:i + 1, 0], in_path[:i + 1, 1])
        head_in.set_data([in_path[i, 0]], [in_path[i, 1]])
        far_out = np.hypot(*(out_path[i] - np.array(ANSWER)))
        far_in = np.hypot(*(in_path[i] - np.array(ANSWER)))
        note.set_text(f"step {i:>3}      distance from the answer:"
                      f"   chasing {far_out:6.2f}      anticipating {far_in:6.2f}")
        note.set_color(TEXT)
        return []

    animate(fig, update, STEPS + 1, OUT_PDHG / "spiral.gif", fps=fps, hold=3.2)


def outward_png():
    fig, ax = figure(6.4, 5.2)
    fig.subplots_adjust(top=0.86, bottom=0.13, left=0.14, right=0.96)
    path = walk(False)
    draw_plane(ax, "winding outward", path, PRICE, 13.0)
    ax.plot(path[:, 0], path[:, 1], color=PRICE, linewidth=1.5, zorder=5)
    ax.plot([START[0]], [START[1]], "o", color=TEXT, markersize=6, zorder=7)
    tag(ax, START[0] + 0.5, START[1] + 0.4, "start", color=TEXT, size=9.5)
    far = np.hypot(*(path[-1] - np.array(ANSWER)))
    ax.text(3 - 12, -11.4,
            f"after {STEPS} steps it is {far:.1f} away,\n"
            f"having started {np.hypot(*(np.array(START) - np.array(ANSWER))):.1f} away",
            color=TEXT_DIM, fontsize=9.5, va="bottom", zorder=9,
            bbox=dict(boxstyle="square,pad=0.35", facecolor=SURFACE,
                      edgecolor="none"))
    save(fig, OUT_GDA / "outward.png", tight=False)


def inward_png():
    fig, ax = figure(6.4, 5.2)
    fig.subplots_adjust(top=0.86, bottom=0.13, left=0.14, right=0.96)
    path = walk(True)
    draw_plane(ax, "winding inward", path, PLAN, 2.6)
    ax.plot(path[:, 0], path[:, 1], color=PLAN, linewidth=1.5, zorder=5)
    ax.plot([START[0]], [START[1]], "o", color=TEXT, markersize=6, zorder=7)
    tag(ax, START[0] + 0.1, START[1] + 0.16, "start", color=TEXT, size=9.5)
    far = np.hypot(*(path[-1] - np.array(ANSWER)))
    ax.text(3 - 2.45, -2.32,
            f"after {STEPS} steps it is {far:.2f} away.\n"
            f"it turns {s.SPIRAL['rotation_degrees']:.1f}° per step\n"
            f"and shrinks by only {(1 - s.SPIRAL['contraction']) * 100:.1f}%",
            color=TEXT_DIM, fontsize=9.5, va="bottom", zorder=9,
            bbox=dict(boxstyle="square,pad=0.35", facecolor=SURFACE,
                      edgecolor="none"))
    save(fig, OUT_PDHG / "inward.png", tight=False)


if __name__ == "__main__":
    outward_png()
    inward_png()
    spiral_gif()
