"""Half the distance to a violated wall keeps a whole disc outside."""

import math
from fractions import Fraction

from matplotlib.patches import Circle, Polygon

from illuminate.draw import (HAIRLINE, PLAN, TEXT, TEXT_DIM, WARN, animate,
                             chapter_dir, figure, margin_note)
from linprog import mill as f
from scene import Stages, claim, draw_axes, mark

OUT = chapter_dir("01-inside-the-walls")
A = f.MILL.A[0]
B = f.MILL.b[0]
X = (Fraction(6), Fraction(14))
EPSILON = f.MILL.used(0, X) - B
AA = sum((u * u for u in A), Fraction(0))
Y_STAR = tuple(X[i] - EPSILON * A[i] / AA for i in range(2))
WINDOW_EXACT = (Fraction(5, 2), Fraction(19, 2),
                Fraction(21, 2), Fraction(33, 2))
STAGES = Stages((0, 12), (0, 12), (48, 12))
SUBS = ["radius 2 = epsilon in hours: the disc crosses the lathe wall",
        "radius 2 ÷ √5: it touches at the nearest point",
        "radius 1 ÷ √5: a probe circles the edge"]
TITLE = "a sufficiently small disc stays over the wall"
FINAL = "every point of the disc is over the lathe hours, so the outside is open"


def clip_exact(poly, a, b):
    out = []
    for i, p in enumerate(poly):
        q = poly[(i + 1) % len(poly)]
        gp = sum((u * v for u, v in zip(a, p)), Fraction(0)) - b
        gq = sum((u * v for u, v in zip(a, q)), Fraction(0)) - b
        if gp <= 0:
            out.append(p)
        if (gp <= 0) != (gq <= 0):
            s = gp / (gp - gq)
            out.append(tuple(p[j] + s * (q[j] - p[j]) for j in range(2)))
    return out


def local_region():
    x0, x1, y0, y1 = WINDOW_EXACT
    poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for a, b in zip(f.MILL.A, f.MILL.b):
        poly = clip_exact(poly, a, b)
    return poly


REGION = local_region()


def ball_gif():
    fig, ax = figure(7.2, 6.4)
    fig.subplots_adjust(left=0.13, right=0.97, top=0.84, bottom=0.2)
    note = margin_note(fig, y=0.025, size=9.4)
    frames = STAGES.total
    x = tuple(float(v) for v in X)
    y_star = tuple(float(v) for v in Y_STAR)
    a = tuple(float(v) for v in A)
    wall_norm = math.sqrt(float(AA))
    radii = (float(EPSILON), float(EPSILON) / wall_norm,
             float(EPSILON) / (2 * wall_norm))
    theta_min = math.atan2(-a[1], -a[0])

    def update(i):
        i = min(i, frames - 1)
        k, s = STAGES(i)
        if i == frames - 1:
            s = 1.0
        radius = radii[k]
        ax.clear()
        draw_axes(ax)
        ax.set_xlim(float(WINDOW_EXACT[0]), float(WINDOW_EXACT[1]))
        ax.set_ylim(float(WINDOW_EXACT[2]), float(WINDOW_EXACT[3]))
        ax.set_xticks(range(3, 10))
        ax.set_yticks(range(11, 17))

        region_points = [(float(p[0]), float(p[1])) for p in REGION]
        region = Polygon(region_points, closed=True, facecolor=PLAN, alpha=0.14,
                         edgecolor=PLAN, linewidth=1.4, zorder=1)
        ax.add_patch(region)
        xlim = ax.get_xlim()
        for index, (row, rhs) in enumerate(zip(f.MILL.A, f.MILL.b)):
            rowf = tuple(float(v) for v in row)
            rhsf = float(rhs)
            ys = [(rhsf - rowf[0] * t) / rowf[1] for t in xlim]
            ax.plot(xlim, ys, color=TEXT, lw=1.45 if index == 0 else 1.0,
                    zorder=2)
        ax.text(8.15, (float(B) - 8.15 * a[0]) / a[1] + 0.34,
                "lathe wall", color=TEXT, fontsize=9.2, ha="center", zorder=6,
                bbox=dict(boxstyle="square,pad=0.18", facecolor="#fffff8",
                          edgecolor="none"))

        if k == 0:
            inside = Circle(x, radius, facecolor=WARN, edgecolor="none",
                            alpha=0.42, zorder=3)
            inside.set_clip_path(region)
            ax.add_patch(inside)
        edge_color = WARN if k == 0 else PLAN
        ax.add_patch(Circle(x, radius, fill=False, edgecolor=edge_color,
                            linewidth=1.8, zorder=4))
        mark(ax, x, "x = (6, 14)", color=WARN, size=9.5, dx=0.5, dy=0.38)

        if k == 1:
            mark(ax, y_star, "(5.6, 13.2)", color=PLAN, size=8.5,
                 dx=-0.12, dy=-0.43, ha="right")
            ax.plot([x[0], y_star[0]], [x[1], y_star[1]], color=TEXT_DIM,
                    lw=0.9, dashes=(3, 2), zorder=5)
        if k == 2:
            theta = theta_min + 2 * math.pi * s
            probe = (x[0] + radius * math.cos(theta),
                     x[1] + radius * math.sin(theta))
            ax.plot([x[0], probe[0]], [x[1], probe[1]], color=TEXT_DIM,
                    lw=0.8, dashes=(2, 2), zorder=5)
            mark(ax, probe, "probe", size=7.5, dx=-0.7, dy=-0.35, ha="right")
            used = a[0] * probe[0] + a[1] * probe[1]
            min_used = sum((u * v for u, v in zip(A, X)), Fraction(0)) - EPSILON / 2
            note.set_text(f"lathe hours at probe = {used:.1f}\n"
                          f"minimum on the circle = {min_used} hours")
        elif k == 0:
            farthest_inside = float(sum((u * v for u, v in zip(A, X)), Fraction(0))) \
                - radius * wall_norm
            note.set_text(f"radius = epsilon = {EPSILON} hours\n"
                          f"inside disc reaches {farthest_inside:.1f} lathe hours")
        else:
            note.set_text(f"radius = 2 ÷ √5 ≈ {radii[1]:.2f} batches\n"
                          f"the disc touches the lathe wall at 32 hours")
        if i == frames - 1:
            claim(ax, TITLE)
            ax.text(0, 1.025, FINAL, transform=ax.transAxes, fontsize=8.2,
                    color=TEXT_DIM, ha="left", va="bottom")
        else:
            claim(ax, TITLE, SUBS[k])
        return []

    animate(fig, update, frames, OUT / "ball.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    ball_gif()
