"""Corner-plan values lie below all fair-offer bills."""

from fractions import Fraction
from itertools import combinations

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             chapter_dir, figure, save)
from linprog import mill as f
from linprog.lp import solve_square
from scene import claim

OUT = chapter_dir("04-buying-the-hours")


def fair_offer_corners():
    boundaries = [
        (tuple(f.MILL.A[i][j] for i in range(f.MILL.m)), f.MILL.c[j])
        for j in range(f.MILL.n)
    ]
    boundaries.extend(
        (tuple(Fraction(int(i == j)) for i in range(f.MILL.m)), Fraction(0))
        for j in range(f.MILL.m)
    )
    found = {}
    for first, second in combinations(boundaries, f.MILL.m):
        offer = solve_square((first[0], second[0]), (first[1], second[1]))
        if offer is None or any(price < 0 for price in offer):
            continue
        if any(sum((offer[i] * f.MILL.A[i][j] for i in range(f.MILL.m)),
                   Fraction(0)) < f.MILL.c[j]
               for j in range(f.MILL.n)):
            continue
        bill = sum((offer[i] * f.MILL.b[i] for i in range(f.MILL.m)),
                   Fraction(0))
        found[offer] = bill
    return tuple(sorted(found.items(), key=lambda item: (item[1], item[0])))


def sandwich_still():
    fig, ax = figure(12.4, 6.1)
    fig.subplots_adjust(left=0.055, right=0.99, top=0.77, bottom=0.17)
    ax.set_xlim(-5, 110)
    ax.set_ylim(-2.6, 2.6)
    ax.set_yticks([])
    ax.set_xticks(range(0, 111, 10))
    ax.set_xlabel("thousands of roubles", fontsize=10, color=TEXT_DIM, labelpad=8)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.grid(axis="x", color=HAIRLINE, linewidth=0.65,
            linestyle=(0, (1, 3)), zorder=0)
    ax.set_axisbelow(True)
    ax.axhline(0, color=TEXT, lw=1.25, zorder=2)

    plans = sorted(((f.MILL.value(point), point) for point in f.CORNERS),
                   key=lambda item: item[0])
    offers = list(fair_offer_corners())
    extra = (Fraction(2), Fraction(2))
    assert all(sum((extra[i] * f.MILL.A[i][j] for i in range(f.MILL.m)),
                   Fraction(0)) >= f.MILL.c[j]
               for j in range(f.MILL.n))
    extra_bill = sum((extra[i] * f.MILL.b[i] for i in range(f.MILL.m)),
                     Fraction(0))
    offers.append((extra, extra_bill))
    offers.sort(key=lambda item: item[1])

    plan_rows = (("0", -0.72), ("1", -0.72), ("2", -1.25), ("3", -1.8))
    for (value, point), (_, label_y) in zip(plans, plan_rows):
        x = float(value)
        ax.vlines(x, -0.08, -0.33, color=PLAN, lw=1.6, zorder=3)
        ax.plot([x], [-0.33], "o", color=PLAN, markersize=6.5, zorder=4)
        label = f"{value}: ({point[0]}, {point[1]})"
        ax.plot([x, x], [-0.38, label_y + 0.08], color=PLAN, lw=0.8, alpha=0.65,
                zorder=2)
        ax.text(x, label_y, label, color=PLAN, fontsize=8.5, ha="center",
                va="top", zorder=5,
                bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                          edgecolor="none"))

    offer_levels = (0.72, 1.22, 1.72, 2.22)
    for (offer, bill), label_y in zip(offers, offer_levels):
        x = float(bill)
        ax.vlines(x, 0.08, 0.33, color=PRICE, lw=1.6, zorder=3)
        ax.plot([x], [0.33], "o", color=PRICE, markersize=6.5, zorder=4)
        ax.plot([x, x], [0.38, label_y - 0.08], color=PRICE, lw=0.8, alpha=0.65,
                zorder=2)
        ax.text(x, label_y, f"{bill}: offer ({offer[0]}, {offer[1]})",
                color=PRICE, fontsize=8.5, ha="center", va="bottom", zorder=5,
                bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                          edgecolor="none"))

    best = f.BEST_VALUE
    ax.axvline(float(best), ymin=0.36, ymax=0.64, color=TEXT_DIM,
               lw=1.1, dashes=(3, 2), zorder=1)
    claim(ax, "every corner plan value is at most every fair bill",
          "plans below in blue · fair offers above in rust · thousands of roubles")
    return save(fig, OUT / "sandwich.png", tight=False)


if __name__ == "__main__":
    sandwich_still()
