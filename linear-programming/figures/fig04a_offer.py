"""Fair prices form an unbounded region with a cheapest corner."""

from fractions import Fraction
from itertools import combinations

from illuminate.draw import (HAIRLINE, PRICE, SURFACE, TEXT, TEXT_DIM,
                             WARN, animate, chapter_dir, figure, margin_note)
from linprog import mill as f
from linprog.lp import dual_by_enumeration, solve_square
from scene import Stages, claim, clip, fill

OUT = chapter_dir("04-buying-the-hours")
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
STAGES = Stages((0, 18), (30, 12), (48, 12), (0, 36))
TITLE = "the cheapest fair offer is 2 and 1"
SUBTITLES = (
    "the mill compares the buyer's offer with each product's value",
    "raise the offer until both products are covered",
    "move the bill line down to the cheapest fair corner",
    "",
)
FINAL = f"cheapest fair offer: 2 and 1, a bill of {f.money(BEST_BILL)}"


def _sum_offer(offer, product):
    return sum((offer[i] * MILL.A[i][product] for i in range(MILL.m)),
               Fraction(0))


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
    frames = STAGES.total
    stock = tuple(float(v) for v in MILL.b)
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
            offer = (Fraction(1 + 2 * progress), Fraction(1 - progress))
        elif stage == 2:
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
            if stage != 3:
                ax.text(point[0] + 0.18, point[1] + 0.25, "offer", color=color,
                        fontsize=9, ha="left", va="bottom", zorder=8,
                        bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE,
                                  edgecolor="none"))

        if stage >= 2:
            x0, x1 = MILL.b
            y1 = WINDOW[3]
            start = max(0.0, (bill - float(x1) * y1) / float(x0))
            end = min(float(WINDOW[1]), bill / float(x0))
            if start <= end:
                ax.plot([start, end],
                        [(bill - float(x0) * start) / float(x1),
                         (bill - float(x0) * end) / float(x1)],
                        color=TEXT, lw=1.6, dashes=(5, 3), zorder=5)
            ax.text(4.05, 5.25, "32y₁ + 20y₂ = k", color=TEXT, fontsize=8.8,
                    ha="left", va="center",
                    bbox=dict(boxstyle="square,pad=0.16", facecolor=SURFACE,
                              edgecolor="none"), zorder=7)
            for (exact_point, exact_bill), (point, _) in zip(
                    FAIR_CORNERS, fair_corners):
                if bill > float(exact_bill) and stage == 2:
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
            terms = tuple(_sum_offer(offer, j) for j in range(MILL.n))
            note_lines = [
                f"3-ply's hours: 1+1 = {terms[0]} < {MILL.c[0]}",
                f"5-ply's hours: 2+1 = {terms[1]} < {MILL.c[1]}",
                "mill would rather make plywood",
            ]
        elif stage == 1:
            current = tuple(Fraction(1 + 2 * progress).limit_denominator(10000)
                            if j == 0 else
                            Fraction(1 - progress).limit_denominator(10000)
                            for j in range(MILL.m))
            terms = tuple(_sum_offer(current, j) for j in range(MILL.n))
            note_lines = [
                f"3-ply's hours: {_number(terms[0])} {'≥' if terms[0] >= MILL.c[0] else '<'} {MILL.c[0]}",
                f"5-ply's hours: {_number(terms[1])} {'≥' if terms[1] >= MILL.c[1] else '<'} {MILL.c[1]}",
                f"bill: {_number(sum((current[j] * MILL.b[j] for j in range(MILL.m)), Fraction(0)))}",
            ]
        else:
            note_lines = [
                f"bill = k = {_number(Fraction(bill).limit_denominator(10000))} thousand roubles",
                f"cheapest point: ({BEST_OFFER[0]}, {BEST_OFFER[1]})",
            ]
            if stage == 3:
                note_lines.append(f"bill = {f.money(BEST_BILL)}")

        claim(ax, TITLE, FINAL if i == frames - 1 else SUBTITLES[stage])
        note.set_text("\n".join(note_lines))
        return []

    animate(fig, update, frames, OUT / "offer.gif", fps=12, hold=3.0)


if __name__ == "__main__":
    offer_gif()
