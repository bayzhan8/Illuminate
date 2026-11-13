"""The mill's best value is the lower envelope of fair-offer bills."""

from fractions import Fraction
from itertools import combinations

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT_DIM,
                             chapter_dir, figure, save)
from linprog import mill as f
from linprog.lp import best_by_enumeration, solve_square
from scene import claim

OUT = chapter_dir("07-one-more")


def fair_offer_corners():
    boundaries = [
        (tuple(f.MILL.A[i][j] for i in range(f.MILL.m)), f.MILL.c[j])
        for j in range(f.MILL.n)
    ]
    boundaries.extend(
        (tuple(Fraction(int(i == j)) for i in range(f.MILL.m)), Fraction(0))
        for j in range(f.MILL.m)
    )
    found = set()
    for first, second in combinations(boundaries, f.MILL.m):
        offer = solve_square((first[0], second[0]), (first[1], second[1]))
        if offer is None or any(price < 0 for price in offer):
            continue
        if any(sum((offer[i] * f.MILL.A[i][j] for i in range(f.MILL.m)),
                   Fraction(0)) < f.MILL.c[j]
               for j in range(f.MILL.n)):
            continue
        found.add(offer)
    return tuple(sorted(found))


def stock_lp(axis, b):
    stock = list(f.MILL.b)
    stock[axis] = Fraction(b)
    return f.MILL.with_b(stock)


def bill(offer, stock):
    return sum((offer[i] * stock[i] for i in range(f.MILL.m)), Fraction(0))


def panel(ax, axis, maximum, offers, sample):
    values = [
        best_by_enumeration(stock_lp(axis, b))[1]
        for b in range(maximum + 1)
    ]
    stocks = [list(f.MILL.b) for _ in range(maximum + 1)]
    for b, stock in enumerate(stocks):
        stock[axis] = Fraction(b)
    x = list(range(maximum + 1))

    ax.set_xlim(0, maximum)
    highest = max([values[-1]] + [bill(offer, stocks[-1]) for offer in offers])
    ax.set_ylim(0, float(highest) * 1.12)
    ax.set_xticks(range(0, maximum + 1, 10))
    ax.set_xlabel("lathe hours b" if axis == 0 else "press hours b",
                  fontsize=9.5, color=TEXT_DIM, labelpad=6)
    ax.set_ylabel("thousand roubles", fontsize=9.5, color=TEXT_DIM,
                  labelpad=6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.65,
            linestyle=(0, (1, 3)), zorder=0)
    ax.set_axisbelow(True)

    for offer in offers:
        ax.plot(x, [float(bill(offer, stock)) for stock in stocks],
                color=PRICE, linewidth=1.05, dashes=(4, 3), alpha=0.88,
                zorder=3)
    ax.plot(x, [float(value) for value in values], color=PLAN,
            linewidth=2.8, zorder=4)
    for offer in offers:
        ax.plot(x, [float(bill(offer, stock)) for stock in stocks],
                color=PRICE, linewidth=0.9, dashes=(4, 3), alpha=0.78,
                zorder=5)

    b, value = sample
    ax.plot([float(b)], [float(value)], "o", color=PLAN,
            markeredgecolor=SURFACE, markeredgewidth=1.6,
            markersize=7.5, zorder=8)
    ax.text(float(b) - (2.0 if axis == 0 else 1.5), float(value) - 7,
            f"({b}, {value})", color=PLAN, fontsize=8.0,
            ha="right", va="top", zorder=9,
            bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE,
                      edgecolor="none"))

    if axis == 0:
        offer_labels = ((offers[2], 36, 110), (offers[1], 18, 58),
                        (offers[0], 45, 104))
    else:
        offer_labels = ((offers[0], 34, 176), (offers[1], 23, 90),
                        (offers[2], 34, 100))
    for offer, label_x, label_y in offer_labels:
        ax.text(label_x, label_y, f"offer ({offer[0]}, {offer[1]})",
                color=PRICE, fontsize=7.6, ha="center", va="bottom",
                zorder=10,
                bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                          edgecolor="none"))


def value_curves():
    offers = fair_offer_corners()
    fig, title_ax = figure(12.2, 6.5)
    title_ax.set_axis_off()
    title_ax.set_position([0.07, 0.23, 0.88, 0.56])
    left = fig.add_axes([0.09, 0.21, 0.38, 0.55])
    right = fig.add_axes([0.55, 0.21, 0.38, 0.55])
    fig.subplots_adjust(left=0.07, right=0.97, top=0.8, bottom=0.19)
    claim(title_ax, "the best value is the lowest fair bill",
          "the blue curve follows the cheapest rust offer at every stock")

    left_sample = (Fraction(32), best_by_enumeration(stock_lp(0, 32))[1])
    right_sample = (Fraction(20), best_by_enumeration(stock_lp(1, 20))[1])
    panel(left, 0, 50, offers, left_sample)
    panel(right, 1, 40, offers, right_sample)
    return save(fig, OUT / "value_curves.png", tight=False)


if __name__ == "__main__":
    value_curves()
