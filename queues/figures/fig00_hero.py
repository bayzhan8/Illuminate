"""Chapter 0: the poster. The wait against how busy the desk is."""

import numpy as np

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, animate, chapter_dir, figure, heading,
                             margin_note, tag)
from queues import desk as d

OUT = chapter_dir("00-what-this-is")


def hero_gif(frames=54, fps=12):
    """Walk the arrival rate up and watch the wait leave the page."""
    fig, ax = figure(8.4, 4.4)
    fig.subplots_adjust(bottom=0.27, top=0.82, left=0.11, right=0.96)
    heading(ax, "the same desk, at different levels of busy")

    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 130)
    ax.set_xlabel("fraction of the time the clerk is busy", fontsize=10,
                  color=TEXT_DIM, labelpad=7)
    ax.set_ylabel("minutes of waiting", fontsize=10, color=TEXT_DIM, labelpad=7)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 0.9, 1.0])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)

    grid = np.linspace(0.001, 0.985, 900)
    curve = [float(r / (1 - r)) * 6 for r in grid]        # W_q = rho/(1-rho) * E[S]
    drawn, = ax.plot([], [], color=PLAN, linewidth=2.4, zorder=5)
    dot, = ax.plot([], [], "o", color=PLAN, markersize=8, zorder=7,
                   markeredgecolor=SURFACE, markeredgewidth=2)
    note = margin_note(fig, x=0.05, size=10.5)

    def update(i):
        i = min(i, frames - 1)
        t = i / (frames - 1)
        rho = 0.001 + (0.985 - 0.001) * (t ** 1.7)        # linger near the wall
        k = int(np.searchsorted(grid, rho))
        drawn.set_data(grid[:k + 1], curve[:k + 1])
        wait = float(rho / (1 - rho)) * 6
        dot.set_data([rho], [min(wait, 128)])
        note.set_text(
            f"busy {rho * 100:4.1f}% of the time     "
            f"average wait {wait:6.1f} minutes\n"
            + ("the clerk still serves everyone in six minutes"
               if rho < 0.8 else
               "the clerk has not slowed down. the queue has."))
        note.set_color(TEXT if rho < 0.9 else PRICE)
        return []

    animate(fig, update, frames, OUT / "hero.gif", fps=fps, hold=3.4)


if __name__ == "__main__":
    hero_gif()
