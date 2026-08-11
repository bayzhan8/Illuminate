"""Chapters 8 and 9: it finds the right answer, and what that costs."""

import numpy as np

from firstorder import story as s
from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, figure, heading, save, tag)

OUT_AGREE = chapter_dir("11-the-same-answer")
OUT_COST = chapter_dir("12-what-it-costs")


def agree_png():
    """The distance to the answer the exact simplex already gave us."""
    fig, ax = figure(8.0, 4.5)
    fig.subplots_adjust(top=0.84, bottom=0.16, left=0.13, right=0.96)
    heading(ax, "closing on the answer the exact solver already knew")
    curve = s.distance_curve(s.converging_run(1200))
    ax.semilogy(np.maximum(curve, 1e-16), color=PLAN, linewidth=2.2, zorder=5)
    ax.set_xlim(0, 1200)
    ax.set_ylim(1e-16, 40)
    ax.set_xlabel("iterations", fontsize=10, color=TEXT_DIM, labelpad=6)
    ax.set_ylabel("distance from the exact answer", fontsize=10,
                  color=TEXT_DIM, labelpad=6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, which="both", color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)
    ax.text(0.04, 0.08,
            "the target is 9 tables and 4 chairs with prices 6.25, 2.50 and 0,\n"
            "computed in exact fractions by a method sharing no code with this one",
            transform=ax.transAxes, fontsize=9.5, color=TEXT_DIM,
            bbox=dict(boxstyle="square,pad=0.4", facecolor=SURFACE,
                      edgecolor="none"), zorder=9)
    save(fig, OUT_AGREE / "agree.png", tight=False)


def cost_png():
    import matplotlib.pyplot as plt

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10.0, 4.4),
                                   gridspec_kw={"width_ratios": [1.25, 1]})
    fig.subplots_adjust(left=0.10, right=0.97, bottom=0.17, top=0.84, wspace=0.32)

    # --- left: the plan is illegal until it has converged
    heading(axL, "how far outside the rules the plan still is")
    ladder = s.feasibility_ladder((5, 10, 25, 50, 100, 250, 500, 1000, 2500))
    steps = [n for n, _, _ in ladder]
    viol = [max(v, 1e-16) for _, _, v in ladder]
    axL.loglog(steps, viol, color=PRICE, linewidth=2.2, zorder=5)
    axL.loglog(steps, viol, "o", color=PRICE, markersize=5, zorder=6,
               markeredgecolor=SURFACE, markeredgewidth=1.5)
    axL.axhline(1e-15, color=OK, linewidth=1.4, linestyle=(0, (4, 4)), zorder=4)
    axL.text(6, 3e-15, "every simplex iterate sits here: exactly legal",
             color=OK, fontsize=9)
    axL.set_xlabel("iterations", fontsize=10, color=TEXT_DIM, labelpad=6)
    axL.set_ylabel("worst rule broken, in planks", fontsize=10,
                   color=TEXT_DIM, labelpad=6)
    axL.set_ylim(1e-16, 5)
    for side in ("top", "right"):
        axL.spines[side].set_visible(False)
    axL.grid(True, which="both", color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    axL.set_axisbelow(True)

    # --- right: on a tie it lands between the corners
    heading(axR, "and on a tie it does not pick a corner")
    interior, corner = s.tie_answers()
    axR.plot([1, 0], [0, 1], color=TEXT, linewidth=2.4, zorder=4)
    axR.plot([corner[0]], [corner[1]], "o", color=OK, markersize=10, zorder=7,
             markeredgecolor=SURFACE, markeredgewidth=2)
    axR.plot([interior[0]], [interior[1]], "o", color=PRICE, markersize=10,
             zorder=7, markeredgecolor=SURFACE, markeredgewidth=2)
    axR.text(corner[0] - 0.04, corner[1] + 0.07, "simplex", color=OK,
             fontsize=9.5, ha="right")
    axR.text(interior[0] + 0.06, interior[1] + 0.05, "first-order", color=PRICE,
             fontsize=9.5)
    axR.text(0.30, 0.30, "every point on this line\nis equally optimal",
             color=TEXT_DIM, fontsize=9, ha="center")
    axR.set_xlim(-0.12, 1.25)
    axR.set_ylim(-0.12, 1.25)
    axR.set_xlabel("one product", fontsize=10, color=TEXT_DIM, labelpad=6)
    axR.set_ylabel("the other", fontsize=10, color=TEXT_DIM, labelpad=6)
    for side in ("top", "right"):
        axR.spines[side].set_visible(False)
    axR.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    axR.set_axisbelow(True)
    axR.set_aspect("equal")
    save(fig, OUT_COST / "cost.png", tight=False)


if __name__ == "__main__":
    agree_png()
    cost_png()
