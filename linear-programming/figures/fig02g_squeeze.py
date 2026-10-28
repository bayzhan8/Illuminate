"""Repeated quartering traps a subsequence in nested squares."""

import math
from fractions import Fraction

from matplotlib.patches import Rectangle
from matplotlib.ticker import MaxNLocator

from illuminate.draw import (HAIRLINE, PLAN, TEXT, TEXT_DIM, animate, chapter_dir,
                             figure, margin_note)
from linprog import mill as f
from scene import Stages, claim

OUT = chapter_dir("02-best-is-a-corner")
N = 5_000
CUTS = 5
SIDE = f.MILL.b[1]
CENTER = SIDE / 2
RADIUS = Fraction(19, 2)
FREQUENCY = Fraction(17, 10)
START = (Fraction(0), SIDE, Fraction(0), SIDE)
POINTS = tuple(
    (k, float(CENTER) + float(RADIUS) * math.cos(k),
     float(CENTER) + float(RADIUS) * math.sin(float(FREQUENCY) * k))
    for k in range(1, N + 1)
)


def in_square(point, square):
    _, t, v = point
    t0, t1, v0, v1 = square
    return float(t0) <= t <= float(t1) and float(v0) <= v <= float(v1)


def quarters(square):
    t0, t1, v0, v1 = square
    mt, mv = (t0 + t1) / 2, (v0 + v1) / 2
    return (
        (t0, mt, v0, mv),
        (mt, t1, v0, mv),
        (t0, mt, mv, v1),
        (mt, t1, mv, v1),
    )


def build_cuts():
    cuts = []
    parent = START
    active = POINTS
    previous_pick = 0
    for _ in range(CUTS):
        children = quarters(parent)
        mt = (parent[0] + parent[1]) / 2
        mv = (parent[2] + parent[3]) / 2
        buckets = [[] for _ in children]
        for point in active:
            _, t, v = point
            quadrant = (1 if t > float(mt) else 0) + (2 if v > float(mv) else 0)
            buckets[quadrant].append(point)
        kept_index = max(range(4), key=lambda q: len(buckets[q]))
        kept_points = tuple(buckets[kept_index])
        picked = next((point for point in kept_points
                       if point[0] > previous_pick), None)
        assert picked is not None
        kept_square = children[kept_index]
        assert in_square(picked, kept_square)
        cuts.append((parent, children, kept_index, kept_points, picked))
        parent = kept_square
        active = kept_points
        previous_pick = picked[0]
    return tuple(cuts)


CUT_DATA = build_cuts()
SQUARES = tuple(children[kept_index]
                for _, children, kept_index, _, _ in CUT_DATA)
KEPT_POINTS = tuple(kept_points for _, _, _, kept_points, _ in CUT_DATA)
COUNTS = tuple(len(points) for points in KEPT_POINTS)
PICK_POINTS = tuple(picked for _, _, _, _, picked in CUT_DATA)
PICK_INDICES = tuple(point[0] for point in PICK_POINTS)

assert all(first < second for first, second in zip(PICK_INDICES, PICK_INDICES[1:]))
assert all(in_square(point, square)
           for point, square in zip(PICK_POINTS, SQUARES))
assert COUNTS[-1] >= 3

LABEL_OFFSETS = ((0.16, 0.18), (0.16, 0.16), (-0.18, -0.24),
                 (0.18, 0.16), (-0.22, -0.18))


def view_bounds(square, picks):
    t0, t1, v0, v1 = (float(value) for value in square)
    ts = [t0, t1]
    vs = [v0, v1]
    for point, (dt, dv) in zip(picks, LABEL_OFFSETS):
        _, t, v = point
        ts.extend((t, t + dt))
        vs.extend((v, v + dv))
    t_mid = (min(ts) + max(ts)) / 2
    v_mid = (min(vs) + max(vs)) / 2
    extent = max(max(ts) - min(ts), max(vs) - min(vs))
    extent += 0.8 * float(t1 - t0)
    return (t_mid - extent / 2, t_mid + extent / 2,
            v_mid - extent / 2, v_mid + extent / 2)


VIEWS = [(0.0, float(SIDE), 0.0, float(SIDE))]
for cut_index, square in enumerate(SQUARES):
    VIEWS.append(view_bounds(square, PICK_POINTS[:cut_index + 1]))
VIEWS = tuple(VIEWS)

STAGES = Stages((10, 10), (10, 10), (10, 10), (10, 10), (10, 14))
TITLE = "quartering traps later terms in a smaller square"
SUBS = tuple(f"cut {k}: keep the quarter containing the most points"
             for k in range(1, CUTS + 1))
FINAL = "a bounded sequence has a convergent subsequence"


def squeeze_gif():
    fig, ax = figure(8.0, 6.8)
    fig.subplots_adjust(left=0.11, right=0.97, top=0.84, bottom=0.2)
    note = margin_note(fig, y=0.025, size=9.1)
    frames = STAGES.total
    point_t = tuple(point[1] for point in POINTS)
    point_v = tuple(point[2] for point in POINTS)

    def update(i):
        i = min(i, frames - 1)
        k, s = STAGES(i)
        if i == frames - 1:
            s = 1.0
        parent, children, kept_index, _, _ = CUT_DATA[k]
        view_from, view_to = VIEWS[k], VIEWS[k + 1]
        view = tuple(start + s * (end - start)
                     for start, end in zip(view_from, view_to))

        ax.clear()
        ax.set_xlim(view[0], view[1])
        ax.set_ylim(view[2], view[3])
        ax.set_aspect("equal", adjustable="box")
        ax.xaxis.set_major_locator(MaxNLocator(5))
        ax.yaxis.set_major_locator(MaxNLocator(5))
        ax.set_xlabel("first coordinate", fontsize=9.5, color=TEXT_DIM, labelpad=6)
        ax.set_ylabel("second coordinate", fontsize=9.5, color=TEXT_DIM, labelpad=6)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.grid(True, color=HAIRLINE, linewidth=0.65, linestyle=(0, (1, 3)),
                zorder=0)
        ax.set_axisbelow(True)

        t0, t1, v0, v1 = (float(value) for value in parent)
        ax.add_patch(Rectangle((t0, v0), t1 - t0, v1 - v0,
                               facecolor="none", edgecolor=TEXT_DIM,
                               linewidth=0.9, alpha=0.55, zorder=1))
        for quarter_index, square in enumerate(children):
            q0, q1, w0, w1 = (float(value) for value in square)
            kept = quarter_index == kept_index
            color = PLAN if kept else TEXT_DIM
            ax.add_patch(Rectangle(
                (q0, w0), q1 - q0, w1 - w0,
                facecolor=color, edgecolor=color,
                linewidth=1.45 if kept else 0.8,
                alpha=(0.2 if kept else 0.11) * s, zorder=2,
            ))

        ax.scatter(point_t, point_v, s=7, color=TEXT_DIM, alpha=0.42,
                   linewidths=0, zorder=3)

        previous = PICK_POINTS[:k]
        if len(previous) > 1:
            ax.plot([point[1] for point in previous],
                    [point[2] for point in previous],
                    color=PLAN, linewidth=1.0, alpha=0.8, zorder=5)
        if previous and s > 0:
            ax.plot([previous[-1][1], PICK_POINTS[k][1]],
                    [previous[-1][2], PICK_POINTS[k][2]],
                    color=PLAN, linewidth=1.0, alpha=0.8 * s, zorder=5)
        for pick_index, point in enumerate(PICK_POINTS[:k + 1]):
            alpha = s if pick_index == k else 1.0
            _, t, v = point
            ax.scatter([t], [v], s=33, color=PLAN, alpha=alpha,
                       edgecolors="#fffff8", linewidths=1.2, zorder=7)
            dt, dv = LABEL_OFFSETS[pick_index]
            ax.text(t + dt, v + dv, rf"$x_{{{point[0]}}}$", color=PLAN,
                    fontsize=8.2, ha="left" if dt > 0 else "right",
                    va="center", alpha=alpha,
                    bbox=dict(boxstyle="square,pad=0.12",
                              facecolor="#fffff8", edgecolor="none"),
                    zorder=8)

        if i == frames - 1:
            claim(ax, TITLE)
            ax.text(0, 1.025, FINAL, transform=ax.transAxes, fontsize=8.5,
                    color=TEXT_DIM, ha="left", va="bottom")
        else:
            claim(ax, TITLE, SUBS[k])
        side = SIDE / (2 ** (k + 1))
        indices = " → ".join(str(index) for index in PICK_INDICES[:k + 1])
        note.set_text(
            f"cut {k + 1}: side {SIDE} ÷ {2 ** (k + 1)} = {float(side):g}, "
            f"points inside = {COUNTS[k]:,}\n"
            f"picked indices: {indices}"
        )
        return []

    animate(fig, update, frames, OUT / "squeeze.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    squeeze_gif()
