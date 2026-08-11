"""Chapter 1: why a machine with far more arithmetic cannot use it here."""

import numpy as np

from firstorder import story as s
from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, figure, heading, save, tag)

OUT = chapter_dir("01-wider-not-faster")

# Two illustrative machines. The point is the *shape* of the comparison, not
# these particular products: one has far more arithmetic per byte delivered.
MACHINES = [
    ("a server processor", 256e9, 137.5e9, PRICE),
    ("a data-centre accelerator", 26e12, 2e12, PLAN),
]


def roofline_png():
    fig, ax = figure(8.2, 4.8)
    fig.subplots_adjust(top=0.84, bottom=0.16, left=0.12, right=0.96)
    heading(ax, "what a kernel can reach, against how much it asks for")

    intensity = np.logspace(-2, 2, 400)
    for name, flops, bandwidth, colour in MACHINES:
        reachable = np.minimum(bandwidth * intensity, flops) / 1e12
        ax.loglog(intensity, reachable, color=colour, linewidth=2.3, zorder=5)
        balance = flops / bandwidth
        ax.plot([balance], [flops / 1e12], "o", color=colour, markersize=6,
                zorder=7, markeredgecolor=SURFACE, markeredgewidth=1.8)
        ax.text(balance * 1.35, flops / 1e12 * 0.62, name, color=colour,
                fontsize=9.5, zorder=8)

    here = s.INTENSITY
    ax.axvline(here, color=TEXT, linewidth=1.3, linestyle=(0, (4, 3)), zorder=4)
    ax.text(here * 1.18, 4e-3,
            f"a sparse matrix-vector product\nasks for {here:.2f} operations per byte",
            color=TEXT, fontsize=9.5, zorder=9,
            bbox=dict(boxstyle="square,pad=0.35", facecolor=SURFACE,
                      edgecolor="none"))

    for name, flops, bandwidth, colour in MACHINES:
        reachable = bandwidth * here / 1e12
        ax.plot([here], [reachable], "o", color=colour, markersize=8, zorder=8,
                markeredgecolor=SURFACE, markeredgewidth=2)
        share = s.usable_fraction_for(flops, bandwidth) * 100
        ax.text(here * 0.72, reachable, f"{share:.1f}% of its arithmetic",
                color=colour, fontsize=9, ha="right", va="center", zorder=9)

    ax.set_xlabel("operations the kernel performs per byte it fetches",
                  fontsize=10, color=TEXT_DIM, labelpad=7)
    ax.set_ylabel("achievable rate, teraflop/s", fontsize=10, color=TEXT_DIM, labelpad=7)
    ax.set_xlim(0.01, 100)
    ax.set_ylim(1e-3, 60)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, which="both", color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    ax.set_axisbelow(True)
    save(fig, OUT / "roofline.png", tight=False)


if __name__ == "__main__":
    roofline_png()
