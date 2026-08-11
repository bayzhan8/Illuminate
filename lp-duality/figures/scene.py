"""The workshop's picture: the region of plans that are actually possible.

Chapters 1, 6 and 7 all draw the same shape, so it is built once here.  The
region is drawn from the program itself rather than from typed-in corner
points, which means that when chapter 7 slides a capacity the outline follows
without anyone having to remember to update it.
"""

from __future__ import annotations

import math
from fractions import Fraction

from illuminate.draw import (TEXT, TEXT_DIM, TEXT_FAINT, SURFACE, PLAN, PLAN_FILL, PRICE,
                            HAIRLINE, tag)
from lpduality.lp import LP, vertices

WINDOW = (0, 12.4, 0, 11.6)   # tables, chairs

LINE_STYLE = {
    "planks": dict(color=TEXT, linewidth=1.6),
    "hours": dict(color=TEXT, linewidth=1.6),
    "saw time": dict(color=TEXT, linewidth=1.6),
}


def ordered_corners(lp: LP) -> list[tuple[float, float]]:
    """The corners of the region, walked round the outside rather than listed."""
    pts = [(float(x), float(y)) for x, y in vertices(lp)]
    if not pts:
        return []
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return sorted(pts, key=lambda p: math.atan2(p[1] - cy, p[0] - cx))


def draw_region(ax, lp: LP, fill=True, edge=PLAN, alpha=0.13):
    corners = ordered_corners(lp)
    if fill and corners:
        ax.fill([p[0] for p in corners], [p[1] for p in corners],
                color=edge, alpha=alpha, zorder=1, linewidth=0)
        ax.plot([p[0] for p in corners] + [corners[0][0]],
                [p[1] for p in corners] + [corners[0][1]],
                color=edge, linewidth=1.8, zorder=3)
    return corners


def draw_constraint(ax, lp: LP, i: int, label=True, color=TEXT, lw=1.4,
                    dashes=None, label_x=None):
    """One rule, drawn as the boundary line it is."""
    a, bcoef = float(lp.A[i][0]), float(lp.A[i][1])
    rhs = float(lp.b[i])
    x0, x1, y0, y1 = WINDOW
    if bcoef != 0:
        xs = [x0, x1]
        ys = [(rhs - a * x) / bcoef for x in xs]
    else:
        xs = [rhs / a, rhs / a]
        ys = [y0, y1]
    kw = dict(color=color, linewidth=lw, zorder=2)
    if dashes:
        kw["dashes"] = dashes
    line, = ax.plot(xs, ys, **kw)
    if label:
        # the label sits *on* its own line, with the paper punched out behind
        # it, so it can never be mistaken for a label on a neighbouring line
        lx = label_x if label_x is not None else x1 - 0.35
        ly = (rhs - a * lx) / bcoef if bcoef != 0 else y1 - 0.6
        if y0 <= ly <= y1:
            ax.text(lx, ly, lp.row_names[i], color=color, ha="center",
                    va="center", fontsize=9.5, zorder=6,
                    bbox=dict(boxstyle="square,pad=0.25", facecolor=SURFACE,
                              edgecolor="none"))
    return line


def callout(ax, text, point, at, color=TEXT, ha="center"):
    """A boxed note parked in empty space, with a hairline back to what it means."""
    return ax.annotate(
        text, xy=(float(point[0]), float(point[1])), xytext=at,
        color=color, ha=ha, va="center", fontsize=10, zorder=9,
        bbox=dict(boxstyle="square,pad=0.5", facecolor=SURFACE, edgecolor=color,
                  linewidth=1.1),
        arrowprops=dict(arrowstyle="-", color=color, linewidth=0.9,
                        shrinkA=6, shrinkB=8))


def clipped_corners(lp: LP, x_max: float, y_max: float) -> list[tuple[float, float]]:
    """Corners of a region that may run off to infinity, boxed in for drawing.

    The dual's region is unbounded -- prices can always be raised -- so there is
    no polygon to fill until a window is chosen.  Adding the window as two more
    rows and asking for corners again is the honest way to get one: the shape
    drawn is exactly the feasible set intersected with what the reader can see.
    """
    boxed = LP.build(
        c=lp.c,
        A=list(lp.A) + [[1, 0], [0, 1]],
        b=list(lp.b) + [Fraction(x_max), Fraction(y_max)],
        op=list(lp.op) + ["<=", "<="],
        sense=lp.sense,
        var_names=lp.var_names,
        row_names=tuple(lp.row_names) + ("window x", "window y"),
    )
    return ordered_corners(boxed)


def draw_axes(ax, xlabel="tables built", ylabel="chairs built"):
    x0, x1, y0, y1 = WINDOW
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_xlabel(xlabel, fontsize=10, color=TEXT_DIM, labelpad=7)
    ax.set_ylabel(ylabel, fontsize=10, color=TEXT_DIM, labelpad=7)
    ax.set_xticks(range(0, 13, 2))
    ax.set_yticks(range(0, 12, 2))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)), zorder=0)
    ax.set_axisbelow(True)
    return ax


def profit_line(ax, level: float, c=(30, 20), **kw):
    """The set of plans worth exactly *level*: a straight line of equal profit."""
    x0, x1, _, _ = WINDOW
    xs = [x0, x1]
    ys = [(level - c[0] * x) / c[1] for x in xs]
    style = dict(color=PRICE, linewidth=1.7, zorder=4)
    style.update(kw)
    return ax.plot(xs, ys, **style)[0]


def mark_plan(ax, point, label=None, color=PLAN, size=9.5):
    x, y = float(point[0]), float(point[1])
    dot, = ax.plot([x], [y], "o", markersize=size, color=color,
                   markeredgecolor=SURFACE, markeredgewidth=2.0, zorder=7)
    if label:
        tag(ax, x + 0.28, y + 0.32, label, color=color, size=10, weight="bold")
    return dot
