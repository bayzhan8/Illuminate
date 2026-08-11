"""What a rule does to the set of plans you are allowed to choose from.

Before any method can walk anywhere there has to be somewhere to walk, and the
shape it walks on is not drawn by anyone. It is what is left after each rule
takes its cut. Adding the rules one at a time is the fastest way to see that
the corners are not features of the problem: they are the places where two
rules happen to run out at once.
"""

import numpy as np

from illuminate.draw import (HAIRLINE, PLAN, SURFACE, TEXT, TEXT_DIM, TEXT_FAINT,
                             animate, chapter_dir, figure, heading, margin_note,
                             save, tag)

OUT = chapter_dir("01-a-new-kind-of-problem")

WINDOW = (-1.1, 14.5, -1.0, 13.5)
RULES = [
    ((-1.0, 0.0), 0.0, "you cannot build a negative number of tables"),
    ((0.0, -1.0), 0.0, "nor a negative number of chairs"),
    ((4.0, 2.0), 44.0, "44 planks: a table takes 4, a chair 2"),
    ((2.0, 3.0), 30.0, "30 hours of bench time: 2 and 3"),
    ((3.0, 1.0), 32.0, "32 hours of finishing: 3 and 1"),
]


def region_after(count):
    """The corners of what survives the first `count` rules, in draw order."""
    walls = [(np.array(a, float), c) for a, c, _ in RULES[:count]]
    box = [(np.array([-1.0, 0.0]), 0.4), (np.array([0.0, -1.0]), 0.4),
           (np.array([1.0, 0.0]), WINDOW[1]), (np.array([0.0, 1.0]), WINDOW[3])]
    walls = walls + box
    points = []
    for i in range(len(walls)):
        for j in range(i + 1, len(walls)):
            (a1, c1), (a2, c2) = walls[i], walls[j]
            det = a1[0] * a2[1] - a2[0] * a1[1]
            if abs(det) < 1e-12:
                continue
            p = np.array([(c1 * a2[1] - c2 * a1[1]) / det,
                          (a1[0] * c2 - a2[0] * c1) / det])
            if all(a @ p <= c + 1e-9 for a, c in walls):
                points.append(p)
    if not points:
        return np.empty((0, 2))
    points = np.array(points)
    middle = points.mean(axis=0)
    order = np.argsort(np.arctan2(points[:, 1] - middle[1], points[:, 0] - middle[0]))
    return points[order]


def true_corners():
    """The five corners of the finished region, for counting in the caption."""
    shape = region_after(len(RULES))
    keep = [p for p in shape if p[0] >= -1e-9 and p[1] >= -1e-9]
    unique = []
    for p in keep:
        if not any(np.allclose(p, q, atol=1e-7) for q in unique):
            unique.append(p)
    return unique


def frame(ax, count):
    ax.clear()
    ax.set_xlim(*WINDOW[:2])
    ax.set_ylim(*WINDOW[2:])
    ax.set_xlabel("tables", fontsize=10, color=TEXT_DIM, labelpad=5)
    ax.set_ylabel("chairs", fontsize=10, color=TEXT_DIM, labelpad=5)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)

    shape = region_after(count)
    if len(shape):
        ax.fill(shape[:, 0], shape[:, 1], color=PLAN, alpha=0.11, zorder=1,
                linewidth=0)
    for index, (a, c, _) in enumerate(RULES[:count]):
        a = np.array(a, float)
        fresh = index == count - 1
        if abs(a[1]) > 1e-12:
            xs = np.array(WINDOW[:2], float)
            ys = (c - a[0] * xs) / a[1]
        else:
            ys = np.array(WINDOW[2:], float)
            xs = np.full(2, c / a[0])
        ax.plot(xs, ys, color=TEXT if fresh else TEXT_FAINT,
                linewidth=2.0 if fresh else 1.0, zorder=4 if fresh else 3)
    if len(shape):
        ax.plot(list(shape[:, 0]) + [shape[0, 0]],
                list(shape[:, 1]) + [shape[0, 1]],
                color=PLAN, linewidth=1.8, zorder=5)
    return shape



def region_gif(fps=1.6):
    fig, ax = figure(7.4, 5.0)
    fig.subplots_adjust(top=0.84, bottom=0.22, left=0.10, right=0.97)
    note = margin_note(fig, x=0.035, size=10.5)

    def update(i):
        count = min(i + 1, len(RULES))
        shape = frame(ax, count)
        heading(ax, "adding the rules, one at a time")
        if count == len(RULES):
            for point in true_corners():
                ax.plot([point[0]], [point[1]], "o", color=PLAN, markersize=7,
                        zorder=8, markeredgecolor=SURFACE, markeredgewidth=1.8)
        note.set_text(f"rule {count} of {len(RULES)}   {RULES[count - 1][2]}\n"
                      f"plans still allowed: the shaded region")
        note.set_color(TEXT)
        return []

    animate(fig, update, len(RULES) + 2, OUT / "the-region.gif", fps=fps, hold=3.0)


if __name__ == "__main__":
    region_gif()
