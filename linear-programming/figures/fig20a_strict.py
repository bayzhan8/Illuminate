"""Move through the optimal price face to a strictly complementary pair."""

from fractions import Fraction as Q

from matplotlib.patches import Rectangle

from illuminate.draw import (HAIRLINE, PLAN, PRICE, PRICE_FILL, SURFACE, TEXT,
                             TEXT_DIM, WARN, animate, chapter_dir, figure,
                             style)
from linprog.strict import strict_pair

OUT = chapter_dir("20-strict")
RESOURCES = ("lathe", "press", "glue")
A = (
    (Q(1), Q(2)),
    (Q(1), Q(1)),
    (Q(2), Q(3)),
)
B = (Q(32), Q(20), Q(52))
C = (Q(3), Q(5))
RESULT = strict_pair(A, B, C)
START_PRICES = RESULT.price_witnesses[0]
END_PRICES = RESULT.price_witnesses[2]
MIDDLE_PRICES = tuple(
    (left + right) / 2
    for left, right in zip(START_PRICES, END_PRICES)
)
PARAMETERS = (
    START_PRICES[2], MIDDLE_PRICES[2], END_PRICES[2]
)
BILL = sum(
    (bound * price for bound, price in zip(B, MIDDLE_PRICES)), Q(0)
)

TITLE = "The strictest kind of fit"
HOLD_FRAMES = 18
MOVE_FRAMES = 18
TOTAL_FRAMES = 3 * HOLD_FRAMES + 2 * MOVE_FRAMES
HOLD_INDICES = (
    HOLD_FRAMES - 1,
    2 * HOLD_FRAMES + MOVE_FRAMES - 1,
    TOTAL_FRAMES - 1,
)


def fraction_text(value):
    value = Q(value)
    sign = "−" if value < 0 else ""
    numerator = abs(value.numerator)
    if value.denominator == 1:
        return f"{sign}{numerator}"
    return f"{sign}{numerator}/{value.denominator}"


def prices_at(parameter):
    parameter = Q(parameter)
    span = PARAMETERS[2] - PARAMETERS[0]
    progress = (parameter - PARAMETERS[0]) / span
    return tuple(
        left + progress * (right - left)
        for left, right in zip(START_PRICES, END_PRICES)
    )


def frame_state(index):
    index = max(0, min(index, TOTAL_FRAMES - 1))
    for stage in range(3):
        if index < HOLD_FRAMES:
            return stage, False, Q(0)
        index -= HOLD_FRAMES
        if stage < 2:
            if index < MOVE_FRAMES:
                return stage, True, Q(index, MOVE_FRAMES - 1)
            index -= MOVE_FRAMES
    return 2, False, Q(0)


def frame_parameter(index):
    stage, moving, progress = frame_state(index)
    if not moving:
        return PARAMETERS[stage]
    start, end = PARAMETERS[stage:stage + 2]
    return start + progress * (end - start)


def subtitle_for_frame(index):
    stage, moving, _ = frame_state(index)
    parameter = frame_parameter(index)
    if moving:
        return (
            f"prices slide along the optimal face; bill remains "
            f"{fraction_text(BILL)}"
        )
    if stage == 1:
        return (
            f"s = {fraction_text(parameter)}; strict: every tight row "
            "has a positive price"
        )
    return (
        f"s = {fraction_text(parameter)}; "
        "tight but priced 0: not strict"
    )


def _draw_segment(ax, parameter):
    ax.clear()
    ax.set_xlim(-0.06, 1.06)
    ax.set_ylim(-0.63, 0.63)
    ax.axis("off")
    middle = PARAMETERS[1]
    ax.plot(
        [PARAMETERS[0], PARAMETERS[2]], [0, 0],
        color=HAIRLINE, linewidth=2.2, solid_capstyle="round",
    )
    ax.plot(
        [PARAMETERS[0] + Q(1, 50), PARAMETERS[2] - Q(1, 50)], [0, 0],
        color=PLAN, linewidth=2.2, solid_capstyle="round",
    )
    ax.scatter(
        [PARAMETERS[0], PARAMETERS[2]], [0, 0],
        s=52, facecolor=SURFACE, edgecolor=WARN, linewidth=1.8, zorder=4,
    )
    ax.scatter(
        [middle], [0], s=24, facecolor=PLAN, edgecolor=SURFACE,
        linewidth=0.8, zorder=5,
    )
    ax.scatter(
        [float(parameter)], [0], s=36, facecolor=PRICE, edgecolor=TEXT,
        linewidth=0.7, zorder=6,
    )
    ax.text(
        PARAMETERS[0], -0.37, "simplex corners",
        color=WARN, fontsize=8.7, ha="left", va="center",
    )
    ax.text(
        PARAMETERS[2], -0.37, "simplex corners",
        color=WARN, fontsize=8.7, ha="right", va="center",
    )
    ax.text(
        middle, 0.38, "strictly complementary",
        color=PLAN, fontsize=9.1, ha="center", va="center",
        fontweight="semibold",
    )


def _draw_bars(ax, parameter, prices, stage, moving):
    ax.clear()
    style(ax, ylabel="price", grid=True)
    ax.set_xlim(-0.62, len(RESOURCES) - 0.38)
    ax.set_ylim(0, 2.82)
    ax.set_xticks(range(len(RESOURCES)), RESOURCES)
    ax.set_yticks((0, 1, 2))
    ax.tick_params(axis="x", length=0, pad=7)
    ax.tick_params(axis="y", length=0, pad=5)

    middle = stage == 1 and not moving
    for index, price in enumerate(prices):
        height = float(price)
        width = 0.58
        if price > 0:
            ax.add_patch(Rectangle(
                (index - width / 2, 0), width, height,
                facecolor=PRICE_FILL, edgecolor=PRICE, linewidth=1.5,
                zorder=3,
            ))
            label_y = height + 0.07
            label_color = PRICE
        else:
            ax.add_patch(Rectangle(
                (index - width / 2, 0), width, 0.12,
                facecolor="none", edgecolor=WARN, linewidth=1.7,
                zorder=4,
            ))
            label_y = 0.19
            label_color = WARN
        if middle and price > 0:
            ax.add_patch(Rectangle(
                (index - width / 2 - 0.025, 0), width + 0.05, height,
                facecolor="none", edgecolor=PLAN, linewidth=1.0,
                zorder=4,
            ))
        ax.text(
            index, label_y, fraction_text(price), color=label_color,
            fontsize=9.2, ha="center", va="bottom", zorder=5,
        )

    if not moving and stage in (0, 2):
        ax.text(
            1, 2.58, "tight but priced 0: not strict",
            color=WARN, fontsize=9.2, ha="center", va="center",
            fontweight="semibold",
        )
    elif middle:
        ax.text(
            1, 2.58, "strict: every tight row has a positive price",
            color=PLAN, fontsize=9.2, ha="center", va="center",
            fontweight="semibold",
        )


def strict_gif():
    fig, empty_ax = figure(10.2, 6.2)
    fig.delaxes(empty_ax)
    fig.text(
        0.07, 0.96, TITLE, fontsize=11, color=TEXT,
        fontweight="semibold", ha="left",
    )
    subtitle = fig.text(
        0.07, 0.91, "", fontsize=8.8, color=TEXT_DIM, ha="left"
    )
    segment_ax = fig.add_axes((0.16, 0.70, 0.68, 0.14))
    bars_ax = fig.add_axes((0.16, 0.20, 0.68, 0.42))
    bill = fig.text(
        0.17, 0.085, "", color=PRICE, fontsize=9.5,
        family="monospace", ha="left", va="center",
    )
    price_readout = fig.text(
        0.57, 0.085, "", color=TEXT, fontsize=9.5,
        family="monospace", ha="left", va="center",
    )

    def update(index):
        stage, moving, _ = frame_state(index)
        parameter = frame_parameter(index)
        prices = prices_at(parameter)
        subtitle.set_text(subtitle_for_frame(index))
        subtitle.set_color(
            TEXT_DIM if moving
            else PLAN if stage == 1
            else WARN
        )
        _draw_segment(segment_ax, parameter)
        _draw_bars(bars_ax, parameter, prices, stage, moving)
        current_bill = sum(
            (bound * price for bound, price in zip(B, prices)), Q(0)
        )
        bill.set_text(f"bill b y = {fraction_text(current_bill)}")
        price_readout.set_text(
            f"s = {fraction_text(parameter)}; prices = "
            f"({', '.join(fraction_text(price) for price in prices)})"
        )
        return [subtitle, bill, price_readout]

    animate(
        fig, update, TOTAL_FRAMES, OUT / "strict.gif",
        fps=12, hold=3.0, preserve_colors=(PLAN, PRICE, WARN),
    )


if __name__ == "__main__":
    strict_gif()
