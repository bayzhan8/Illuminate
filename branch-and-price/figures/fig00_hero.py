"""Chapter 0: the poster. Two relaxations of the same order, and where they stop.

The obvious model cannot rule out six boards. The pattern model proves you need
seven, and seven is the answer. The whole guide is the distance between those
two claims, and how it is closed without ever writing the patterns down.
"""

import math

from bandp import mill as m
from illuminate.draw import (TEXT, TEXT_DIM, TEXT_FAINT, OK, SURFACE, PLAN, PRICE, HAIRLINE,
                             animate, chapter_dir, figure, heading, margin_note, tag)

OUT = chapter_dir("00-what-this-is")


def hero_gif(frames=48, fps=12):
    fig, ax = figure(8.6, 3.9)
    fig.subplots_adjust(bottom=0.30, top=0.80, left=0.06, right=0.97)
    heading(ax, "how many boards does this order really need?")

    ax.set_xlim(4.6, 8.2)
    ax.set_ylim(-1.0, 1.25)
    ax.set_yticks([])
    ax.set_xticks([5, 6, 7, 8])
    ax.set_xlabel("boards", fontsize=10, color=TEXT_DIM, labelpad=7)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.grid(True, axis="x", color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)

    naive, dw, answer = float(m.NAIVE_BOUND), float(m.DW_BOUND), float(m.ANSWER)

    bar = ax.barh([0.35], [0], left=4.6, height=0.34, color=PLAN, zorder=4,
                  edgecolor=SURFACE, linewidth=2)[0]
    marker, = ax.plot([], [], "o", color=PRICE, markersize=9, zorder=7,
                      markeredgecolor=SURFACE, markeredgewidth=2)
    ax.axvline(answer, color=TEXT_FAINT, linewidth=1.0, linestyle=(0, (4, 4)), zorder=2)
    tag(ax, answer + 0.06, 1.05, "the answer: 7 boards", color=TEXT_DIM, size=10)
    note = margin_note(fig, x=0.06, size=10.5)

    def update(i):
        i = min(i, frames - 1)
        t = i / (frames - 1)
        if t < 0.45:                     # the obvious model creeps up
            here = naive * min(1.0, t / 0.4)
            reached, phase = here, "naive"
        elif t < 0.8:                    # the pattern model pushes past six
            u = (t - 0.45) / 0.35
            reached, phase = naive + (dw - naive) * u, "dw"
        else:
            reached, phase = dw, "done"
        bar.set_width(max(0.0, reached - 4.6))
        marker.set_data([reached], [0.35])
        if phase == "naive":
            note.set_text("the obvious model proves you need at least "
                          f"{reached:.2f} boards\nso six might be enough — "
                          "it cannot say otherwise")
            note.set_color(TEXT_DIM)
            bar.set_color(TEXT_FAINT)
        elif phase == "dw":
            note.set_text(f"one variable per cutting pattern proves at least "
                          f"{reached:.2f}\nsix is now impossible")
            note.set_color(PLAN)
            bar.set_color(PLAN)
        else:
            note.set_text("at least 6 and a half, so at least 7 — and 7 can be "
                          "cut\nfound without ever listing the patterns")
            note.set_color(OK)
            bar.set_color(PLAN)
        return []

    animate(fig, update, frames, OUT / "hero.gif", fps=fps, hold=3.2)


if __name__ == "__main__":
    hero_gif()
