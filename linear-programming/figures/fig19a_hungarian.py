"""Prices grow until the tight assignment graph has a perfect matching."""

from fractions import Fraction as Q

from matplotlib.patches import Circle, Rectangle

from illuminate.draw import (HAIRLINE, PLAN, PRICE, SURFACE, TEXT, TEXT_DIM,
                             WARN, animate, chapter_dir, figure)
from linprog.primal_dual import hungarian

OUT = chapter_dir("19-primal-dual")
ORDERS = ("birch", "pine", "alder")
COSTS = (
    (Q(4), Q(2), Q(5)),
    (Q(3), Q(6), Q(4)),
    (Q(5), Q(4), Q(7)),
)
RESULT = hungarian(COSTS)
ROUND_BOUNDS = tuple(round_.bound for round_ in RESULT.rounds)
ASSIGNMENT_CELLS = tuple(sorted(RESULT.assignment.items()))

TITLE = "Prices first, then plans"
HOLD_FRAMES = 18
MOVE_FRAMES = 18
TOTAL_FRAMES = (
    len(RESULT.rounds) * HOLD_FRAMES
    + (len(RESULT.rounds) - 1) * MOVE_FRAMES
)
HOLD_INDICES = tuple(
    HOLD_FRAMES + index * (HOLD_FRAMES + MOVE_FRAMES) - 1
    for index in range(len(RESULT.rounds))
)


def fraction_text(value):
    value = Q(value)
    sign = "−" if value < 0 else ""
    numerator = abs(value.numerator)
    if value.denominator == 1:
        return f"{sign}{numerator}"
    return f"{sign}{numerator}/{value.denominator}"


def _move_subtitle(round_):
    rows = ", ".join(f"u{row + 1}" for row in round_.S)
    columns = ", ".join(f"v_{ORDERS[column]}" for column in round_.N)
    return (
        f"raise {rows}; lower {columns} by theta = "
        f"{fraction_text(round_.theta)}"
    )


ROUND_SUBTITLES = tuple(
    (
        f"round {index}: {len(round_.S)} lathes, "
        f"{len(round_.N)} order"
        f"{'' if len(round_.N) == 1 else 's'}; "
        f"theta = {fraction_text(round_.theta)} at lathe "
        f"{round_.theta_pair[0] + 1}–{ORDERS[round_.theta_pair[1]]}"
        if round_.theta_pair is not None
        else f"round {index}: the tight pairs make a full assignment"
    )
    for index, round_ in enumerate(RESULT.rounds)
)
MOVE_SUBTITLES = tuple(
    _move_subtitle(round_) for round_ in RESULT.rounds[:-1]
)
BOUND_TEXT = "bound Σu + Σv = " + " → ".join(
    fraction_text(value) for value in ROUND_BOUNDS
)


def frame_state(index):
    index = max(0, min(index, TOTAL_FRAMES - 1))
    for round_index in range(len(RESULT.rounds)):
        if index < HOLD_FRAMES:
            return round_index, False, Q(0)
        index -= HOLD_FRAMES
        if round_index < len(RESULT.rounds) - 1:
            if index < MOVE_FRAMES:
                return round_index, True, Q(index, MOVE_FRAMES - 1)
            index -= MOVE_FRAMES
    return len(RESULT.rounds) - 1, False, Q(0)


def subtitle_for_frame(index):
    round_index, moving, _ = frame_state(index)
    return (
        MOVE_SUBTITLES[round_index]
        if moving else ROUND_SUBTITLES[round_index]
    )


def _display_prices(round_index, moving, progress):
    start = RESULT.rounds[round_index]
    if not moving:
        return start.u, start.v
    end = RESULT.rounds[round_index + 1]
    u = tuple(
        left + progress * (right - left)
        for left, right in zip(start.u, end.u)
    )
    v = tuple(
        left + progress * (right - left)
        for left, right in zip(start.v, end.v)
    )
    return u, v


def _draw_frame(ax, round_index, moving, progress):
    round_ = RESULT.rounds[round_index]
    u, v = _display_prices(round_index, moving, progress)
    obstruction_rows = set(round_.S)
    obstruction_columns = set(round_.N)
    final = round_index == len(RESULT.rounds) - 1 and not moving
    assigned = set(ASSIGNMENT_CELLS) if final else set()

    ax.clear()
    ax.set_xlim(-2.45, 6.0)
    ax.set_ylim(-0.68, 4.1)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    ax.text(
        -2.2, 3.93, "slack  c_ij − u_i − v_j",
        color=TEXT_DIM, fontsize=8.7, ha="left", va="center",
    )
    for column, order in enumerate(ORDERS):
        ax.text(
            column + 0.5, 3.58, f"v{column + 1} = {fraction_text(v[column])}",
            color=PRICE, fontsize=9, ha="center", va="center",
        )
        ax.text(
            column + 0.5, 3.25, order,
            color=TEXT_DIM, fontsize=9, ha="center", va="center",
        )

    for row in range(3):
        y = 2 - row
        ax.text(
            -2.2, y + 0.5, f"u{row + 1} = {fraction_text(u[row])}",
            color=PRICE, fontsize=9, ha="left", va="center",
        )
        ax.text(
            -0.22, y + 0.5, f"lathe {row + 1}",
            color=TEXT_DIM, fontsize=8.5, ha="right", va="center",
        )
        for column in range(3):
            slack = COSTS[row][column] - u[row] - v[column]
            tight = slack == 0
            is_assigned = (row, column) in assigned
            obstruction = (
                row in obstruction_rows
                or column in obstruction_columns
            )
            face = PLAN if is_assigned else WARN if obstruction else SURFACE
            alpha = 0.15 if is_assigned else 0.12 if obstruction else 1
            ax.add_patch(Rectangle(
                (column, y), 1, 1, facecolor=face, alpha=alpha,
                edgecolor=PLAN if tight else HAIRLINE,
                linewidth=2.0 if tight else 0.9, zorder=1,
            ))
            ax.text(
                column + 0.5, y + 0.53, fraction_text(slack),
                color=PLAN if tight else TEXT, fontsize=11,
                fontweight="semibold" if tight else "normal",
                ha="center", va="center", zorder=3,
            )
            if is_assigned:
                ax.text(
                    column + 0.83, y + 0.15, "✓",
                    color=PLAN, fontsize=9, ha="center", va="center",
                    fontweight="semibold", zorder=4,
                )

    if round_.theta_pair is not None:
        row, column = round_.theta_pair
        y = 2 - row
        ax.add_patch(Circle(
            (column + 0.5, y + 0.53), radius=0.31,
            fill=False, edgecolor=WARN, linewidth=2.0, zorder=5,
        ))

    if round_.S:
        label = f"{len(round_.S)} lathes, {len(round_.N)} order"
        if len(round_.N) != 1:
            label += "s"
        ax.text(
            3.35, 2.55, "amber obstruction",
            color=WARN, fontsize=8.4, ha="left", va="center",
            fontweight="semibold",
        )
        ax.text(
            3.35, 2.14, label, color=WARN, fontsize=10.5,
            ha="left", va="center",
        )
        row, column = round_.theta_pair
        ax.text(
            3.35, 1.53,
            f"theta = {fraction_text(round_.theta)} at\n"
            f"lathe {row + 1}–{ORDERS[column]}",
            color=WARN, fontsize=9.2, ha="left", va="center",
        )
    else:
        ax.text(
            3.35, 2.55, "assignment",
            color=PLAN, fontsize=8.4, ha="left", va="center",
            fontweight="semibold",
        )
        for offset, (row, column) in enumerate(ASSIGNMENT_CELLS):
            ax.text(
                3.35, 2.12 - 0.34 * offset,
                f"lathe {row + 1} → {ORDERS[column]}",
                color=PLAN, fontsize=9.4, ha="left", va="center",
            )


def hungarian_gif():
    fig, empty_ax = figure(11.0, 6.2)
    fig.delaxes(empty_ax)
    fig.text(
        0.07, 0.96, TITLE, fontsize=11, color=TEXT,
        fontweight="semibold", ha="left",
    )
    subtitle = fig.text(
        0.07, 0.90, "", fontsize=8.8, color=TEXT_DIM, ha="left"
    )
    ax = fig.add_axes((0.07, 0.19, 0.86, 0.68))
    bound = fig.text(
        0.08, 0.085, BOUND_TEXT, color=PRICE, fontsize=9.2,
        family="monospace", ha="left", va="center",
    )
    cost = fig.text(
        0.67, 0.085, "", color=TEXT, fontsize=9.8,
        family="monospace", fontweight="semibold", ha="left", va="center",
    )

    def update(index):
        round_index, moving, progress = frame_state(index)
        subtitle.set_text(subtitle_for_frame(index))
        _draw_frame(ax, round_index, moving, progress)
        if round_index == len(RESULT.rounds) - 1 and not moving:
            final_bound = RESULT.rounds[-1].bound
            cost.set_text(
                f"cost {fraction_text(RESULT.cost)} = "
                f"bound {fraction_text(final_bound)}"
            )
        else:
            cost.set_text("")
        return [subtitle, bound, cost]

    animate(
        fig, update, TOTAL_FRAMES, OUT / "hungarian.gif",
        fps=12, hold=3.0, preserve_colors=(PLAN, PRICE, WARN),
    )


if __name__ == "__main__":
    hungarian_gif()
