"""Fair prices form an unbounded region with a cheapest corner."""

from fractions import Fraction
from itertools import combinations

from illuminate.draw import (HAIRLINE, PRICE, SURFACE, TEXT, TEXT_DIM,
                             WARN, animate, chapter_dir, figure, margin_note)
from linprog import mill as f
from linprog.lp import dual_by_enumeration, solve_square
from scene import Stages, claim, clip, fill

OUT = chapter_dir("06-buying-the-hours")
MILL = f.MILL
WINDOW = (0, 6, 0, 6)
PRICE_ROWS = tuple(
    tuple(MILL.A[i][j] for i in range(MILL.m))
    for j in range(MILL.n)
)


def fair_offer_corners():
    boundaries = list(zip(PRICE_ROWS, MILL.c))
    boundaries.extend(
        (tuple(Fraction(int(i == j)) for i in range(MILL.m)), Fraction(0))
        for j in range(MILL.m)
    )
    found = {}
    for first, second in combinations(boundaries, MILL.m):
        offer = solve_square((first[0], second[0]), (first[1], second[1]))
        if offer is None or any(price < 0 for price in offer):
            continue
        if any(sum((offer[i] * MILL.A[i][j] for i in range(MILL.m)),
                   Fraction(0)) < MILL.c[j]
               for j in range(MILL.n)):
            continue
        bill = sum((offer[i] * MILL.b[i] for i in range(MILL.m)),
                   Fraction(0))
        found[offer] = bill
    return tuple(sorted(found.items(), key=lambda item: (item[1], item[0])))


FAIR_CORNERS = fair_offer_corners()
BEST_OFFER, BEST_BILL = dual_by_enumeration(MILL)
INITIAL_BILL = max(bill for _, bill in FAIR_CORNERS) + MILL.b[1]
STAGES = Stages((0, 18), (30, 0), (0, 24), (48, 12), (0, 36))
TITLE = "the cheapest fair offer is 2 and 1"
SUBTITLES = (
    "the mill compares the buyer's offer with each product's value",
    "raise the offer until both products are covered",
    "a fair offer: both products covered",
    "move the bill line down to the cheapest fair corner",
    "",
)
FINAL = f"cheapest fair offer: 2 and 1, a bill of {f.money(BEST_BILL)}"


def _sum_offer(offer, product):
    return sum((offer[i] * MILL.A[i][product] for i in range(MILL.m)),
               Fraction(0))


def _offer_terms(offer, product):
    return tuple(offer[i] * MILL.A[i][product] for i in range(MILL.m))


def _number(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{float(value):.1f}"


def _draw_axes(ax):
    ax.set_xlim(WINDOW[0], WINDOW[1])
    ax.set_ylim(WINDOW[2], WINDOW[3])
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks(range(0, 7))
    ax.set_yticks(range(0, 7))
    ax.set_xlabel("lathe price y₁ (thousands of roubles)",
                  fontsize=9.5, color=TEXT_DIM, labelpad=7)
    ax.set_ylabel("press price y₂ (thousands of roubles)",
                  fontsize=9.5, color=TEXT_DIM, labelpad=7)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, color=HAIRLINE, linewidth=0.7, linestyle=(0, (1, 3)), zorder=0)
    ax.set_axisbelow(True)


def _fair_region(ax):
    polygon = [(WINDOW[0], WINDOW[2]), (WINDOW[1], WINDOW[2]),
               (WINDOW[1], WINDOW[3]), (WINDOW[0], WINDOW[3])]
    for coefficients, bound in zip(PRICE_ROWS, MILL.c):
        polygon = clip(polygon, coefficients, bound, keep_le=False)
    fill(ax, polygon, PRICE, 0.14, z=1)


def _product_walls(ax):
    for j, label in enumerate(("3-ply", "5-ply")):
        row = PRICE_ROWS[j]
        rhs = MILL.c[j]
        x = (WINDOW[0], WINDOW[1])
        y = tuple(float(rhs - row[0] * value) / float(row[1]) for value in x)
        ax.plot(x, y, color=PRICE, lw=1.8, zorder=3)
        label_x = 0.35 if j == 0 else 0.55
        label_y = float(rhs - row[0] * label_x) / float(row[1])
        ax.text(label_x + 0.08, label_y + 0.18, label, color=PRICE, fontsize=9,
                ha="left", va="bottom", zorder=6,
                bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                          edgecolor="none"))


def offer_gif():
    fig, ax = figure(7.5, 7.0)
    fig.subplots_adjust(left=0.13, right=0.97, top=0.84, bottom=0.2)
    note = margin_note(fig, y=0.025, size=9.0)
    note.set_linespacing(1.35)
    frames = STAGES.total
    fair_corners = tuple((tuple(float(v) for v in point), bill)
                         for point, bill in FAIR_CORNERS)

    def update(i):
        i = min(i, frames - 1)
        stage, progress = STAGES(i)
        if i == frames - 1:
            progress = 1.0
        ax.clear()
        _draw_axes(ax)
        _fair_region(ax)
        _product_walls(ax)

        offer = None
        bill = None
        if stage == 0:
            offer = (Fraction(1), Fraction(1))
        elif stage == 1:
            progress = min(progress, 0.9)
            offer = (Fraction(1 + 2 * progress).limit_denominator(10000),
                     Fraction(1 - progress).limit_denominator(10000))
        elif stage == 2:
            offer = (Fraction(3), Fraction(0))
        elif stage == 3:
            bill = float(INITIAL_BILL) + progress * (
                float(BEST_BILL) - float(INITIAL_BILL)
            )
        else:
            offer = BEST_OFFER
            bill = float(BEST_BILL)

        if offer is not None:
            point = tuple(float(value) for value in offer)
            fair = all(_sum_offer(offer, j) >= MILL.c[j] for j in range(MILL.n))
            color = PRICE if fair else WARN
            ax.plot([point[0]], [point[1]], "o", color=color, markersize=9,
                    markeredgecolor=SURFACE, markeredgewidth=2.0, zorder=8)
            if stage != 4:
                ax.text(point[0] + 0.18, point[1] + 0.25,
                        "fair offer" if fair else "unfair", color=color,
                        fontsize=9, ha="left", va="bottom", zorder=8,
                        bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE,
                                  edgecolor="none"))

        if stage >= 3:
            x0, x1 = MILL.b
            y1 = WINDOW[3]
            start = max(0.0, (bill - float(x1) * y1) / float(x0))
            end = min(float(WINDOW[1]), bill / float(x0))
            if start <= end:
                ax.plot([start, end],
                        [(bill - float(x0) * start) / float(x1),
                         (bill - float(x0) * end) / float(x1)],
                        color=TEXT, lw=1.6, dashes=(5, 3), zorder=5)
            line_label_x = min(end - 0.2, max(start + 0.2, (start + end) / 2))
            line_label_y = (bill - float(x0) * line_label_x) / float(x1)
            ax.text(line_label_x + 0.12, line_label_y - 0.22,
                    f"{MILL.b[0]}y₁ + {MILL.b[1]}y₂ = k",
                    color=TEXT, fontsize=8.3, ha="left", va="top",
                    bbox=dict(boxstyle="square,pad=0.16", facecolor=SURFACE,
                              edgecolor="none"), zorder=7)
            for (exact_point, exact_bill), (point, _) in zip(
                    FAIR_CORNERS, fair_corners):
                if bill > float(exact_bill) and stage == 3:
                    continue
                ax.plot([point[0]], [point[1]], "o", color=PRICE, markersize=5.5,
                        markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=7)
                if exact_point == (Fraction(0), Fraction(5)):
                    offset = (0.32, 0.16)
                elif exact_point == (Fraction(3), Fraction(0)):
                    offset = (0.18, 0.4)
                else:
                    offset = (0.2, 0.18)
                ax.text(point[0] + offset[0], point[1] + offset[1],
                        f"({exact_point[0]}, {exact_point[1]}): {exact_bill}",
                        color=PRICE, fontsize=8.1, ha="left", va="bottom",
                        bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                                  edgecolor="none"), zorder=8)

        if stage == 0:
            offer = (Fraction(1), Fraction(1))
            note_lines = []
            for j, product in enumerate(MILL.var_names):
                terms = _offer_terms(offer, j)
                value = sum(terms, Fraction(0))
                note_lines.append(
                    f"{product}'s hours: {' + '.join(map(_number, terms))} = "
                    f"{_number(value)} < {MILL.c[j]}"
                )
            note_lines.append("mill would rather make plywood")
        elif stage == 1:
            note_lines = []
            for j, product in enumerate(MILL.var_names):
                terms = _offer_terms(offer, j)
                value = sum(terms, Fraction(0))
                sign = "≥" if value >= MILL.c[j] else "<"
                note_lines.append(
                    f"{product}'s hours: {' + '.join(map(_number, terms))} = "
                    f"{_number(value)} {sign} {MILL.c[j]}"
                )
            bill_terms = tuple(MILL.b[i] * offer[i] for i in range(MILL.m))
            bill_value = sum(bill_terms, Fraction(0))
            bill_expression = " + ".join(
                f"{MILL.b[i]}×{_number(offer[i])}" for i in range(MILL.m)
            )
            note_lines.append(f"bill: {bill_expression} = {_number(bill_value)}")
        elif stage == 2:
            note_lines = []
            for j, product in enumerate(MILL.var_names):
                terms = _offer_terms(offer, j)
                value = sum(terms, Fraction(0))
                note_lines.append(
                    f"{product}'s hours: {' + '.join(map(_number, terms))} = "
                    f"{_number(value)} ≥ {MILL.c[j]}"
                )
            bill_terms = tuple(MILL.b[i] * offer[i] for i in range(MILL.m))
            bill_value = sum(bill_terms, Fraction(0))
            bill_expression = " + ".join(
                f"{MILL.b[i]}×{_number(offer[i])}" for i in range(MILL.m)
            )
            note_lines.append(f"bill: {bill_expression} = {_number(bill_value)}")
        elif stage == 3:
            note_lines = [
                f"bill k = {_number(Fraction(bill).limit_denominator(10000))}"
            ]
        else:
            product_checks = []
            for j, product in enumerate(MILL.var_names):
                terms = _offer_terms(BEST_OFFER, j)
                value = sum(terms, Fraction(0))
                product_checks.append(
                    f"{product}: {' + '.join(map(_number, terms))} = "
                    f"{_number(value)} = {MILL.c[j]}"
                )
            note_lines = [
                f"bill k = {_number(BEST_BILL)}",
                " · ".join(product_checks) + " (both priced exactly at value)",
            ]

        claim(ax, TITLE, FINAL if i == frames - 1 else SUBTITLES[stage])
        note.set_text("\n".join(note_lines))
        return []

    animate(fig, update, frames, OUT / "offer.gif", fps=12, hold=3.0,
            preserve_colors=(PRICE, WARN))


if __name__ == "__main__":
    offer_gif()
