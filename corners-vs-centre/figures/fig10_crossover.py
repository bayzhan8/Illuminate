"""Why the two methods end up inside the same program.

The path never lands. Both panels here are the same corner, drawn at scales
that differ by a hundred, with the repulsion turned down by a hundred between
them -- and they look the same. That is not an accident of this example: on
the central path the remaining distance falls by the factor mu falls by, so
zooming in and tightening the tolerance move together and the picture never
changes. There is no setting at which the point becomes a corner.

For plenty of purposes it does not need to be. For the ones that do -- reading
off which rules are binding, warm starting the next solve, handing a bound to
a branch-and-bound tree -- the last move of a modern barrier solve is to pass
the point to a simplex-style routine and let it walk the short way to an
actual vertex.
"""

import matplotlib.pyplot as plt
import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, save)
from twopaths.barrier import Region, central_path

OUT = chapter_dir("14-neither-one-won")

A = [[4, 2], [2, 3], [3, 1]]
B = [44, 30, 32]
PROFIT = [30, 20]
REGION = Region.build(A, B, PROFIT)
START = np.array([1.0, 1.0])
CORNER = np.array([9.0, 4.0])
# mu = 1 is not yet in the regime where distance falls with mu, so the two
# panels start once it is: then a hundredfold in mu is a hundredfold in
# distance, and the drawings coincide.
PANELS = [(0.01, 0.0062), (1e-4, 6.2e-5)]  # (stopping mu, half-width shown)


def landing(mu):
    """Where the path is when the repulsion reaches `mu`, and how far short."""
    curve = central_path(REGION, START, mu_from=8000.0, mu_to=mu, points=140)
    return curve, float(np.hypot(*(curve[-1] - CORNER)))


def _pair(width, height):
    dpi = plt.rcParams["figure.dpi"]
    width = round(width * dpi / 2) * 2 / dpi
    height = round(height * dpi / 2) * 2 / dpi
    return plt.subplots(1, 2, figsize=(width, height))


def crossover_png():
    fig, axes = _pair(8.8, 4.3)
    fig.subplots_adjust(top=0.76, bottom=0.26, left=0.105, right=0.975,
                        wspace=0.30)
    fig.text(0.105, 0.915,
             "THE  SAME  CORNER  AT  TWO  SCALES,  AND  THE  SAME  PICTURE",
             ha="left", va="bottom", fontsize=10.5, color=TEXT,
             family="monospace")

    results = []
    for ax, (mu, half) in zip(axes, PANELS):
        curve, away = landing(mu)
        results.append((mu, away))
        ax.set_xlim(CORNER[0] - half, CORNER[0] + half * 0.55)
        ax.set_ylim(CORNER[1] - half, CORNER[1] + half * 0.55)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.grid(True, color=HAIRLINE, linewidth=0.6, linestyle=(0, (1, 4)))
        ax.set_axisbelow(True)
        # No tick numbers. The argument is that the two panels are the same
        # picture, and absolute coordinates at the second scale are noise
        # (matplotlib renders them as an offset like 1e-5+9, which reads as a
        # difference between the panels when there is none).
        ax.tick_params(labelbottom=False, labelleft=False, length=0)

        # The two walls that meet at the corner, drawn far past the window so
        # they fill it at any zoom: planks, then labour.
        span = np.array([-2.0, 2.0]) * half
        for row, limit in ((A[0], B[0]), (A[1], B[1])):
            xs = CORNER[0] + span
            ys = (limit - row[0] * xs) / row[1]
            ax.plot(xs, ys, color=TEXT, linewidth=1.4, zorder=4)
        corner_fill = np.linspace(CORNER[0] - 2 * half, CORNER[0] + 2 * half, 200)
        lower = np.minimum((B[0] - A[0][0] * corner_fill) / A[0][1],
                           (B[1] - A[1][0] * corner_fill) / A[1][1])
        ax.fill_between(corner_fill, CORNER[1] - 2 * half, lower,
                        color=TEXT_FAINT, alpha=0.11, zorder=1, linewidth=0)

        ax.plot(curve[:, 0], curve[:, 1], color=PRICE, linewidth=2.2, zorder=6)
        ax.plot([curve[-1, 0]], [curve[-1, 1]], "o", color=PRICE, markersize=7,
                zorder=8, markeredgecolor=SURFACE, markeredgewidth=1.7)
        ax.plot([CORNER[0]], [CORNER[1]], "o", color=OK, markersize=8, zorder=9,
                markeredgecolor=SURFACE, markeredgewidth=1.8)
        ax.annotate("", xy=tuple(CORNER), xytext=tuple(curve[-1]),
                    arrowprops=dict(arrowstyle="-|>", color=PLAN, linewidth=1.6,
                                    shrinkA=6, shrinkB=8, mutation_scale=11),
                    zorder=7)
        ax.set_xlabel(f"stopped at mu = {mu:g}\n"
                      f"{away:.2e} short of the corner\n"
                      f"window {2 * half:.1e} wide",
                      fontsize=9.5, color=TEXT_DIM, labelpad=10, linespacing=1.6)

    ratio = results[0][1] / results[1][1]
    fig.text(0.105, 0.855,
             f"a hundredfold less repulsion bought {ratio:.0f} times closer, "
             f"and changed nothing else",
             ha="left", va="bottom", fontsize=10, color=TEXT_DIM)
    save(fig, OUT / "crossover.png", tight=False)
    return results


if __name__ == "__main__":
    crossover_png()
