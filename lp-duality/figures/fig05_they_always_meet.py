"""Chapter 5: the gap closes here, and it closes everywhere.

Two figures, because there are two things to believe and they need different
kinds of evidence.

``meet.gif`` is this workshop: real plans climbing from below, real prices
falling from above, and the space between them squeezed to nothing.  It shows
what happened.

``always.png`` is a few hundred other workshops, invented at random, each one
solved twice from scratch.  Every one of them lands on the diagonal.  That is
not a proof and the chapter says so -- it is what a proof would have to
explain, and it is the difference between "the two numbers matched" and "the
two numbers match".
"""

import random

from lpduality import workshop as w
from illuminate.draw import (TEXT, TEXT_DIM, TEXT_FAINT, OK, SURFACE, PLAN, PRICE, HAIRLINE,
                            animate, chapter_dir, figure, heading, margin_note,
                            save, tag)
from lpduality.duality import ceiling_from, dual
from lpduality.lp import LP, solve

OUT = chapter_dir("05-the-gap-closes")


def meet_gif(fps=11):
    """The two ladders, one rung at a time, on a single scale of dollars."""
    floors = [(float(w.PRIMAL.objective(plan)), why) for plan, why in w.ASCENT]
    ceilings = [(float(ceiling_from(w.PRIMAL, y)), why) for y, why in w.DESCENT]
    steps = max(len(floors), len(ceilings))
    frames = steps * 6

    fig, ax = figure(8.6, 4.2)
    fig.subplots_adjust(bottom=0.30, top=0.82)
    heading(ax, "closing in on the answer from both sides")

    ax.set_xlim(-40, 1010)
    ax.set_ylim(-1.15, 1.15)
    ax.set_yticks([])
    ax.set_xlabel("dollars", fontsize=10, color=TEXT_DIM, labelpad=7)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.grid(True, axis="x", color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)

    band = ax.axvspan(0, 1000, color=TEXT_FAINT, alpha=0.10, zorder=1)
    floor_dots, = ax.plot([], [], "o", color=PLAN, markersize=8, zorder=6,
                          markeredgecolor=SURFACE, markeredgewidth=1.6)
    ceil_dots, = ax.plot([], [], "o", color=PRICE, markersize=8, zorder=6,
                         markeredgecolor=SURFACE, markeredgewidth=1.6)
    tag(ax, -30, 0.72, "plans you could really carry out", color=PLAN, size=10)
    tag(ax, -30, -0.85, "prices that really cover every product", color=PRICE,
        size=10)
    note = margin_note(fig, x=0.04, size=10.5)

    def update(i):
        i = min(i, frames - 1)
        k = min(steps, i // 6 + 1)
        fl = floors[:k]
        ce = ceilings[:k]
        floor_dots.set_data([v for v, _ in fl], [0.45] * len(fl))
        ceil_dots.set_data([v for v, _ in ce], [-0.45] * len(ce))
        lo = fl[-1][0] if fl else 0.0
        hi = ce[-1][0] if ce else 1000.0
        # axvspan hands back a Rectangle, so the span is moved by its bounds
        # rather than by a list of corners
        band.set_bounds(lo, -1.15, max(hi - lo, 1.5), 2.3)
        if lo == hi:
            note.set_text(f"the answer is exactly ${lo:,.0f}\n"
                          "no room left for it to be anything else")
            note.set_color(TEXT)
            band.set_color(OK)
        else:
            note.set_text(f"the answer is somewhere in ${lo:,.0f} to ${hi:,.0f}\n"
                          f"{fl[-1][1]}   /   {ce[-1][1]}")
            note.set_color(TEXT_DIM)
        return []

    animate(fig, update, frames, OUT / "meet.gif", fps=fps, hold=3.2)


def always_png(count=320, seed=7):
    """Solve a few hundred unrelated workshops twice each, and plot the pairs.

    Each one is invented with positive recipes, positive stocks and positive
    profits, which makes it feasible (build nothing) and bounded (every product
    consumes something scarce).  The plan is found by the simplex method; the
    prices are found by handing the dual program to the same solver as a fresh
    problem, with nothing carried over from the first solve.
    """
    rng = random.Random(seed)
    pairs = []
    while len(pairs) < count:
        n = rng.randint(2, 4)
        m = rng.randint(2, 4)
        lp = LP.build(
            c=[rng.randint(1, 40) for _ in range(n)],
            A=[[rng.randint(1, 9) for _ in range(n)] for _ in range(m)],
            b=[rng.randint(5, 60) for _ in range(m)],
            op="<=", sense="max")
        best, prices = solve(lp), solve(dual(lp))
        if best.ok and prices.ok:
            pairs.append((best.value, prices.value))

    fig, ax = figure(6.0, 5.4)
    heading(ax, "320 workshops, each solved twice")
    top = float(max(max(p) for p in pairs)) * 1.06
    ax.plot([0, top], [0, top], color=TEXT_FAINT, linewidth=1.0,
            linestyle=(0, (4, 4)), zorder=2)
    ax.plot([float(p[0]) for p in pairs], [float(p[1]) for p in pairs], "o", markersize=5.5,
            color=PLAN, alpha=0.45, zorder=4, markeredgewidth=0)
    ax.set_xlim(0, top)
    ax.set_ylim(0, top)
    ax.set_xlabel("the best plan's profit", fontsize=10, color=PLAN, labelpad=7)
    ax.set_ylabel("the cheapest prices' bill", fontsize=10, color=PRICE, labelpad=7)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)
    ax.set_aspect("equal")

    # exact fractions on both sides, so this is a real zero and not a rounded one
    worst = max(abs(a - b) for a, b in pairs)
    tag(ax, top * 0.05, top * 0.88,
        f"every point is on the line\nlargest disagreement, in exact\n"
        f"arithmetic, across all {len(pairs)}: {worst}",
        color=TEXT_DIM, size=10.5)
    save(fig, OUT / "always.png")


if __name__ == "__main__":
    meet_gif()
    always_png()
