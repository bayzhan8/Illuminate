"""Chapter 1: the region of possible plans, and the sweep that finds its best corner."""

from lpduality import workshop as w
from illuminate.draw import (TEXT, TEXT_DIM, TEXT_FAINT, OK, PLAN, PRICE, animate, chapter_dir,
                            figure, heading, plate, margin_note, save, tag)
from scene import (WINDOW, callout, draw_axes, draw_constraint, draw_region,
                   mark_plan, ordered_corners, profit_line)

OUT = chapter_dir("01-the-workshop")


def region_png():
    """Every plan the workshop could actually carry out, and the corners of that set.

    Straight boundaries because doubling a plan doubles what it consumes. That
    proportionality is the only modelling assumption in the guide, and it is
    what gives the region flat sides and sharp corners rather than curves.
    """
    fig, ax = figure(7.6, 5.0)
    draw_axes(ax)
    heading(ax, "what the workshop can build")

    # each label is placed where its own line runs through empty paper, which
    # is outside the region for all three of them
    for i, lx in enumerate((7.0, 11.4, 8.7)):
        draw_constraint(ax, w.PRIMAL, i, color=TEXT, lw=1.3, label_x=lx)
    draw_region(ax, w.PRIMAL)

    for corner in ordered_corners(w.PRIMAL):
        ax.plot([corner[0]], [corner[1]], "o", markersize=5.5, color=PLAN, zorder=6)

    mark_plan(ax, w.PLAN)
    callout(ax, f"9 tables, 4 chairs\n{w.money(w.BEST_PROFIT)}", w.PLAN,
            at=(10.2, 9.3), color=PLAN)
    tag(ax, 1.1, 3.0, "every plan in here is one\nyou could actually carry out",
        color=TEXT_DIM, size=10)
    save(fig, OUT / "region.png")


def sweep_gif(frames=46, fps=12):
    """Push the equal-profit line outwards until it is about to leave the region.

    Each position of the line is a set of plans worth the same amount. Sliding
    it outwards raises that amount; the last plan it touches is the best one.
    It lands on a corner, which is why every method in this repository spends
    its time on corners.
    """
    fig, ax = figure(7.6, 5.0)
    fig.subplots_adjust(bottom=0.22)
    draw_axes(ax)
    heading(ax, "raise the profit until the line lets go")

    for i in range(w.PRIMAL.m):
        draw_constraint(ax, w.PRIMAL, i, color=TEXT, lw=1.1, label=False)
    draw_region(ax, w.PRIMAL)

    line = profit_line(ax, 0)
    dot, = ax.plot([], [], "o", markersize=9.5, color=PLAN, zorder=7,
                   markeredgecolor="#fffff8", markeredgewidth=2.0)
    note = margin_note(fig)
    top = float(w.BEST_PROFIT)

    def update(i):
        i = min(i, frames - 1)
        level = top * i / (frames - 1)
        line.set_ydata([(level - 30 * x) / 20 for x in [WINDOW[0], WINDOW[1]]])
        if i == frames - 1:
            dot.set_data([float(w.PLAN[0])], [float(w.PLAN[1])])
            note.set_text(f"every plan on this line is worth {w.money(w.BEST_PROFIT)}\n"
                          "one plan is left: 9 tables and 4 chairs")
            note.set_color(PLAN)
            line.set_color(PLAN)
        else:
            dot.set_data([], [])
            note.set_text(f"every plan on this line is worth ${level:,.0f}\n"
                          "the line still crosses the region: push it further")
            note.set_color(TEXT_DIM)
            line.set_color(PRICE)
        return []

    animate(fig, update, frames, OUT / "sweep.gif", fps=fps)


if __name__ == "__main__":
    region_png()
    sweep_gif()
