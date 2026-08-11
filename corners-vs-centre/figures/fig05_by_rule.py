"""The same cube, the same code, three choices of which column to enter.

This is the figure that settles what the cube proves. If the exponential blow
up belonged to the method, changing one function could not move it. Changing
that one function moves it from doubling to a golden-ratio climb to a single
pivot, which means the cube is an argument about a rule.

The two step counts are exact and closed form, and the tests check them
against these formulas rather than against a stored number:

    Dantzig   2^n - 1            visits every corner of the cube
    Bland     2*Fib(n+1) - 1     still exponential, base phi rather than 2
"""

import numpy as np

from illuminate.draw import (PLAN, PRICE, SURFACE, TEXT_DIM, chapter_dir,
                             figure, heading, save, style, tag)
from twopaths.simplex import bland, dantzig, klee_minty, solve, steepest_edge

OUT = chapter_dir("05-not-the-rule")

SIZES = list(range(2, 13))
RULES = [("Dantzig's rule", dantzig, PRICE),
         ("Bland's rule", bland, TEXT_DIM),
         ("steepest edge", steepest_edge, PLAN)]


def counts():
    out = {}
    for name, rule, _ in RULES:
        out[name] = [solve(*klee_minty(n), rule=rule).steps for n in SIZES]
    return out


def by_rule_png():
    measured = counts()
    fig, ax = figure(7.6, 5.0)
    fig.subplots_adjust(top=0.85, bottom=0.15, left=0.13, right=0.96)
    heading(ax, "one line of the code changes, and so does the exponent")
    style(ax, "dimension of the cube", "pivots to the answer (log scale)")
    ax.set_yscale("log")

    for name, _, colour in RULES:
        ax.plot(SIZES, measured[name], color=colour, linewidth=2.2, marker="o",
                markersize=6, markeredgecolor=SURFACE, markeredgewidth=1.6,
                zorder=6)

    ax.set_ylim(0.6, 1e4)
    tag(ax, 5.3, 1.6e3, "Dantzig: 2$^n$ - 1, which is every\ncorner the cube has", color=PRICE, size=10.5)
    tag(ax, 8.15, 21, "Bland: 2 Fib(n+1) - 1", color=TEXT_DIM, size=10.5)
    tag(ax, 4.6, 1.5, "steepest edge: one pivot, at every size", color=PLAN,
        size=10.5)

    save(fig, OUT / "by-rule.png", tight=False)
    return measured


if __name__ == "__main__":
    by_rule_png()
