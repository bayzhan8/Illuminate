"""The difference that actually matters in practice: knowing when you are done.

A walk along the edge gives you no warning. Until the last hop, every corner
looks like the ones before it, and the number of hops left is not something
you can ask about. A point on the central path arrives with a receipt: the
gap to the best possible answer is at most mu times the number of walls, so
dividing mu by ten divides your remaining ignorance by ten.

Both quantities here are computed, not asserted. The bound comes from the
barrier; the actual gap comes from comparing with the exact rational optimum
that the simplex code returns.
"""

import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             chapter_dir, figure, heading, save, style, tag)
from twopaths.barrier import Region, centre_for, duality_gap
from twopaths.simplex import dantzig, solve

OUT = chapter_dir("09-a-gap-you-can-forecast")

A = [[4, 2], [2, 3], [3, 1]]
B = [44, 30, 32]
PROFIT = [30, 20]
REGION = Region.build(A, B, PROFIT)
START = np.array([1.0, 1.0])
MUS = np.array([1e3, 1e2, 1e1, 1e0, 1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6])


def ladder():
    """For each mu: the guaranteed bound, and the gap that actually remains."""
    best = float(solve(PROFIT, A, B, rule=dantzig).value)
    rows = []
    for mu in MUS:
        point = centre_for(REGION, float(mu), START)
        worth = float(PROFIT[0] * point[0] + PROFIT[1] * point[1])
        rows.append((float(mu), duality_gap(REGION, point, float(mu)),
                     max(best - worth, 0.0)))
    return best, rows


def gap_png():
    best, rows = ladder()
    mus = np.array([r[0] for r in rows])
    bound = np.array([r[1] for r in rows])
    actual = np.array([max(r[2], 1e-12) for r in rows])

    fig, ax = figure(7.6, 5.0)
    fig.subplots_adjust(top=0.85, bottom=0.15, left=0.14, right=0.96)
    heading(ax, "the promise, and what it was actually worth")
    style(ax, "mu (falling to the right)", "dollars from the best plan")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.invert_xaxis()

    ax.plot(mus, bound, color=PRICE, linewidth=2.2, marker="o", markersize=6,
            markeredgecolor=SURFACE, markeredgewidth=1.6, zorder=6)
    ax.plot(mus, actual, color=PLAN, linewidth=2.2, marker="o", markersize=6,
            markeredgecolor=SURFACE, markeredgewidth=1.6, zorder=6)
    ax.fill_between(mus, actual, bound, color=PRICE, alpha=0.10, zorder=4,
                    linewidth=0)

    tag(ax, 3e0, 2.2e3, "what the method promises: 5 mu", color=PRICE, size=10.5)
    tag(ax, 6e-3, 4.5e-5, "what it had already achieved", color=PLAN, size=10.5)
    tag(ax, 4e-3, 1.1e2, f"both fall tenfold for every tenfold in mu:\n"
        f"the gap to ${best:,.0f} is forecastable", color=TEXT_DIM, size=9.5)
    save(fig, OUT / "the-gap.png", tight=False)
    return best, rows


if __name__ == "__main__":
    gap_png()
