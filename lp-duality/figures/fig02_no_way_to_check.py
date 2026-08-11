"""Chapter 2: trying plans forever, and still not knowing when to stop."""

import random

from lpduality import workshop as w
from illuminate.draw import (TEXT, TEXT_DIM, TEXT_FAINT, PLAN, PRICE, HAIRLINE, chapter_dir,
                            figure, heading, save, style, tag)

OUT = chapter_dir("02-no-way-to-check")


def guessing_png(trials=600, seed=11):
    """The best plan found so far, against how many plans have been tried.

    The curve does what a search curve always does: it shoots up, then flattens,
    and then stays flat for a long time.  The flattening is the point.  It looks
    exactly the same whether the search has found the best plan or has merely
    stopped getting lucky, so it cannot tell the reader which of those happened.
    That is the gap the rest of the guide is about.
    """
    rng = random.Random(seed)
    best, best_curve = 0.0, []
    for _ in range(trials):
        # a random plan, rejected unless the workshop could really build it
        while True:
            t = rng.uniform(0, 11)
            c = rng.uniform(0, 10)
            if w.PRIMAL.is_feasible((round(t, 6), round(c, 6))):
                break
        best = max(best, 30 * t + 20 * c)
        best_curve.append(best)

    fig, ax = figure(8.0, 4.4)
    style(ax, "plans tried", "best profit found so far")
    heading(ax, "searching, without ever being told to stop")

    ax.plot(range(1, trials + 1), best_curve, color=PLAN, linewidth=2.0, zorder=4)
    ax.axhline(float(w.BEST_PROFIT), color=TEXT_FAINT, linewidth=1.0,
               linestyle=(0, (4, 4)), zorder=2)
    ax.set_ylim(0, 400)
    ax.set_xlim(0, trials)

    tag(ax, trials * 0.985, float(w.BEST_PROFIT) + 9,
        "the best there is — but nothing in the search says so",
        color=TEXT_FAINT, ha="right", size=9.5)
    tag(ax, trials * 0.5, best_curve[trials // 2] - 60,
        f"after {trials} plans the best found is "
        f"${best_curve[-1]:,.2f}\nit has not moved in a long time\n"
        "is that because it cannot, or because\nthe next plan was never tried?",
        color=TEXT_DIM, size=10.5, va="top")
    save(fig, OUT / "guessing.png")


if __name__ == "__main__":
    guessing_png()
