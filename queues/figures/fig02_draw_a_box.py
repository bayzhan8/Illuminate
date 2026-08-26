"""Chapter 2: the same area, counted twice.

This is the whole theorem and it needs no probability at all.

Draw the arrivals staircase and the departures staircase. The region between
them has height equal to the number of people in the queue. Slice it
vertically and you are adding up how many people were present at each moment,
which is the manager's number. Slice it horizontally and you are adding up how
long each person stayed, which is the customer's number. Same region.

The animation re-tiles one shaded shape from vertical strips into horizontal
bars. Nothing is approximated at any point, which is why the figure can be
built from a handful of hand-placed customers rather than from a simulation.
"""

import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, animate, chapter_dir, figure, heading,
                             margin_note, save, tag)

OUT = chapter_dir("02-draw-a-box")

# Eight customers, placed by hand so the picture is legible and the arithmetic
# is checkable on the page. The window starts and ends empty, which is what
# makes the two counts exactly equal rather than nearly equal.
#
# Departures are in the same order as arrivals here. Little's law does not
# need that -- chapter 3 is largely about what it does not need -- but the
# *picture* does: served in order, customer j's bar occupies exactly the strip
# between heights j and j+1, so the bars tile the region between the
# staircases with nothing left over. Let the departures cross and the identity
# survives while the tiling stops being visible, which would make this a worse
# figure and a worse argument.
ARRIVALS = [0.5, 1.2, 2.0, 3.4, 4.1, 5.6, 7.0, 7.6]
DEPARTURES = [1.9, 2.6, 3.6, 5.0, 6.2, 6.9, 8.1, 8.7]
STAYS = [d - a for a, d in zip(ARRIVALS, DEPARTURES)]
WINDOW = (0.0, 9.2)

assert DEPARTURES == sorted(DEPARTURES), "the tiling argument needs served-in-order"
assert all(s > 0 for s in STAYS)


def occupancy(t):
    return sum(1 for a, dpt in zip(ARRIVALS, DEPARTURES) if a <= t < dpt)


def staircases(ax):
    grid = np.linspace(*WINDOW, 3000)
    arrived = [sum(1 for a in ARRIVALS if a <= t) for t in grid]
    left = [sum(1 for x in DEPARTURES if x <= t) for t in grid]
    ax.step(grid, arrived, where="post", color=PLAN, linewidth=1.9, zorder=5)
    ax.step(grid, left, where="post", color=PRICE, linewidth=1.9, zorder=5)
    tag(ax, 8.0, 8.35, "arrived", color=PLAN, size=10)
    tag(ax, 8.4, 6.6, "left", color=PRICE, size=10)
    return grid, arrived, left


def setup(ax, title):
    heading(ax, title)
    ax.set_xlim(*WINDOW)
    ax.set_ylim(-0.35, 9.1)
    ax.set_xlabel("time", fontsize=10, color=TEXT_DIM, labelpad=6)
    ax.set_ylabel("customers", fontsize=10, color=TEXT_DIM, labelpad=6)
    ax.set_xticks(range(0, 10, 2))
    ax.set_yticks(range(0, 9, 2))
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)


def two_counts_gif(fps=14):
    """Fill the region with vertical strips, then rebuild it from horizontal bars."""
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle

    # The sweep is repetitive once the reader has the idea, so it goes quickly.
    # The bars are the payoff and each one has to land separately, so they get
    # half a second each.
    # The strip edges are the event times, not a uniform grid. On a uniform
    # grid the occupancy jumps inside a strip, midpoint sampling misses it,
    # and the running total lands on 11.73 for a region whose area is 11.60 --
    # which would have this figure disproving the identity it exists to show.
    # Between two consecutive events the occupancy is constant, so these
    # rectangles are the region exactly.
    edges = np.array(sorted({WINDOW[0], WINDOW[1], *ARRIVALS, *DEPARTURES}))
    strips = len(edges) - 1
    bars = len(ARRIVALS)
    hold_between = 10
    frames_per_bar = 7
    frames = strips + hold_between + bars * frames_per_bar + 10

    fig, ax = figure(8.4, 4.6)
    fig.subplots_adjust(bottom=0.26, top=0.84)
    setup(ax, "one region, two ways of measuring it")
    grid, arrived, left = staircases(ax)
    note = margin_note(fig, x=0.04, size=10.5)
    drawn: list = []

    total_area = sum(STAYS)
    exact = sum(occupancy((edges[s] + edges[s + 1]) / 2) * (edges[s + 1] - edges[s])
                for s in range(strips))
    assert abs(exact - total_area) < 1e-12, (exact, total_area)

    def clear():
        while drawn:
            drawn.pop().remove()

    def update(i):
        i = min(i, frames - 1)
        clear()

        if i < strips:                       # --- vertical: count heads, repeatedly
            k = i + 1
            covered = 0.0
            for s in range(k):
                lo, hi = edges[s], edges[s + 1]
                height = occupancy((lo + hi) / 2)
                if height:
                    drawn.append(ax.add_patch(Rectangle(
                        (lo, 0), hi - lo, height, facecolor=PLAN, alpha=0.30,
                        edgecolor=PLAN, linewidth=0.4, zorder=3)))
                covered += height * (hi - lo)
            note.set_text(
                "counting heads: how many people are here, moment by moment\n"
                f"running total of person-hours   {covered:5.2f}")
            note.set_color(PLAN)

        elif i < strips + hold_between:      # --- hold the finished region
            for s in range(strips):
                lo, hi = edges[s], edges[s + 1]
                height = occupancy((lo + hi) / 2)
                if height:
                    drawn.append(ax.add_patch(Rectangle(
                        (lo, 0), hi - lo, height, facecolor=PLAN, alpha=0.30,
                        edgecolor=PLAN, linewidth=0.4, zorder=3)))
            note.set_text(f"the manager's total: {total_area:.2f} person-hours\n"
                          "now count the same region the other way")
            note.set_color(TEXT)

        else:                                # --- horizontal: one bar per person
            k = min(bars, (i - strips - hold_between) // frames_per_bar + 1)
            order = np.argsort(ARRIVALS)
            covered = 0.0
            for level, person in enumerate(order[:k]):
                drawn.append(ax.add_patch(Rectangle(
                    (ARRIVALS[person], level), STAYS[person], 1.0,
                    facecolor=PRICE, alpha=0.34, edgecolor=PRICE,
                    linewidth=0.8, zorder=4)))
                covered += STAYS[person]
            note.set_text(
                f"asking each person how long they stayed   ({k} of {bars})\n"
                f"running total of person-hours   {covered:5.2f}"
                + ("   the same number" if k == bars else ""))
            note.set_color(OK if k == bars else PRICE)
        return []

    animate(fig, update, frames, OUT / "two-counts.gif", fps=fps, hold=3.2)


def region_png():
    """The still: the region, with both readings labelled."""
    from matplotlib.patches import Rectangle

    fig, ax = figure(8.4, 4.4)
    fig.subplots_adjust(top=0.84, bottom=0.14)
    setup(ax, "the gap between the staircases is the queue")
    grid, arrived, left = staircases(ax)

    ax.fill_between(grid, left, arrived, step="post", color=PLAN, alpha=0.16,
                    zorder=2, linewidth=0)
    for level, person in enumerate(np.argsort(ARRIVALS)):
        ax.add_patch(Rectangle((ARRIVALS[person], level), STAYS[person], 1.0,
                               facecolor="none", edgecolor=PRICE, linewidth=1.0,
                               linestyle=(0, (3, 2)), zorder=4))

    tag(ax, 0.35, 5.4,
        "vertical slices add up to\nthe person-hours the\nmanager sees",
        color=PLAN, size=9.5)
    tag(ax, 4.6, 2.2,
        "horizontal bars add up to\nthe same person-hours,\none customer at a time",
        color=PRICE, size=9.5)
    save(fig, OUT / "region.png", tight=False)


if __name__ == "__main__":
    region_png()
    two_counts_gif()
