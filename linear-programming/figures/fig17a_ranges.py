"""Animate the stock and value ranges in the mill's final dictionary."""

from fractions import Fraction as Q

from matplotlib.patches import Polygon

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             WARN, animate, chapter_dir, figure, style)
from linprog.sensitivity import (
    basis_inverse, cost_range, rhs_range,
)
from linprog.simplex import dictionary

OUT = chapter_dir("17-sensitivity")
MILL_A = (
    (Q(1), Q(2), Q(1), Q(0)),
    (Q(1), Q(1), Q(0), Q(1)),
)
MILL_B = (Q(32), Q(20))
MILL_C = (Q(3), Q(5), Q(0), Q(0))
BASIS = (0, 1)
STATE = dictionary(MILL_A, MILL_B, MILL_C, BASIS)
INVERSE = basis_inverse(MILL_A, MILL_B, MILL_C, BASIS)
LATHE_RANGE = rhs_range(MILL_A, MILL_B, MILL_C, BASIS, 0)
PRESS_RANGE = rhs_range(MILL_A, MILL_B, MILL_C, BASIS, 1)
THREE_PLY_RANGE = cost_range(MILL_A, MILL_B, MILL_C, BASIS, 0)
FIVE_PLY_RANGE = cost_range(MILL_A, MILL_B, MILL_C, BASIS, 1)
BASE_PLAN = STATE.x_B
BASE_VALUE = sum((MILL_C[index] * BASE_PLAN[row]
                  for row, index in enumerate(BASIS)), Q(0))
STOCK_START = (LATHE_RANGE[0], MILL_B[1])
STOCK_FINAL = (LATHE_RANGE[1], MILL_B[1])
STOCK_REFERENCE = MILL_B
PRICE_START = (THREE_PLY_RANGE[0], MILL_C[1])
PRICE_FINAL = (THREE_PLY_RANGE[1], MILL_C[1])
PRICE_REFERENCE = (MILL_C[0], MILL_C[1])
STOCK_TIE_ANCHORS = (STOCK_START, STOCK_FINAL)
PRICE_TIE_ANCHORS = (PRICE_START, PRICE_FINAL)
STOCK_RAYS = (
    tuple(MILL_A[row][0] for row in range(2)),
    tuple(MILL_A[row][1] for row in range(2)),
)
VALUE_RAYS = (
    tuple(MILL_A[0][index] for index in range(2)),
    tuple(MILL_A[1][index] for index in range(2)),
)
TITLE = "The last dictionary contains the ranges"
SUBTITLES = (
    "at both lower limits, the 3-ply ray and lathe wall tie",
    "move the stock and value data while the same basis stays optimal",
    "at both upper limits, the 5-ply ray and press wall tie",
)
START_HOLD = 18
MOVE_FRAMES = 21
FINAL_HOLD = 24
TOTAL_FRAMES = START_HOLD + MOVE_FRAMES + FINAL_HOLD
HOLD_INDICES = (START_HOLD - 1, TOTAL_FRAMES - 1)
STOCK_POINT_ANCHOR = STOCK_START
PRICE_POINT_ANCHOR = PRICE_START
STOCK_BASE_ANCHOR = STOCK_REFERENCE
PRICE_BASE_ANCHOR = PRICE_REFERENCE


def fraction_text(value):
    value = Q(value)
    sign = "−" if value < 0 else ""
    numerator = abs(value.numerator)
    if value.denominator == 1:
        return f"{sign}{numerator}"
    return f"{sign}{numerator}/{value.denominator}"


def _dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Q(0))


def _matvec(matrix, vector):
    return tuple(_dot(row, vector) for row in matrix)


def _format_pair(values):
    return f"({fraction_text(values[0])}, {fraction_text(values[1])})"


def plan_at_stock(stock):
    return _matvec(INVERSE, stock)


def value_at_stock(stock):
    return _dot(MILL_C[:2], plan_at_stock(stock))


def objective_at(progress):
    return (
        THREE_PLY_RANGE[0]
        + Q(progress) * (THREE_PLY_RANGE[1] - THREE_PLY_RANGE[0]),
        MILL_C[1],
    )


def stock_at(progress):
    return (
        LATHE_RANGE[0] + Q(progress) * (LATHE_RANGE[1] - LATHE_RANGE[0]),
        MILL_B[1],
    )


def prices_at(objective):
    return tuple(
        sum((objective[row] * INVERSE[row][column]
             for row in range(len(BASIS))), Q(0))
        for column in range(len(BASIS))
    )


def frame_state(index):
    index = max(0, min(index, TOTAL_FRAMES - 1))
    if index < START_HOLD:
        return 0, Q(0)
    index -= START_HOLD
    if index < MOVE_FRAMES:
        return 1, Q(index, max(1, MOVE_FRAMES - 1))
    return 2, Q(1)


def subtitle_for_frame(index):
    return SUBTITLES[frame_state(index)[0]]


def _affine_text(base, slope):
    if slope == 0:
        return fraction_text(base)
    sign = " + " if slope > 0 else " − "
    coefficient = ("" if abs(slope) == 1
                   else f"{fraction_text(abs(slope))}")
    return f"{fraction_text(base)}{sign}{coefficient}δ"


def stock_formula_text():
    slopes = tuple(INVERSE[row][0] for row in range(2))
    plan_terms = tuple(
        _affine_text(BASE_PLAN[row], slopes[row])
        for row in range(2)
    )
    value_slope = _dot(MILL_C[:2], slopes)
    return (
        f"δ = b₁ − {fraction_text(MILL_B[0])}: "
        f"plan = ({plan_terms[0]}, {plan_terms[1]}), "
        f"value = {_affine_text(BASE_VALUE, value_slope)}"
    )


def price_formula_text():
    slopes = tuple(INVERSE[0][column] for column in range(2))
    prices = prices_at(PRICE_REFERENCE)
    price_terms = tuple(
        _affine_text(prices[column], slopes[column])
        for column in range(2)
    )
    return (
        f"δ = c₁ − {fraction_text(MILL_C[0])}: "
        f"y = ({price_terms[0]}, {price_terms[1]})"
    )


def ranges_gif():
    fig, empty_ax = figure(12.0, 6.6)
    fig.delaxes(empty_ax)
    fig.text(0.07, 0.96, TITLE, fontsize=11, color=TEXT,
             fontweight="semibold", ha="left")
    subtitle = fig.text(0.07, 0.90, "", fontsize=8.8, color=TEXT_DIM,
                        ha="left")
    stock_ax = fig.add_axes((0.07, 0.30, 0.41, 0.55))
    price_ax = fig.add_axes((0.56, 0.30, 0.38, 0.55))
    stock_readout = fig.text(0.08, 0.19, "", fontsize=7.9, color=PLAN,
                             family="monospace")
    price_readout = fig.text(0.57, 0.19, "", fontsize=7.9, color=PRICE,
                             family="monospace")
    fig.text(0.08, 0.11, stock_formula_text(), fontsize=7.0,
             color=TEXT_DIM, family="monospace")
    fig.text(0.57, 0.11, price_formula_text(), fontsize=7.0,
             color=TEXT_DIM, family="monospace")

    def update(index):
        stage, progress = frame_state(index)
        stock = stock_at(progress)
        plan = plan_at_stock(stock)
        value = value_at_stock(stock)
        objective = objective_at(progress)
        prices = prices_at(objective)
        subtitle.set_text(SUBTITLES[stage])

        stock_ax.clear()
        price_ax.clear()
        style(stock_ax, xlabel="lathe stock b₁", ylabel="press stock b₂")
        stock_ax.set_xlim(0, 52)
        stock_ax.set_ylim(0, 47)
        stock_ax.set_xticks(range(0, 51, 10))
        stock_ax.set_yticks(range(0, 46, 10))
        stock_ax.set_aspect("equal", adjustable="box")
        stock_ax.add_patch(Polygon(
            ((0, 0), (40, 40), (52, 26), (0, 0)),
            closed=True, facecolor=PLAN, alpha=0.11, edgecolor="none",
            zorder=1,
        ))
        stock_ax.plot((0, 40), (0, 40), color=PLAN, linewidth=1.1, zorder=2)
        stock_ax.plot((0, 52), (0, 26), color=PLAN, linewidth=1.1, zorder=2)
        stock_ax.axhline(0, color=TEXT_DIM, linewidth=0.8, zorder=2)
        stock_ax.axvline(0, color=TEXT_DIM, linewidth=0.8, zorder=2)
        stock_ax.plot(
            (float(STOCK_START[0]), float(STOCK_FINAL[0])),
            (float(STOCK_START[1]), float(STOCK_FINAL[1])),
            color=PLAN, alpha=0.55, linewidth=1.2, linestyle=(0, (3, 2)),
            zorder=3,
        )
        stock_ax.plot(float(STOCK_REFERENCE[0]), float(STOCK_REFERENCE[1]),
                      "o", color=TEXT_DIM, markersize=4.4, zorder=4)
        stock_ax.annotate(
            "base (32, 20)", xy=tuple(map(float, STOCK_REFERENCE)),
            xytext=(7, -14), textcoords="offset points", color=TEXT_DIM,
            fontsize=6.9,
        )
        for point, label, offset in (
                (STOCK_TIE_ANCHORS[0], "20·(1, 1): 3-ply only",
                 (-50, -18)),
                (STOCK_TIE_ANCHORS[1], "20·(2, 1): 5-ply only",
                 (8, 10))):
            stock_ax.plot(float(point[0]), float(point[1]), "o",
                          color=PLAN, markeredgecolor=SURFACE,
                          markeredgewidth=0.7, markersize=4.1, zorder=4)
            if (stage == 0 and point == STOCK_TIE_ANCHORS[0]) or (
                    stage == 2 and point == STOCK_TIE_ANCHORS[1]):
                stock_ax.annotate(
                    label, xy=tuple(map(float, point)), xytext=offset,
                    textcoords="offset points", color=WARN, fontsize=6.7,
                    arrowprops=dict(arrowstyle="-", color=WARN,
                                    linewidth=0.55),
                    bbox=dict(boxstyle="square,pad=0.10",
                              facecolor=SURFACE, edgecolor=WARN,
                              linewidth=0.4),
                    zorder=8,
                )
        stock_ax.annotate(
            "", xy=tuple(map(float, stock)),
            xytext=(float(stock[0]) - 2.4, float(stock[1])),
            arrowprops=dict(arrowstyle="-|>", color=PLAN, linewidth=1.8),
            zorder=6,
        )
        stock_ax.plot(float(stock[0]), float(stock[1]), "o", color=PLAN,
                      markeredgecolor=WARN if stage != 1 else SURFACE,
                      markeredgewidth=1.4, markersize=7.0, zorder=7)
        stock_readout.set_text(
            f"b = {_format_pair(stock)}   plan = {_format_pair(plan)}"
            f"   value = {fraction_text(value)}"
        )
        stock_ax.annotate(
            "3-ply column (1, 1)", xy=(15, 15), xytext=(10, 27),
            textcoords="data", color=PLAN, fontsize=6.7,
            arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.45),
            bbox=dict(boxstyle="square,pad=0.10", facecolor=SURFACE,
                      edgecolor=PLAN, linewidth=0.35),
            zorder=7,
        )
        stock_ax.annotate(
            "5-ply column (2, 1)", xy=(38, 19), xytext=(31, 10),
            textcoords="data", color=PLAN, fontsize=6.7,
            arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.45),
            bbox=dict(boxstyle="square,pad=0.10", facecolor=SURFACE,
                      edgecolor=PLAN, linewidth=0.35),
            zorder=7,
        )

        style(price_ax, xlabel="3-ply value c₁", ylabel="5-ply value c₂")
        price_ax.set_xlim(0, 6.7)
        price_ax.set_ylim(0, 8)
        price_ax.set_xticks(range(0, 7))
        price_ax.set_yticks(range(0, 9, 2))
        price_ax.set_aspect("equal", adjustable="box")
        price_ax.add_patch(Polygon(
            ((0, 0), (3.5, 7), (6.5, 6.5), (0, 0)),
            closed=True, facecolor=PRICE, alpha=0.11, edgecolor="none",
            zorder=1,
        ))
        price_ax.plot((0, 3.5), (0, 7), color=PRICE, linewidth=1.1, zorder=2)
        price_ax.plot((0, 6.5), (0, 6.5), color=PRICE, linewidth=1.1,
                      zorder=2)
        price_ax.axhline(0, color=TEXT_DIM, linewidth=0.8, zorder=2)
        price_ax.axvline(0, color=TEXT_DIM, linewidth=0.8, zorder=2)
        price_ax.plot(
            (float(PRICE_START[0]), float(PRICE_FINAL[0])),
            (float(PRICE_START[1]), float(PRICE_FINAL[1])),
            color=PRICE, alpha=0.55, linewidth=1.2, linestyle=(0, (3, 2)),
            zorder=3,
        )
        price_ax.plot(float(PRICE_REFERENCE[0]), float(PRICE_REFERENCE[1]),
                      "o", color=TEXT_DIM, markersize=4.4, zorder=4)
        price_ax.annotate(
            "base c = (3, 5)", xy=tuple(map(float, PRICE_REFERENCE)),
            xytext=(7, -15), textcoords="offset points", color=TEXT_DIM,
            fontsize=6.9,
        )
        for point, label, offset in (
                (PRICE_TIE_ANCHORS[0], "lathe edge ties", (-55, -17)),
                (PRICE_TIE_ANCHORS[1], "press edge ties", (8, 10))):
            price_ax.plot(float(point[0]), float(point[1]), "o",
                          color=PRICE, markeredgecolor=SURFACE,
                          markeredgewidth=0.7, markersize=4.1, zorder=4)
            if (stage == 0 and point == PRICE_TIE_ANCHORS[0]) or (
                    stage == 2 and point == PRICE_TIE_ANCHORS[1]):
                price_ax.annotate(
                    label, xy=tuple(map(float, point)), xytext=offset,
                    textcoords="offset points", color=WARN, fontsize=6.8,
                    arrowprops=dict(arrowstyle="-", color=WARN,
                                    linewidth=0.55),
                    bbox=dict(boxstyle="square,pad=0.10",
                              facecolor=SURFACE, edgecolor=WARN,
                              linewidth=0.4),
                    zorder=8,
                )
        price_ax.annotate(
            "", xy=tuple(map(float, objective)),
            xytext=(0, 0),
            arrowprops=dict(arrowstyle="-|>", color=PRICE, linewidth=1.8),
            zorder=6,
        )
        price_ax.plot(float(objective[0]), float(objective[1]), "o",
                      color=PRICE, markeredgecolor=WARN if stage != 1
                      else SURFACE, markeredgewidth=1.4, markersize=7.0,
                      zorder=7)
        price_readout.set_text(
            f"c = {_format_pair(objective)}   prices y = {_format_pair(prices)}"
        )
        price_ax.annotate(
            "lathe row (1, 2)", xy=(2.8, 5.6), xytext=(3.8, 7.0),
            textcoords="data", color=PRICE, fontsize=6.7,
            arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.45),
            bbox=dict(boxstyle="square,pad=0.10", facecolor=SURFACE,
                      edgecolor=PRICE, linewidth=0.35),
            zorder=7,
        )
        price_ax.annotate(
            "press row (1, 1)", xy=(4.8, 4.8), xytext=(4.0, 3.2),
            textcoords="data", color=PRICE, fontsize=6.7,
            arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.45),
            bbox=dict(boxstyle="square,pad=0.10", facecolor=SURFACE,
                      edgecolor=PRICE, linewidth=0.35),
            zorder=7,
        )
        return []

    animate(fig, update, TOTAL_FRAMES, OUT / "ranges.gif", fps=12, hold=3.0,
            preserve_colors=(PLAN, PRICE, WARN))


if __name__ == "__main__":
    ranges_gif()
