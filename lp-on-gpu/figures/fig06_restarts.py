"""Chapters 6 and 7: what the spiral costs, and what cancelling it buys."""

import numpy as np

from firstorder import story as s
from firstorder.methods import pdhg, spiral_anatomy
from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, figure, heading, save, tag)

OUT_ANATOMY = chapter_dir("09-fast-turn-slow-shrink")
OUT_RESTART = chapter_dir("10-cancel-the-rotation")


def anatomy_png():
    """Rotation and contraction, against the step size, from the closed forms."""
    fig, ax = figure(8.0, 4.6)
    fig.subplots_adjust(top=0.84, bottom=0.16, left=0.11, right=0.88)
    heading(ax, "what a bigger step buys, and what it costs")

    steps = np.linspace(0.02, 0.97, 400)
    rotation = [spiral_anatomy(1.0, t, t)["rotation_degrees"] for t in steps]
    shrink = [(1 - spiral_anatomy(1.0, t, t)["contraction"]) * 100 for t in steps]

    ax.plot(steps, rotation, color=PRICE, linewidth=2.3, zorder=5)
    ax.set_xlabel("step size", fontsize=10, color=TEXT_DIM, labelpad=6)
    ax.set_ylabel("degrees turned per iteration", fontsize=10, color=PRICE, labelpad=6)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 92)
    for side in ("top",):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)

    twin = ax.twinx()
    twin.plot(steps, shrink, color=PLAN, linewidth=2.3, zorder=5)
    twin.set_ylabel("percent closer per iteration", fontsize=10, color=PLAN, labelpad=8)
    twin.set_ylim(0, 92)
    twin.spines["top"].set_visible(False)

    here = s.SPIRAL
    ax.plot([0.2], [here["rotation_degrees"]], "o", color=PRICE, markersize=7,
            zorder=8, markeredgecolor=SURFACE, markeredgewidth=2)
    twin.plot([0.2], [(1 - here["contraction"]) * 100], "o", color=PLAN,
              markersize=7, zorder=8, markeredgecolor=SURFACE, markeredgewidth=2)
    ax.annotate(f"at a step of 0.2 it turns {here['rotation_degrees']:.1f}°\n"
                f"and closes {(1 - here['contraction']) * 100:.1f}% of the gap",
                xy=(0.2, here["rotation_degrees"]), xytext=(0.40, 30),
                fontsize=9.5, color=TEXT_DIM,
                bbox=dict(boxstyle="square,pad=0.4", facecolor=SURFACE,
                          edgecolor=HAIRLINE, linewidth=1.0),
                arrowprops=dict(arrowstyle="-", color=TEXT_FAINT, linewidth=0.9,
                                shrinkA=4, shrinkB=6), zorder=9)
    tag(ax, 0.03, 84, "turning fast", color=PRICE, size=9.5)
    tag(ax, 0.03, 6, "barely shrinking", color=PLAN, size=9.5)
    save(fig, OUT_ANATOMY / "anatomy.png", tight=False)


def restarts_png():
    """The same iteration, with and without averaging away the rotation."""
    fig, ax = figure(8.0, 4.6)
    fig.subplots_adjust(top=0.84, bottom=0.16, left=0.13, right=0.96)
    heading(ax, "distance from the answer, same cost per step")

    steps = 600
    plain = s.distance_curve(pdhg(s.WORKSHOP, steps))
    restarted = s.distance_curve(pdhg(s.WORKSHOP, steps, restart_every=40))
    floor = 1e-16
    ax.semilogy(np.maximum(plain, floor), color=PRICE, linewidth=2.2, zorder=5)
    ax.semilogy(np.maximum(restarted, floor), color=PLAN, linewidth=2.2, zorder=5)

    ax.set_xlabel("iterations", fontsize=10, color=TEXT_DIM, labelpad=6)
    ax.set_ylabel("distance from the answer", fontsize=10, color=TEXT_DIM, labelpad=6)
    ax.set_xlim(0, steps)
    ax.set_ylim(1e-16, 40)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)
    tag(ax, 330, 2.0, "left alone", color=PRICE, size=10)
    tag(ax, 250, 2e-12, "restarted every 40 steps", color=PLAN, size=10)

    gain = plain[-1] / max(restarted[-1], floor)
    ax.text(0.03, 0.06,
            f"after {steps} steps the restarted run is {gain:.0e} times closer,\n"
            "having performed exactly the same matrix products",
            transform=ax.transAxes, fontsize=9.5, color=TEXT_DIM, va="bottom",
            bbox=dict(boxstyle="square,pad=0.4", facecolor=SURFACE,
                      edgecolor="none"), zorder=9)
    save(fig, OUT_RESTART / "restarts.png", tight=False)
    return gain


if __name__ == "__main__":
    anatomy_png()
    print("  restart gain:", f"{restarts_png():.3e}")
