"""Chapter 0: the poster. One term of difference, on a real problem."""

import numpy as np

from firstorder import story as s
from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, animate, chapter_dir, figure, heading,
                             margin_note, tag)

OUT = chapter_dir("00-what-this-is")
# 130 steps at 15fps is under nine seconds and still shows a dozen full
# cycles of the method that never settles
SHOWN = 130


def hero_gif(fps=15):
    cycling = s.cycling_run(SHOWN)
    settling = s.converging_run(SHOWN)
    cyc = -(s.WORKSHOP.c @ cycling.xs.T)
    con = -(s.WORKSHOP.c @ settling.xs.T)

    fig, ax = figure(8.6, 4.4)
    fig.subplots_adjust(bottom=0.26, top=0.82, left=0.11, right=0.96)
    heading(ax, "two methods, one term apart, on the same workshop")
    ax.axhline(s.TRUE_VALUE, color=TEXT_FAINT, linewidth=1.1,
               linestyle=(0, (4, 4)), zorder=3)
    ax.text(SHOWN * 0.99, s.TRUE_VALUE + 22, "the answer: $350", color=TEXT_FAINT,
            fontsize=9.5, ha="right")
    ax.set_xlim(0, SHOWN)
    ax.set_ylim(-40, 820)
    ax.set_xlabel("iterations", fontsize=10, color=TEXT_DIM, labelpad=6)
    ax.set_ylabel("what the plan claims to be worth", fontsize=10,
                  color=TEXT_DIM, labelpad=6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)

    a, = ax.plot([], [], color=PRICE, linewidth=1.8, zorder=5)
    b, = ax.plot([], [], color=PLAN, linewidth=2.0, zorder=6)
    tag(ax, 8, 745, "prices chasing the old plan", color=PRICE, size=10)
    tag(ax, 8, 250, "prices anticipating the new one", color=PLAN, size=10)
    note = margin_note(fig, x=0.05, size=10.5)

    def update(i):
        i = min(i, SHOWN)
        a.set_data(range(i + 1), cyc[:i + 1])
        b.set_data(range(i + 1), con[:i + 1])
        note.set_text(
            f"step {i:>3}     chasing {cyc[i]:7.1f}     anticipating {con[i]:7.1f}\n"
            + ("one of them will do this forever"
               if i > 40 else "both start from nothing"))
        note.set_color(TEXT)
        return []

    animate(fig, update, SHOWN + 1, OUT / "hero.gif", fps=fps, hold=3.4)


if __name__ == "__main__":
    hero_gif()
