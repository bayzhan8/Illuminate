"""The surface the barrier method is actually minimising, at three settings.

Contours make the mechanism obvious in a way the path alone does not. At
large mu the surface is a broad bowl whose bottom sits in the middle of the
region and has almost nothing to do with profit. As mu falls the bowl tilts
and its bottom slides towards the corner, and at every stage there is a single
smooth minimum that Newton's method can find. Nothing here is combinatorial.
"""

import matplotlib.pyplot as plt
import numpy as np

from illuminate.draw import (HAIRLINE, OK, PRICE, SURFACE, TEXT, TEXT_DIM,
                             chapter_dir, save)
from twopaths.barrier import Region, barrier_value, centre_for

OUT = chapter_dir("12-what-the-barrier-does")

A = [[4, 2], [2, 3], [3, 1]]
B = [44, 30, 32]
PROFIT = [30, 20]
REGION = Region.build(A, B, PROFIT)
START = np.array([1.0, 1.0])
CORNERS = [(0, 0), (32 / 3, 0), (10, 2), (9, 4), (0, 10)]
SHOWN = (100.0, 10.0, 1.0)
GRID = 320


def surface(mu):
    xs = np.linspace(0.02, 11.4, GRID)
    ys = np.linspace(0.02, 10.4, GRID)
    X, Y = np.meshgrid(xs, ys)
    Z = np.full(X.shape, np.nan)
    for i in range(GRID):
        for j in range(GRID):
            point = np.array([X[i, j], Y[i, j]])
            if REGION.interior(point):
                Z[i, j] = barrier_value(REGION, point, mu)
    return X, Y, Z


def _row_of_three(width, height):
    """Three panels sharing one figure, at an even pixel size like figure()."""
    dpi = plt.rcParams["figure.dpi"]
    width = round(width * dpi / 2) * 2 / dpi
    height = round(height * dpi / 2) * 2 / dpi
    return plt.subplots(1, 3, figsize=(width, height))


def landscape_png():
    fig, axes = _row_of_three(9.6, 3.7)
    fig.subplots_adjust(top=0.80, bottom=0.16, left=0.065, right=0.985,
                        wspace=0.22)
    fig.text(0.065, 0.925, "THE  SURFACE  THE  METHOD  MINIMISES,  AS  THE"
             "  REPULSION  IS  TURNED  DOWN", ha="left", va="bottom",
             fontsize=10.5, color=TEXT, family="monospace")

    middle = np.mean(CORNERS, axis=0)
    shape = sorted(CORNERS, key=lambda p: np.arctan2(p[1] - middle[1],
                                                     p[0] - middle[0]))
    for ax, mu in zip(axes, SHOWN):
        X, Y, Z = surface(mu)
        finite = Z[np.isfinite(Z)]
        floor = finite.min()
        levels = floor + np.geomspace(0.05, max(finite.max() - floor, 1.0), 16)
        ax.contour(X, Y, Z, levels=levels, colors=PRICE, linewidths=0.7,
                   alpha=0.55, zorder=4)
        ax.plot([p[0] for p in shape] + [shape[0][0]],
                [p[1] for p in shape] + [shape[0][1]],
                color=TEXT, linewidth=1.3, zorder=5)
        best = centre_for(REGION, mu, START)
        ax.plot([best[0]], [best[1]], "o", color=PRICE, markersize=7, zorder=8,
                markeredgecolor=SURFACE, markeredgewidth=1.7)
        ax.plot([9], [4], "o", color=OK, markersize=6, zorder=7,
                markeredgecolor=SURFACE, markeredgewidth=1.5)
        ax.set_xlim(0, 12.0)
        ax.set_ylim(0, 11.0)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.grid(True, color=HAIRLINE, linewidth=0.6, linestyle=(0, (1, 4)))
        ax.set_axisbelow(True)
        ax.tick_params(labelsize=8.5, colors=TEXT_DIM)
        worth = PROFIT[0] * best[0] + PROFIT[1] * best[1]
        ax.set_xlabel(f"mu = {mu:g}      worth ${worth:,.0f}", fontsize=9.5,
                      color=TEXT_DIM, labelpad=6)
    axes[0].set_ylabel("chairs", fontsize=9.5, color=TEXT_DIM, labelpad=4)
    save(fig, OUT / "the-landscape.png", tight=False)


if __name__ == "__main__":
    landscape_png()
