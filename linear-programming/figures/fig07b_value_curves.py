"""The mill's best value is the lower envelope of fair-offer bills."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT_DIM,
                             chapter_dir, figure, save)
from linprog import mill as f
from linprog.lp import best_by_enumeration, solve_square

if __package__:
    from .scene import claim
else:
    from scene import claim

OUT = chapter_dir("07-one-more")


@dataclass(frozen=True)
class OfferLine:
    offer: tuple[Fraction, ...]
    slope: Fraction
    intercept: Fraction
    formula: str
    anchor: tuple[Fraction, Fraction]

    @property
    def label(self):
        return f"({self.offer[0]}, {self.offer[1]}): {self.formula}"


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


def formula_text(axis, slope, intercept):
    if slope == 0:
        return str(intercept)
    term = "b" if slope == 1 else f"{slope}b"
    if intercept == 0:
        return term
    if axis == 0:
        return f"{term} + {intercept}"
    return f"{intercept} + {term}"


def offer_line_table(axis, maximum, offers):
    lines = []
    for offer in offers:
        slope = Fraction(offer[axis])
        intercept = Fraction(offer[1 - axis] * f.MILL.b[1 - axis])
        anchor_x = Fraction(maximum)
        lines.append(OfferLine(
            offer=tuple(offer),
            slope=slope,
            intercept=intercept,
            formula=formula_text(axis, slope, intercept),
            anchor=(anchor_x, slope * anchor_x + intercept),
        ))
    return tuple(lines)


def envelope_bends(lines, maximum):
    bends = set()
    for first, second in combinations(lines, 2):
        if first.slope == second.slope:
            continue
        stock = (second.intercept - first.intercept) / (
            first.slope - second.slope
        )
        if not 0 <= stock <= maximum:
            continue
        value = first.slope * stock + first.intercept
        if value == min(line.slope * stock + line.intercept
                        for line in lines):
            bends.add((stock, value))
    return tuple(sorted(bends))


LABEL_OFFSETS = {
    0: {
        (3, 0): (-7, 15),
        (2, 1): (-7, -14),
        (0, 5): (-7, -14),
    },
    1: {
        (0, 5): (-7, -14),
        (2, 1): (-7, 18),
        (3, 0): (-7, -18),
    },
}


def panel(ax, axis, maximum, lines, sample):
    values = [
        best_by_enumeration(stock_lp(axis, b))[1]
        for b in range(maximum + 1)
    ]
    x = list(range(maximum + 1))

    ax.set_xlim(0, maximum)
    highest = max([values[-1]] +
                  [line.slope * maximum + line.intercept for line in lines])
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

    for line in lines:
        ax.plot(x, [float(line.slope * b + line.intercept) for b in x],
                color=PRICE, linewidth=1.05, dashes=(4, 3), alpha=0.88,
                zorder=3)
    ax.plot(x, [float(value) for value in values], color=PLAN,
            linewidth=2.8, zorder=4)
    for line in lines:
        ax.plot(x, [float(line.slope * b + line.intercept) for b in x],
                color=PRICE, linewidth=0.9, dashes=(4, 3), alpha=0.78,
                zorder=5)

    for bend, value in envelope_bends(lines, maximum):
        ax.plot([float(bend)], [float(value)], "o", color=PLAN,
                markeredgecolor=SURFACE, markeredgewidth=1.0,
                markersize=5.0, zorder=7)

    b, value = sample
    ax.plot([float(b)], [float(value)], "o", color=PLAN,
            markeredgecolor=SURFACE, markeredgewidth=1.6,
            markersize=7.5, zorder=8)
    ax.text(float(b) - (2.0 if axis == 0 else 1.5), float(value) - 7,
            f"({b}, {value})", color=PLAN, fontsize=8.0,
            ha="right", va="top", zorder=9,
            bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE,
                      edgecolor="none"))

    for line in lines:
        ax.annotate(
            line.label,
            xy=tuple(float(value) for value in line.anchor),
            xytext=LABEL_OFFSETS[axis][line.offer],
            textcoords="offset points",
            color=PRICE,
            fontsize=7.2,
            ha="right",
            va="center",
            bbox=dict(boxstyle="round,pad=0.2", facecolor=SURFACE,
                      edgecolor=PRICE, linewidth=0.6),
            arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.65,
                            shrinkA=2, shrinkB=1),
            annotation_clip=False,
            zorder=10,
        )


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
    panel(left, 0, 50, offer_line_table(0, 50, offers), left_sample)
    panel(right, 1, 40, offer_line_table(1, 40, offers), right_sample)
    return save(fig, OUT / "value_curves.png", tight=False)


if __name__ == "__main__":
    value_curves()
