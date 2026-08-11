"""Chapter 9: the two ways a program has no answer, and what the dual says then.

Left: profit that runs away.  The rules leave a direction in which the workshop
can keep building forever, so there is no best plan.  A ceiling would have to
be a number above every plan, and there is no such number -- so the price side
has nothing to offer at all.

Right: an order that cannot be filled.  Twelve tables were promised and the
planks stretch to eleven.  The impossibility has a short proof, and it is worth
seeing that the proof is arithmetic rather than an exhausted search: take a
quarter of the plank rule and all of the order, add them, and the result says a
quantity that cannot be negative is at most minus one.
"""

from fractions import Fraction

from lpduality import workshop as w
from illuminate.draw import (TEXT, TEXT_DIM, TEXT_FAINT, OK, SURFACE, PLAN, PRICE, HAIRLINE,
                            chapter_dir, heading, save, tag)
from lpduality.duality import farkas_certificate, mixture, verify_farkas
from lpduality.lp import solve
from scene import clipped_corners

OUT = chapter_dir("09-when-it-goes-wrong")


def edges_png():
    import matplotlib.pyplot as plt

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10.0, 4.6))
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.14, top=0.86, wspace=0.22)

    # --- left: nothing stops it
    heading(axL, "profit with nothing to stop it")
    corners = clipped_corners(w.ENDLESS, 11.5, 11.0)
    axL.fill([p[0] for p in corners], [p[1] for p in corners],
             color=PLAN, alpha=0.13, zorder=1, linewidth=0)
    axL.plot([p[0] for p in corners] + [corners[0][0]],
             [p[1] for p in corners] + [corners[0][1]],
             color=PLAN, linewidth=1.6, zorder=3)
    xs = [0, 11.5]
    axL.plot(xs, [2 * x - 10 for x in xs], color=TEXT, linewidth=1.3, zorder=2)
    # three lines of equal profit, each labelled, marching out of the picture
    for level, alpha in ((150, 0.42), (300, 0.66), (450, 0.92)):
        axL.plot(xs, [(level - 30 * x) / 20 for x in xs], color=PRICE,
                 linewidth=1.5, alpha=alpha, zorder=4)
        # put the label where this line meets the edge of the panel: near the
        # top if it leaves through the top, otherwise on the left
        top_x = (level - 20 * 10.3) / 30
        if top_x > 0.4:
            lx, ly = top_x, 10.3
        else:
            lx, ly = 0.3, (level - 30 * 0.3) / 20
        axL.text(lx, ly, f"${level}", color=PRICE, fontsize=9,
                 alpha=alpha, ha="center", va="center", zorder=5,
                 bbox=dict(boxstyle="square,pad=0.18", facecolor=SURFACE,
                           edgecolor="none"))
    axL.annotate("", xy=(9.9, 10.4), xytext=(7.2, 6.3),
                 arrowprops=dict(arrowstyle="-|>", color=PRICE, linewidth=1.8))
    axL.text(6.9, 6.0, "and onwards,\nwith no last line", color=PRICE,
             fontsize=9.5, ha="left", va="top", zorder=6,
             bbox=dict(boxstyle="square,pad=0.25", facecolor=SURFACE,
                       edgecolor="none"))
    axL.set_xlim(0, 11.5)
    axL.set_ylim(0, 11.0)
    axL.set_xlabel("tables", fontsize=10, color=TEXT_DIM, labelpad=6)
    axL.set_ylabel("chairs", fontsize=10, color=TEXT_DIM, labelpad=6)
    for s in ("top", "right"):
        axL.spines[s].set_visible(False)
    axL.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    axL.set_axisbelow(True)
    axL.text(6.4, 1.0, "no best plan\n→ no prices at all", color=TEXT_DIM,
             fontsize=10.5, va="bottom")

    # --- right: an order that cannot be met
    heading(axR, "an order the planks cannot reach")
    axR.set_xlim(0, 15)
    axR.set_ylim(0, 1)
    axR.set_yticks([])
    for s in ("top", "right", "left"):
        axR.spines[s].set_visible(False)
    axR.set_xlabel("tables", fontsize=10, color=TEXT_DIM, labelpad=6)
    axR.grid(True, axis="x", color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)))
    axR.set_axisbelow(True)

    axR.axvspan(0, 11, ymin=0.74, ymax=0.90, color=PLAN, alpha=0.22, zorder=2)
    axR.axvspan(12, 15, ymin=0.74, ymax=0.90, color=PRICE, alpha=0.22, zorder=2)
    axR.axvspan(11, 12, ymin=0.72, ymax=0.92, color=TEXT_FAINT, alpha=0.16, zorder=1)
    axR.text(5.5, 0.94, "the planks reach this far", color=PLAN, fontsize=9.5,
             ha="center", va="bottom")
    axR.text(13.5, 0.94, "the order starts here", color=PRICE, fontsize=9.5,
             ha="center", va="bottom")
    axR.annotate("nothing in here", xy=(11.5, 0.72), xytext=(11.5, 0.63),
                 color=TEXT_FAINT, fontsize=9.5, ha="center", va="top",
                 arrowprops=dict(arrowstyle="-", color=TEXT_FAINT, linewidth=0.9))

    # The search in duality.farkas_certificate finds *a* certificate, and for
    # this program it happens to land on the saw rule, which works but is not
    # the one a person would reach for. The plank rule gives the certificate
    # the chapter talks through, so that is the one drawn -- and it is checked
    # here rather than asserted, so the figure cannot show an invalid proof.
    y = (Fraction(1, 4), 0, 0, Fraction(1))
    assert verify_farkas(w.IMPOSSIBLE, y)
    coeffs, total = mixture(w.IMPOSSIBLE, y)
    used = [(w.IMPOSSIBLE.row_names[i], v) for i, v in enumerate(y) if v]
    recipe = "  +  ".join(f"{w.number(v)} × ({name})" for name, v in used)
    proof = (
        "the proof, in one line\n\n"
        f"{recipe}\n"
        f"gives   {w.number(coeffs[1])} × chairs  ≤  {w.number(total)}\n\n"
        "chairs cannot be negative,\n"
        "so there is no such plan"
    )
    axR.text(0.5, 0.46, proof, color=TEXT, fontsize=8.8, va="top", ha="left",
             linespacing=1.3,
             bbox=dict(boxstyle="square,pad=0.55", facecolor=SURFACE,
                       edgecolor=TEXT, linewidth=1.1))
    save(fig, OUT / "edges.png", tight=False)


if __name__ == "__main__":
    edges_png()
