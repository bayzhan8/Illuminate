"""Slide a redundant resource wall through the mill's corner."""

import math
from fractions import Fraction as Q

from matplotlib.patches import Polygon

from illuminate.draw import (PLAN, SURFACE, TEXT, TEXT_DIM, WARN,
                             animate, chapter_dir, figure, margin_note, style)
from linprog.corners import is_degenerate, tight
from linprog.lp import best_by_enumeration, vertices

if __package__:
    from .fig12a_kink import (GLUE_ROW, LATHE_ROW, OBJECTIVE, PRESS_ROW,
                              chapter_lp, format_number)
else:
    from fig12a_kink import (GLUE_ROW, LATHE_ROW, OBJECTIVE, PRESS_ROW,
                             chapter_lp, format_number)

OUT = chapter_dir("12-degeneracy")
TITLE = "A perturbation splits the corner"
HOLD_FRAMES = 24
MOVE_FRAMES = 24
TOTAL_FRAMES = 5 * HOLD_FRAMES
HOLD_INDICES = (
    0,
    HOLD_FRAMES + MOVE_FRAMES,
    2 * HOLD_FRAMES + 2 * MOVE_FRAMES,
)
LATHE_STOCK = Q(32)
PRESS_STOCK = Q(20)
LATHE_LABEL_ANCHOR = (Q(2), Q(15))
PRESS_LABEL_ANCHOR = (Q(14), Q(6))


def glue_label_anchor(stock):
    stock = Q(stock)
    t = Q(12)
    return t, (stock - 2 * t) / 3


def wall_label_anchors(stock):
    return LATHE_LABEL_ANCHOR, PRESS_LABEL_ANCHOR, glue_label_anchor(stock)


def changed_corner_anchors(stock):
    stock = Q(stock)
    lp = chapter_lp(glue_stock=stock)
    return tuple(sorted(
        point for point in vertices(lp)
        if sum((a * x for a, x in zip(GLUE_ROW, point)), Q(0)) == stock
    ))


def _ease(step):
    progress = Q(step, MOVE_FRAMES - 1)
    return progress * progress * (3 - 2 * progress)


def frame_stock(index):
    index = max(0, min(index, TOTAL_FRAMES - 1))
    if index < HOLD_FRAMES:
        return Q(56)
    if index < HOLD_FRAMES + MOVE_FRAMES:
        return Q(56) - 4 * _ease(index - HOLD_FRAMES)
    if index < 2 * HOLD_FRAMES + MOVE_FRAMES:
        return Q(52)
    if index < 2 * HOLD_FRAMES + 2 * MOVE_FRAMES:
        return Q(52) - 2 * _ease(index - 2 * HOLD_FRAMES - MOVE_FRAMES)
    return Q(50)


def _format_number(value):
    return format_number(value)


def subtitle_for_stock(stock):
    stock = Q(stock)
    lp = chapter_lp(glue_stock=stock)
    best, value = best_by_enumeration(lp)
    if stock > 52:
        return (f"g = {_format_number(stock)}: glue slack; "
                f"(8, 12) has two tight rows")
    if stock == 52:
        return "g = 52: three rows tight at (8, 12), degenerate"
    new_corners = changed_corner_anchors(stock)
    ranked = sorted(new_corners, key=lp.value, reverse=True)
    if stock == 50:
        labels = ", ".join(
            f"{_fmt_point(point)} worth {_format_number(lp.value(point))}"
            for point in ranked
        )
        return f"g = 50: {labels}; {_fmt_point(best)} is best"
    return (f"g = {_format_number(stock)}: glue cuts the corner; "
            f"best {_fmt_point(best)} worth {_format_number(value)}")


def subtitle_for_frame(index):
    return subtitle_for_stock(frame_stock(index))


def _polygon_points(points):
    coordinates = [(float(t), float(f)) for t, f in points]
    center = (sum(t for t, _ in coordinates) / len(coordinates),
              sum(f for _, f in coordinates) / len(coordinates))
    return sorted(coordinates,
                  key=lambda point: math.atan2(point[1] - center[1],
                                               point[0] - center[0]))


def _fmt_point(point):
    return f"({', '.join(_format_number(value) for value in point)})"


def glue_gif():
    fig, ax = figure(8.2, 6.4)
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.19, top=0.81)
    fig.text(0.08, 0.96, TITLE, fontsize=11, color=TEXT,
             fontweight="semibold", ha="left")
    subtitle = fig.text(0.08, 0.90, "", fontsize=8.8, color=TEXT_DIM,
                        ha="left")
    note = margin_note(fig, y=0.025, size=8.9)
    full_rows = (LATHE_ROW, PRESS_ROW, GLUE_ROW, (Q(-1), Q(0)),
                 (Q(0), Q(-1)))

    def update(index):
        index = min(index, TOTAL_FRAMES - 1)
        stock = frame_stock(index)
        lp = chapter_lp(glue_stock=stock)
        rhs = (LATHE_STOCK, PRESS_STOCK, stock, Q(0), Q(0))
        full_a = full_rows
        best, value = best_by_enumeration(lp)
        region = _polygon_points(vertices(lp))
        subtitle.set_text(subtitle_for_stock(stock))

        ax.clear()
        style(ax, xlabel="3-ply batches t", ylabel="5-ply batches f")
        ax.set_xlim(-0.7, 22)
        ax.set_ylim(-0.7, 20)
        ax.set_xticks(range(0, 21, 4))
        ax.set_yticks(range(0, 21, 4))
        ax.set_aspect("equal", adjustable="box")
        ax.add_patch(Polygon(region, closed=True, facecolor=PLAN, alpha=0.12,
                             edgecolor="none", zorder=1))
        closed = region + [region[0]]
        ax.plot([point[0] for point in closed],
                [point[1] for point in closed], color=PLAN,
                linewidth=1.0, zorder=2)
        t_values = (Q(-1), Q(22))
        for row, bound in zip((LATHE_ROW, PRESS_ROW, GLUE_ROW),
                              (LATHE_STOCK, PRESS_STOCK, stock)):
            f_values = tuple((bound - row[0] * t) / row[1]
                             for t in t_values)
            ax.plot([float(t) for t in t_values],
                    [float(f) for f in f_values], color=TEXT_DIM,
                    linewidth=1.1, zorder=3)
        ax.axhline(0, color=TEXT_DIM, linewidth=0.9, zorder=3)
        ax.axvline(0, color=TEXT_DIM, linewidth=0.9, zorder=3)

        degenerate = is_degenerate(full_a, rhs, best)
        for point in vertices(lp):
            is_best = point == best
            color = WARN if is_best and degenerate else PLAN
            ax.plot([float(point[0])], [float(point[1])], "o",
                    color=color, markeredgecolor=SURFACE,
                    markeredgewidth=1.3 if is_best else 0.8,
                    markersize=8 if is_best else 4.5, zorder=7)

        for label, anchor, text_position in (
                ("lathe wall", LATHE_LABEL_ANCHOR, (0.6, 18)),
                ("glue wall", glue_label_anchor(stock), (13, 14)),
                ("press wall", PRESS_LABEL_ANCHOR, (16.5, 2))):
            color = TEXT_DIM
            ax.annotate(
                label, xy=tuple(float(value) for value in anchor),
                xytext=text_position, textcoords="data", color=color,
                fontsize=7.1,
                arrowprops=dict(arrowstyle="-", color=color, linewidth=0.55),
                bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                          edgecolor=color, linewidth=0.4),
                zorder=9,
            )

        changed = changed_corner_anchors(stock)
        if stock > 52:
            ax.annotate(
                f"best {_fmt_point(best)}, {_format_number(value)}",
                xy=tuple(float(value) for value in best), xytext=(10, 8),
                textcoords="offset points", color=PLAN, fontsize=7.2,
                arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.55),
                bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                          edgecolor=PLAN, linewidth=0.4),
                zorder=10,
            )
        elif stock == 52:
            ax.annotate(
                "(8, 12): degenerate",
                xy=(8, 12), xytext=(12, -19), textcoords="offset points",
                color=WARN, fontsize=7.2,
                arrowprops=dict(arrowstyle="-", color=WARN, linewidth=0.6),
                bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                          edgecolor=WARN, linewidth=0.45),
                zorder=10,
            )
        else:
            for position, point in enumerate(changed):
                label = (f"best {_fmt_point(point)}, "
                         f"{_format_number(lp.value(point))}"
                         if point == best else
                         f"{_fmt_point(point)}, {_format_number(lp.value(point))}")
                offset = (8, 10) if position == 0 else (12, -20)
                ax.annotate(
                    label, xy=tuple(float(value) for value in point),
                    xytext=offset, textcoords="offset points", color=PLAN,
                    fontsize=7.0,
                    arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.55),
                    bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                              edgecolor=PLAN, linewidth=0.4),
                    zorder=10,
                )

        tight_count = len(tight(full_a, rhs, best))
        note.set_text(f"g = {_format_number(stock)}    best {_fmt_point(best)}"
                      f"    value = {_format_number(value)}"
                      f"    tight rows = {tight_count}")
        return []

    animate(fig, update, TOTAL_FRAMES, OUT / "glue.gif", fps=12, hold=3.0,
            preserve_colors=(WARN,))


if __name__ == "__main__":
    glue_gif()
