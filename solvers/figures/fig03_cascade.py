"""Chapter 3: how much is left after each round, on both instances.

The shape of these lines is the argument. If presolve were a list of tricks
applied once, the drop would happen in round one and the rest would be flat.
It is not flat, because each reduction is what lets the next one fire.
"""

from illuminate.draw import (HAIRLINE, PLAN, PRICE, TEXT_DIM, TEXT_FAINT,
                             chapter_dir, figure, heading, save, style, tag)
from solvers import library as L
from solvers.presolve import presolve

OUT = chapter_dir("03-the-cascade")


def _trace(model, rounds):
    xs, rows, cols, nz = [], [], [], []
    for k in range(rounds + 1):
        r, c, z = presolve(model, stop_after=k).after
        xs.append(k); rows.append(r); cols.append(c); nz.append(z)
    return xs, rows, cols, nz


def cascade_png():
    import matplotlib.pyplot as plt

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.6, 4.3))
    fig.subplots_adjust(left=0.085, right=0.975, bottom=0.17, top=0.80, wspace=0.26)
    fig.patch.set_facecolor("#fffff8")

    for ax, model, rounds, title in (
            (axL, L.SMALL, L.SMALL_PRESOLVED.rounds, "three products, two periods"),
            (axR, L.BIG, L.BIG_PRESOLVED.rounds, "eight products, six periods")):
        ax.set_facecolor("#fffff8")
        heading(ax, title)
        xs, rows, cols, nz = _trace(model, rounds)

        ax.plot(xs, nz, color=PLAN, linewidth=2.4, zorder=5,
                drawstyle="steps-post")
        ax.plot(xs, rows, color=PRICE, linewidth=1.8, zorder=4,
                drawstyle="steps-post")
        ax.plot(xs, cols, color=TEXT_FAINT, linewidth=1.4, zorder=3,
                drawstyle="steps-post", linestyle=(0, (4, 2)))

        ax.set_xlim(0, rounds)
        ax.set_ylim(0, max(nz) * 1.12)
        ax.set_xlabel("rounds of the loop", fontsize=10, color=TEXT_DIM, labelpad=6)
        ax.set_ylabel("still in the model", fontsize=10, color=TEXT_DIM, labelpad=6)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
        ax.set_axisbelow(True)

        # Direct labels, placed early where the three series are still far
        # apart. Labelling them at the right-hand end needs leader lines, and a
        # leader climbing away from a falling series reads as data.
        k = max(1, round(rounds * 0.08))
        lift = max(nz) * 0.028
        for series, label, colour in ((nz, "nonzeros", PLAN),
                                      (cols, "columns", TEXT_FAINT),
                                      (rows, "rows", PRICE)):
            ax.text(k + rounds * 0.035, series[k] + lift, label, fontsize=10,
                    color=colour, ha="left", va="bottom")

    save(fig, OUT / "cascade.png")


if __name__ == "__main__":
    cascade_png()
