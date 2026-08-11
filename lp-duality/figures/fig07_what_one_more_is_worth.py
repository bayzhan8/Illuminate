"""Chapter 7: buy one more plank, and watch where the money comes from.

Sliding the plank stock moves one line of the picture.  The region grows, the
best corner slides along the hours line, and the profit goes up by the plank
price every time -- for a while.

The animation deliberately runs past the point where that stops.  Somewhere
above 45 planks the saw line catches the corner, the picture stops changing,
and the extra planks pile up unused.  The reader sees the price die before the
next chapter explains why it had to.
"""

from fractions import Fraction

from lpduality import workshop as w
from lpduality.draw import (INK, INK2, MUTED, OK, PAPER, PLAN, PRICE, RULE,
                            animate, chapter_dir, figure, heading, readout, tag)
from lpduality.lp import solve
from lpduality.sensitivity import with_rhs
from scene import WINDOW, draw_axes, draw_constraint, draw_region, mark_plan

OUT = chapter_dir("07-what-one-more-is-worth")

LOW, HIGH = 38, 50


def shadow_gif(frames=50, fps=11):
    fig, ax = figure(7.8, 5.0)
    fig.subplots_adjust(bottom=0.26, top=0.84)
    draw_axes(ax)
    heading(ax, "one more plank, and one more, and one more")

    for i in (1, 2):
        draw_constraint(ax, w.PRIMAL, i, label=False, color=MUTED, lw=1.2)
    plank_line, = ax.plot([], [], color=PRICE, linewidth=2.0, zorder=4)
    edge, = ax.plot([], [], color=PLAN, linewidth=1.8, zorder=3)
    fill = ax.fill([], [], color=PLAN, alpha=0.13, zorder=1, linewidth=0)[0]
    dot, = ax.plot([], [], "o", markersize=9, color=PLAN, zorder=7,
                   markeredgecolor=PAPER, markeredgewidth=2)
    trail, = ax.plot([], [], color=PLAN, linewidth=1.0, alpha=0.4, zorder=5,
                     linestyle=(0, (2, 2)))
    note = readout(fig, x=0.035, size=10.5)

    from scene import ordered_corners
    seen_x, seen_y = [], []
    bend = float(w.WOOD_TO)

    def update(i):
        i = min(i, frames - 1)
        stock = LOW + (HIGH - LOW) * i / (frames - 1)
        lp = with_rhs(w.PRIMAL, w.WOOD, Fraction(stock).limit_denominator(1000))
        best = solve(lp)

        xs = [WINDOW[0], WINDOW[1]]
        plank_line.set_data(xs, [(stock - 4 * x) / 2 for x in xs])
        corners = ordered_corners(lp)
        if corners:
            loop = corners + [corners[0]]
            edge.set_data([p[0] for p in loop], [p[1] for p in loop])
            fill.set_xy(corners)
        x, y = float(best.x[0]), float(best.x[1])
        dot.set_data([x], [y])
        seen_x.append(x)
        seen_y.append(y)
        trail.set_data(seen_x, seen_y)

        price = float(best.prices[w.WOOD])
        if stock < bend:
            note.set_text(f"{stock:.1f} planks    profit ${float(best.value):,.2f}\n"
                          f"each extra plank is adding ${price:.2f}")
            note.set_color(INK)
        else:
            note.set_text(f"{stock:.1f} planks    profit ${float(best.value):,.2f}\n"
                          "the saw is the problem now — extra planks add nothing")
            note.set_color(PRICE)
        return []

    animate(fig, update, frames, OUT / "shadow.gif", fps=fps, hold=3.0)


if __name__ == "__main__":
    shadow_gif()
