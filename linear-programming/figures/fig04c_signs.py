"""A fair sign makes the first weak-duality step hold for every plan."""

from fractions import Fraction

from matplotlib.patches import Rectangle

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT,
                             TEXT_DIM, WARN, chapter_dir, figure, save)
from linprog import mill as f
from scene import arrow, claim, mark

OUT = chapter_dir("04-buying-the-hours")
WINDOW = (-1.5, 23, -1.5, 18.5)


def priced_products(offer):
    return tuple(
        sum((offer[i] * f.MILL.A[i][j] for i in range(f.MILL.m)), Fraction(0))
        for j in range(f.MILL.n)
    )


def panel_axes(ax):
    ax.set_xlim(WINDOW[0], WINDOW[1])
    ax.set_ylim(WINDOW[2], WINDOW[3])
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks(range(0, 24, 4))
    ax.set_yticks(range(0, 19, 4))
    ax.set_xlabel("3-ply batches t", fontsize=9, color=TEXT_DIM, labelpad=5)
    ax.set_ylabel("5-ply batches f", fontsize=9, color=TEXT_DIM, labelpad=5)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.65, linestyle=(0, (1, 3)), zorder=0)
    ax.set_axisbelow(True)
    ax.axhline(0, color=TEXT, lw=1.15, zorder=2)
    ax.axvline(0, color=TEXT, lw=1.15, zorder=2)


def signs_still():
    fig, placeholder = figure(12.4, 6.8)
    fig.delaxes(placeholder)
    left = fig.add_subplot(1, 2, 1)
    right = fig.add_subplot(1, 2, 2)
    fig.subplots_adjust(left=0.07, right=0.985, top=0.79, bottom=0.18, wspace=0.28)

    fair_offer = (Fraction(3), Fraction(0))
    fair_gap = tuple(value - cost for value, cost
                     in zip(priced_products(fair_offer), f.MILL.c))
    assert fair_gap == (0, 1)
    panel_axes(left)
    left.fill([WINDOW[0], WINDOW[1], WINDOW[1], WINDOW[0]],
              [0, 0, WINDOW[3], WINDOW[3]],
              color=PLAN, alpha=0.08, zorder=1)
    left.add_patch(Rectangle((0, 0), WINDOW[1], WINDOW[3], fill=False,
                             edgecolor=PLAN, linewidth=0.9, linestyle=(0, (3, 3)),
                             alpha=0.6, zorder=3))
    arrow(left, (0, 0), (0, 1), PRICE, lw=2.0)
    left.text(0.8, 1.35, "g = (0, 1)", color=PRICE, fontsize=9,
              ha="left", va="center",
              bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE,
                        edgecolor="none"), zorder=9)
    left.text(1.2, 16.7, "first step holds at every plan", color=PLAN,
              fontsize=8.8, ha="left", va="center",
              bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE,
                        edgecolor="none"), zorder=6)
    claim(left, "fair offer (3, 0)", "g = yA − c = (0, 1); g·x ≥ 0")

    unfair_offer = (Fraction(1), Fraction(2))
    unfair_gap = tuple(value - cost for value, cost
                       in zip(priced_products(unfair_offer), f.MILL.c))
    assert unfair_gap == (0, -1)
    panel_axes(right)
    right.fill([0, WINDOW[1], WINDOW[1], 0],
               [0, 0, WINDOW[3], WINDOW[3]], color=WARN, alpha=0.18, zorder=1)
    arrow(right, (0, 0), (0, -1), PRICE, lw=2.0)
    right.text(0.8, -0.95, "g = (0, −1)", color=PRICE, fontsize=9,
               ha="left", va="center",
               bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE,
                         edgecolor="none"), zorder=9)
    point = (Fraction(0), Fraction(16))
    value = f.MILL.value(point)
    bill = sum((unfair_offer[i] * f.MILL.b[i] for i in range(f.MILL.m)),
               Fraction(0))
    mark(right, point, "(0, 16)", size=9, dx=1.0, dy=0.75)
    right.text(1.0, 15.3, f"earns {value}", color=PLAN, fontsize=8.7,
               ha="left", va="center", zorder=7,
               bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                         edgecolor="none"))
    right.text(1.0, 14.2, f"bill {bill}", color=PRICE, fontsize=8.7,
               ha="left", va="center", zorder=7,
               bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                         edgecolor="none"))
    claim(right, "unfair offer (1, 2)",
          "g = yA − c = (0, −1); every f > 0 violates the sign")
    return save(fig, OUT / "signs.png", tight=False)


if __name__ == "__main__":
    signs_still()
