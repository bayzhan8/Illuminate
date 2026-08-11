"""Chapter 3: build a ceiling by charging for the ingredients.

The animation runs the argument in two movements, because it is two ideas.

First: raise the plank price alone.  The bars show what the mix charges for one
table and for one chair, and each bar has to reach its own line -- the profit
that product earns -- before the mix says anything at all.  Tables are covered
long before chairs are, and while either bar is short the ceiling is worthless,
which is the thing a reader has to see rather than be told.

Second: with both covered, trade plank price for hour price.  Validity holds the
whole way and the ceiling falls.  Chapter 4 asks how far it can fall.
"""

from lpduality import workshop as w
from lpduality.draw import (INK, INK2, MUTED, OK, PAPER, PLAN, PRICE, RULE,
                            animate, chapter_dir, heading, readout)
from lpduality.duality import ceiling_from, mixture

OUT = chapter_dir("03-mixing-the-rules")

PRODUCTS = ("one table", "one chair")


def path(t: float) -> tuple[float, float, float]:
    """Plank price, hour price, saw price, as one number walks the story."""
    if t <= 0.5:                       # movement one: planks alone, 0 -> 10
        return (20 * t, 0.0, 0.0)
    u = (t - 0.5) / 0.5                # movement two: 10 -> 6.25 and 0 -> 2.5
    return (10 - 3.75 * u, 2.5 * u, 0.0)


def mixing_gif(frames=76, fps=13):
    import matplotlib.pyplot as plt

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.4, 4.5),
                                   gridspec_kw={"width_ratios": [1.05, 1]})
    fig.subplots_adjust(bottom=0.27, wspace=0.32)

    # --- left: does the mix charge enough for each product?
    axL.set_xlim(-0.6, 1.6)
    axL.set_ylim(0, 46)
    for s in ("top", "right"):
        axL.spines[s].set_visible(False)
    axL.set_xticks([0, 1])
    axL.set_xticklabels(PRODUCTS, fontsize=10, color=INK2)
    axL.set_ylabel("dollars", fontsize=10, color=INK2, labelpad=7)
    axL.grid(True, axis="y", color=RULE, linewidth=0.7, linestyle=(0, (1, 3)))
    axL.set_axisbelow(True)
    heading(axL, "what the mix charges")

    bars = axL.bar([0, 1], [0, 0], width=0.46, color=PRICE, zorder=4,
                   edgecolor=PAPER, linewidth=2)
    for k, profit in enumerate((30, 20)):
        axL.plot([k - 0.34, k + 0.34], [profit, profit], color=PLAN,
                 linewidth=2.4, zorder=6, solid_capstyle="butt")
        axL.text(k, profit + 1.4, f"earns ${profit}", color=PLAN, fontsize=9.5,
                 va="bottom", ha="center", zorder=6)
    marks = [axL.text(k + 0.30, 0, "", ha="left", va="center", fontsize=14,
                      fontweight="semibold", zorder=7) for k in (0, 1)]

    # --- right: the ceiling this mix proves
    axR.set_xlim(0, 1)
    axR.set_ylim(300, 1000)
    for s in ("top", "right", "bottom"):
        axR.spines[s].set_visible(False)
    axR.set_xticks([])
    axR.set_ylabel("dollars", fontsize=10, color=INK2, labelpad=7)
    axR.grid(True, axis="y", color=RULE, linewidth=0.7, linestyle=(0, (1, 3)))
    axR.set_axisbelow(True)
    heading(axR, "the ceiling it proves")

    ceiling_line, = axR.plot([], [], color=PRICE, linewidth=2.6, zorder=5)
    trail, = axR.plot([], [], color=PRICE, linewidth=1.0, alpha=0.35, zorder=3)
    axR.axhline(float(w.BEST_PROFIT), color=MUTED, linewidth=1.0,
                linestyle=(0, (4, 4)), zorder=2)
    axR.text(0.98, float(w.BEST_PROFIT) - 22, "$350", color=MUTED, fontsize=9.5,
             ha="right", va="top")

    waiting = axR.text(0.5, 640, "no ceiling yet", color=MUTED, fontsize=10.5,
                       ha="center", va="center", zorder=4)
    note = readout(fig, x=0.045, size=10.5)
    history_x, history_y = [], []

    def update(i):
        i = min(i, frames - 1)
        t = i / (frames - 1)
        y = path(t)
        charged, total = mixture(w.PRIMAL, y)
        charged = [float(v) for v in charged]
        valid = ceiling_from(w.PRIMAL, y) is not None

        for bar, v in zip(bars, charged):
            bar.set_height(v)
        for k, (mark, v, earns) in enumerate(zip(marks, charged, (30, 20))):
            covered = v >= earns
            mark.set_text("✓" if covered else "×")
            mark.set_color(OK if covered else PRICE)
            mark.set_position((k + 0.30, v))

        if valid:
            history_x.append(t)
            history_y.append(float(total))
            trail.set_data(history_x, history_y)
            ceiling_line.set_data([0, 1], [float(total)] * 2)
            note.set_text(f"planks ${y[0]:.2f}   hours ${y[1]:.2f}   "
                          f"saw ${y[2]:.2f}\nboth products covered — "
                          f"so nothing can beat ${float(total):,.2f}")
            note.set_color(INK)
            waiting.set_text("")
        else:
            ceiling_line.set_data([], [])
            waiting.set_text("no ceiling yet")
            short = [p for p, v, e in zip(PRODUCTS, charged, (30, 20)) if v < e]
            note.set_text(f"planks ${y[0]:.2f}   hours ${y[1]:.2f}   "
                          f"saw ${y[2]:.2f}\n{' and '.join(short)} "
                          "underpriced — this mix proves nothing")
            note.set_color(PRICE)
        return []

    animate(fig, update, frames, OUT / "mixing.gif", fps=fps, hold=3.0)


if __name__ == "__main__":
    mixing_gif()
