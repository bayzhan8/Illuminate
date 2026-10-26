"""The farm's picture, drawn from the program itself so it cannot drift from it."""

from __future__ import annotations

import math

from illuminate.draw import HAIRLINE, PLAN, SURFACE, TEXT, TEXT_DIM, tag
from linprog import farm as f
from linprog.lp import LP, vertices

WINDOW = (0, 23, 0, 18.5)   # acres of wheat, acres of corn


def ordered(lp: LP = f.FARM):
    pts = [(float(x), float(y)) for x, y in vertices(lp)]
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return sorted(pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))


def draw_axes(ax):
    x0, x1, y0, y1 = WINDOW
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_xlabel("acres of wheat", fontsize=10, color=TEXT_DIM, labelpad=7)
    ax.set_ylabel("acres of corn", fontsize=10, color=TEXT_DIM, labelpad=7)
    ax.set_xticks(range(0, 23, 4))
    ax.set_yticks(range(0, 19, 4))
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)), zorder=0)
    ax.set_axisbelow(True)
    ax.set_aspect("equal", adjustable="box")   # so right angles look like right angles


def draw_region(ax, lp: LP = f.FARM, alpha=0.13):
    pts = ordered(lp)
    ax.fill([p[0] for p in pts], [p[1] for p in pts], color=PLAN, alpha=alpha,
            zorder=1, linewidth=0)
    ax.plot([p[0] for p in pts] + [pts[0][0]], [p[1] for p in pts] + [pts[0][1]],
            color=PLAN, linewidth=1.8, zorder=3)


def draw_wall(ax, i, label=None, at=None, color=TEXT, lw=1.4):
    """Row i as the line where that resource runs out exactly."""
    a, b, r = (float(v) for v in (*f.FARM.A[i], f.FARM.b[i]))
    x0, x1 = WINDOW[:2]
    ax.plot([x0, x1], [(r - a * x0) / b, (r - a * x1) / b], color=color,
            linewidth=lw, zorder=2)
    if label:
        lx = at
        ax.text(lx, (r - a * lx) / b, label, color=color, ha="center", va="center",
                fontsize=9.5, zorder=6,
                bbox=dict(boxstyle="square,pad=0.25", facecolor=SURFACE, edgecolor="none"))


def iso_profit(ax, level, c=f.PROFIT, **kw):
    """Every plan worth exactly `level`: a straight line."""
    x0, x1 = WINDOW[:2]
    style = dict(color=TEXT, linewidth=1.6, dashes=(6, 3), zorder=4)
    style.update(kw)
    return ax.plot([x0, x1], [(level - c[0] * x0) / c[1], (level - c[0] * x1) / c[1]],
                   **style)[0]


def mark(ax, p, label=None, color=PLAN, size=9.5, dx=0.4, dy=0.5, ha="left"):
    x, y = float(p[0]), float(p[1])
    ax.plot([x], [y], "o", markersize=size, color=color, markeredgecolor=SURFACE,
            markeredgewidth=2.0, zorder=7)
    if label:
        tag(ax, x + dx, y + dy, label, color=color, size=10, ha=ha)


def heading(ax, text: str):
    """The house small-caps title, without illuminate.draw's hair-space tracking.

    The bundled mono face has no hair-space glyph on this renderer, so the
    tracked version prints a box between every letter.
    """
    from illuminate.draw import TEXT_FAINT
    ax.set_title(text.upper(), loc="left", fontsize=9.5, color=TEXT_FAINT, pad=12,
                 fontweight="semibold")


def norm(v):
    return math.hypot(float(v[0]), float(v[1]))


def foot(x, a):
    """Where x lands when dropped at right angles onto the line through 0 along a."""
    k = (float(a[0]) * float(x[0]) + float(a[1]) * float(x[1])) / norm(a) ** 2
    return (k * float(a[0]), k * float(a[1]))


def direction_line(ax, a, color, label=None, reach=24, lw=1.0):
    u = (float(a[0]) / norm(a), float(a[1]) / norm(a))
    ax.plot([0, reach * u[0]], [0, reach * u[1]], color=color, lw=lw,
            dashes=(2, 3), zorder=2)
    if label:
        ax.text(reach * u[0] * 0.97, reach * u[1] * 0.97, label, color=color,
                fontsize=9.5, ha="right", va="bottom", zorder=6)


def arrow(ax, start, vec, color, label=None, lw=2.2, dx=0.3, dy=0.3, ha="left"):
    ax.annotate("", xy=(start[0] + vec[0], start[1] + vec[1]), xytext=start,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw,
                                shrinkA=0, shrinkB=0, mutation_scale=14), zorder=8)
    if label:
        ax.text(start[0] + vec[0] + dx, start[1] + vec[1] + dy, label, color=color,
                fontsize=10, ha=ha, va="center", zorder=8)


WINDOW_POLY = [(WINDOW[0], WINDOW[2]), (WINDOW[1], WINDOW[2]),
               (WINDOW[1], WINDOW[3]), (WINDOW[0], WINDOW[3])]


def ease(s):
    s = min(max(s, 0.0), 1.0)
    return s * s * (3 - 2 * s)


class Stages:
    """Consecutive stages, each (move, pause): `move` eased frames, then `pause` still ones."""

    def __init__(self, *spec):
        self.spec = spec
        self.total = sum(m + p for m, p in spec)

    def __call__(self, i):
        for k, (m, p) in enumerate(self.spec):
            if i < m + p:
                return k, (ease(i / m) if m else 1.0)
            i -= m + p
        return len(self.spec) - 1, 1.0


def claim(ax, text, sub=""):
    """The figure's claim as a sentence, and the line saying what this stage shows."""
    ax.text(0, 1.085, text, transform=ax.transAxes, fontsize=11, color=TEXT,
            ha="left", va="bottom", fontweight="semibold")
    if sub:
        ax.text(0, 1.025, sub, transform=ax.transAxes, fontsize=10, color=TEXT_DIM,
                ha="left", va="bottom")


def unit(v):
    n = norm(v)
    return (float(v[0]) / n, float(v[1]) / n)


def dot(a, x):
    return float(a[0]) * float(x[0]) + float(a[1]) * float(x[1])


def clip(poly, a, b, keep_le=True):
    """The part of a convex polygon where a·x <= b (or >= b)."""
    out = []
    g = (lambda p: dot(a, p) - b) if keep_le else (lambda p: b - dot(a, p))
    for k in range(len(poly)):
        p, q = poly[k], poly[(k + 1) % len(poly)]
        gp, gq = g(p), g(q)
        if gp <= 1e-12:
            out.append(p)
        if (gp <= 1e-12) != (gq <= 1e-12):
            t = gp / (gp - gq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def fill(ax, poly, color, alpha, z=1):
    from matplotlib.patches import Polygon
    if len(poly) >= 3:
        ax.add_patch(Polygon(poly, closed=True, fc=color, alpha=alpha, lw=0, zorder=z))


def line_where(ax, a, b, **kw):
    """Every point with a·x = b, across the window."""
    x0, x1 = WINDOW[:2]
    style = dict(color=TEXT, linewidth=1.4, zorder=3)
    style.update(kw)
    a0, a1 = float(a[0]), float(a[1])
    return ax.plot([x0, x1], [(b - a0 * x0) / a1, (b - a0 * x1) / a1], **style)[0]


def right_angle(ax, at, u, v, s=0.55, color=TEXT_DIM):
    p1 = (at[0] + s * u[0], at[1] + s * u[1])
    p2 = (p1[0] + s * v[0], p1[1] + s * v[1])
    p3 = (at[0] + s * v[0], at[1] + s * v[1])
    ax.plot([p1[0], p2[0], p3[0]], [p1[1], p2[1], p3[1]], color=color, lw=0.9, zorder=6)


def usd(thousands):
    return f"${float(thousands) * 1000:,.0f}"


def signed(v):
    return f"{round(float(v), 2) + 0.0:+.2f}"
