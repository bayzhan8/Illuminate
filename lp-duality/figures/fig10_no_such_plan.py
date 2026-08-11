"""Chapter 10: an order the planks cannot reach, and the one-line proof.

A quarter of the plank rule plus the order gives half the chairs at most -1,
and counts do not go below zero. That settles it for every plan at once.
"""

from fractions import Fraction

from lpduality import workshop as w
from illuminate.draw import (TEXT, TEXT_DIM, TEXT_FAINT, OK, SURFACE, PLAN, PRICE, HAIRLINE,
                            chapter_dir, heading, save, tag)
from lpduality.duality import farkas_certificate, mixture, verify_farkas
from lpduality.lp import solve
from scene import clipped_corners

OUT = chapter_dir("10-no-such-plan")


def no_such_plan_png():
    import matplotlib.pyplot as plt

    fig, axR = plt.subplots(1, 1, figsize=(6.4, 4.6))
    fig.subplots_adjust(left=0.07, right=0.96, bottom=0.13, top=0.86)

    # --- right: an order that cannot be met
    heading(axR, "an order the planks cannot reach")
    axR.set_xlim(0, 15)
    axR.set_ylim(-0.30, 1)
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
    axR.text(0.5, 0.52, proof, color=TEXT, fontsize=8.8, va="top", ha="left",
             linespacing=1.3,
             bbox=dict(boxstyle="square,pad=0.55", facecolor=SURFACE,
                       edgecolor=TEXT, linewidth=1.1))
    save(fig, OUT / "no-such-plan.png", tight=False)


if __name__ == "__main__":
    no_such_plan_png()
