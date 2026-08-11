"""Chapter 7: the relation is satisfied long before either side is right.

Two panels, because there are two separate things to believe.

Left: run one queue and track both averages as they go. They agree with each
other from almost the first customer, and neither is close to the truth for a
very long time. Little's law converging tells you nothing about whether your
measurement has.

Right: what a nominally 95% confident interval actually covers when it assumes
consecutive waits are independent. They are not, and at ninety percent busy
roughly four hundred customers count as one observation.
"""

import numpy as np

from illuminate.draw import (HAIRLINE, OK, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, chapter_dir, figure, heading, save, tag)
from queues import desk as d
from queues.simulate import (batch_interval, correlation_length, lindley,
                             naive_interval, run_queue)

OUT = chapter_dir("07-measuring-is-harder")

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


def measuring_png():
    import matplotlib.pyplot as plt

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10.0, 4.5),
                                   gridspec_kw={"width_ratios": [1.3, 1]})
    fig.subplots_adjust(left=0.09, right=0.97, bottom=0.16, top=0.84, wspace=0.30)

    # --- left: both averages, tracking each other, both wrong
    heading(axL, "both averages, as one run proceeds")
    run = run_queue(rate=9.0, service_rate=10.0, customers=300_000, seed=17,
                    record_every=200)
    running_w = np.cumsum(run.waits) / np.arange(1, len(run.waits) + 1)
    truth = float(d.BUSY.time_in_system) * 60

    # two genuinely separate routes to the same quantity:
    #   ask each customer, and average          -> running_w
    #   count heads over time, divide by rate   -> (area/t) / (departures/t)
    times = np.array([t for t, _, _ in run.trace])
    areas = np.array([a for _, a, _ in run.trace])
    served = np.array([n for _, _, n in run.trace])
    keep = served > 100
    times, areas, served = times[keep], areas[keep], served[keep]
    by_heads = (areas / times) / (served / times)          # L-bar / lambda-hat

    # the broad pale line underneath and the thin one on top of it: they
    # coincide, and drawing them at the same weight would hide that there are
    # two of them at all
    axL.plot(served, by_heads * 60, color=PLAN, linewidth=5.0, alpha=0.45,
             zorder=4, label="counting heads, then dividing by the rate",
             solid_capstyle="round")
    axL.plot(served, running_w[served - 1] * 60, color=PRICE, linewidth=1.5,
             zorder=5, label="asking each customer")
    axL.axhline(truth, color=TEXT_FAINT, linewidth=1.1, linestyle=(0, (4, 4)),
                zorder=3)
    axL.text(2.2e5, truth + 1.6, "the true answer, 60 min", color=TEXT_FAINT,
             fontsize=9, ha="right")
    axL.set_xscale("log")
    axL.set_xlim(200, 3e5)
    axL.set_ylim(38, 76)
    axL.set_xlabel("customers served", fontsize=10, color=TEXT_DIM, labelpad=6)
    axL.set_ylabel("estimate, minutes", fontsize=10, color=TEXT_DIM, labelpad=6)
    for side in ("top", "right"):
        axL.spines[side].set_visible(False)
    axL.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    axL.set_axisbelow(True)
    axL.legend(loc="lower right", fontsize=8.5)
    tag(axL, 900, 74.4,
        "the two ride on top of each other the whole way.\n"
        "neither is close to 60 for a very long time.",
        color=TEXT_DIM, size=9.5)

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
    save(fig, OUT / "measuring.png", tight=False)
    return naive_pct, batch_pct, naive_w, batch_w


if __name__ == "__main__":
    print("  coverage:", measuring_png())
