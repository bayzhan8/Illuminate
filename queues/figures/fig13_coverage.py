"""Chapter 13: what a textbook confidence interval actually covers here.

Consecutive waits in a queue are strongly dependent, so the usual interval,
which assumes they are not, is far too narrow. Both numbers on this chart
come out of running the experiment rather than out of a formula.
"""

import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, figure, heading, save, tag)
from queues import desk as d
from queues.simulate import (batch_interval, correlation_length, lindley,
                             naive_interval, run_queue)

OUT = chapter_dir("12-coverage")

TRIALS = 300
RUN_LENGTH = 200_000


def coverage_study():
    """How often each kind of interval actually contains the true answer."""
    truth = float(d.BUSY.time_waiting) * 60
    rng = np.random.default_rng(20)
    naive_hits = batch_hits = 0
    naive_widths, batch_widths = [], []
    for _ in range(TRIALS):
        waits = lindley(9.0, 10.0, RUN_LENGTH, rng) * 60
        half = naive_interval(waits)
        naive_widths.append(half)
        if abs(float(waits.mean()) - truth) <= half:
            naive_hits += 1
        mean, half_b = batch_interval(waits, batches=10)
        batch_widths.append(half_b)
        if abs(mean - truth) <= half_b:
            batch_hits += 1
    return (100 * naive_hits / TRIALS, 100 * batch_hits / TRIALS,
            float(np.mean(naive_widths)), float(np.mean(batch_widths)), truth)


def coverage_png():
    import matplotlib.pyplot as plt

    fig, axR = plt.subplots(1, 1, figsize=(6.8, 4.5))
    fig.subplots_adjust(left=0.15, right=0.96, bottom=0.16, top=0.84)

    # --- right: coverage
    naive_pct, batch_pct, naive_w, batch_w, _ = coverage_study()
    heading(axR, "does a 95% interval contain the answer?")
    bars = axR.bar([0, 1], [naive_pct, batch_pct], width=0.5,
                   color=[PRICE, OK], zorder=4, edgecolor=SURFACE, linewidth=2)
    axR.axhline(95, color=TEXT_FAINT, linewidth=1.1, linestyle=(0, (4, 4)), zorder=3)
    axR.text(-0.5, 97, "95%, as promised", color=TEXT_FAINT, fontsize=9)
    for x, pct, width in ((0, naive_pct, naive_w), (1, batch_pct, batch_w)):
        axR.text(x, pct + 4, f"{pct:.0f}%", ha="center", fontsize=13,
                 color=TEXT, fontweight="semibold", zorder=6)
        # a short bar has no room inside it for the width label
        inside = pct > 25
        axR.text(x, pct / 2 if inside else pct + 13,
                 f"±{width:.2f} min", ha="center", va="center",
                 fontsize=9, color=SURFACE if inside else TEXT_FAINT, zorder=6)
    axR.set_xticks([0, 1])
    axR.set_xticklabels(["assuming the waits\nare independent",
                         "batch means,\nwhich does not"], fontsize=9, color=TEXT_DIM)
    axR.set_ylim(0, 112)
    axR.set_xlim(-0.55, 1.55)
    axR.set_ylabel("runs containing the true answer", fontsize=10,
                   color=TEXT_DIM, labelpad=6)
    for side in ("top", "right"):
        axR.spines[side].set_visible(False)
    axR.grid(True, axis="y", color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    axR.set_axisbelow(True)
    save(fig, OUT / "coverage.png", tight=False)


if __name__ == "__main__":
    coverage_png()
