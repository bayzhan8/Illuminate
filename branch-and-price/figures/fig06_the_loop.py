"""Chapters 6 to 8: the loop running, and how little of the list it touches."""

from bandp import mill as m
from illuminate.draw import (INK, INK2, MUTED, OK, PAPER, PLAN, PRICE, RULE,
                             animate, chapter_dir, figure, heading, readout, save, tag)
from boards import board_axes, draw_board

OUT_LOOP = chapter_dir("07-the-loop")
OUT_TOUCH = chapter_dir("07-the-loop")


def loop_gif(fps=1.1):
    """One frame per round: what the master says, and what the prices ask for.

    Slow on purpose. Each frame is a full turn of the loop and carries four
    numbers the reader has to actually read, so it is paced to be read rather
    than watched.
    """
    inst = m.BOARDS
    rounds = m.ROUNDS
    frames = len(rounds)

    fig, ax = figure(8.2, 3.4)
    fig.subplots_adjust(left=0.20, right=0.97, top=0.80, bottom=0.30)
    heading(ax, "the loop: solve, price, add, repeat")
    board_axes(ax, inst, rows=1, row_gap=1.0)
    note = readout(fig, x=0.045, size=10.5)

    def update(i):
        i = min(i, frames - 1)
        r = rounds[i]
        for patch in list(ax.patches):
            patch.remove()
        for text in list(ax.texts):
            text.remove()
        draw_board(ax, 0.2, r.best_pattern, inst, height=0.6,
                   label=inst.describe(r.best_pattern), dim=not r.added)
        prices = "   ".join(f"{w}ft {str(d)}" for w, d in zip(inst.widths, r.duals))
        if r.added:
            note.set_text(
                f"round {i + 1}   holding {len(r.patterns)} patterns   "
                f"master says {m.decimal(r.value)} boards\n"
                f"prices: {prices}\n"
                f"best pattern is worth {r.best_value} > 1 — add it and go again")
            note.set_color(INK)
        else:
            note.set_text(
                f"round {i + 1}   holding {len(r.patterns)} patterns   "
                f"master says {m.decimal(r.value)} boards\n"
                f"prices: {prices}\n"
                f"best pattern is worth exactly 1 — nothing is missing, stop")
            note.set_color(OK)
        return []

    animate(fig, update, frames, OUT_LOOP / "loop.gif", fps=fps, hold=4.0)


def touched_png():
    """The bigger order's thirty patterns, with the six the loop ever built."""
    inst = m.SCALE
    every = m.SCALE_PATTERNS
    used = set(m.SCALE_ROUNDS[-1].patterns)

    fig, ax = figure(8.0, 6.4)
    fig.subplots_adjust(left=0.05, right=0.97, top=0.90, bottom=0.04)
    heading(ax, f"{m.SCALE_TOUCHED} of the {len(every)} patterns were ever built")

    rows = (len(every) + 1) // 2
    ax.set_xlim(-2, inst.width * 2 + 14)
    ax.set_ylim(-0.6, rows * 0.62 + 0.85)
    ax.set_xticks([]); ax.set_yticks([])
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)

    for k, pattern in enumerate(every):
        column, row = divmod(k, rows)
        y = (rows - 1 - row) * 0.62
        offset = column * (inst.width + 14)
        hot = pattern in used
        x = offset
        for i, count in enumerate(pattern):
            for _ in range(count):
                from matplotlib.patches import Rectangle
                ax.add_patch(Rectangle(
                    (x, y), inst.widths[i], 0.42,
                    facecolor=PLAN if hot else PAPER,
                    alpha=0.85 if hot else 1.0,
                    edgecolor=INK if hot else "#c9c7bd",
                    linewidth=1.0 if hot else 0.8, zorder=4))
                x += inst.widths[i]
        if hot:
            ax.text(offset + inst.width + 1.5, y + 0.21, "built", ha="left",
                    va="center", fontsize=8, color=PLAN)
    tag(ax, 0, rows * 0.62 + 0.42,
        "the rest were never written down, and never needed to be",
        color=MUTED, size=9.5)
    save(fig, OUT_TOUCH / "touched.png", tight=False)


if __name__ == "__main__":
    loop_gif()
    touched_png()
