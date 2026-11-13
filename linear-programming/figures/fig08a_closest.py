"""The closest plan places a strict wall between itself and an order."""

from fractions import Fraction
from math import sqrt

from illuminate.draw import (PLAN, PRICE, SURFACE, TEXT, TEXT_DIM, WARN,
                             animate, chapter_dir, figure, margin_note)
from linprog import mill as mill
from linprog.lp import vertices
from linprog.separation import project_to_polygon, separator

if __package__:
    from .scene import Stages, claim, draw_axes, line_where, ordered, right_angle
else:
    from scene import Stages, claim, draw_axes, line_where, ordered, right_angle

OUT = chapter_dir("08-separation")
ORDER = (Fraction(11), Fraction(16))
POLYGON_A = mill.MILL.A + ((Fraction(-1), Fraction(0)),
                           (Fraction(0), Fraction(-1)))
POLYGON_B = mill.MILL.b + (Fraction(0), Fraction(0))
CORNER, DISTANCE_SQUARED = project_to_polygon(ORDER, POLYGON_A, POLYGON_B)
MILL_CORNERS = vertices(mill.MILL)
START = next(p for p in MILL_CORNERS if p[0] == 0 and p[1] > 0)
END = next(p for p in MILL_CORNERS if p[0] > 0 and p[1] == 0)
NORMAL = tuple(o - s for o, s in zip(ORDER, CORNER))
MAX_PLAN_VALUE = max(
    sum((a * b for a, b in zip(NORMAL, point)), Fraction(0))
    for point in MILL_CORNERS
)
ORDER_VALUE = sum((a * b for a, b in zip(NORMAL, ORDER)), Fraction(0))
STAGES = Stages((18, 0), (0, 18), (24, 8))
TITLE = "the nearest plan draws a wall the order cannot cross"


def display(value):
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{float(value):.1f}".rstrip("0").rstrip(".")


def display_point(point):
    return f"({display(point[0])}, {display(point[1])})"


def interpolate(start, end, amount):
    return tuple(a + amount * (b - a) for a, b in zip(start, end))


def closest_label_anchors(probe):
    pi, pi0 = separator(ORDER, CORNER)
    t = Fraction(12)
    wall = (t, (pi0 - pi[0] * t) / pi[1])
    return ORDER, tuple(probe), wall


def wall_equation_label():
    pi, pi0 = separator(ORDER, CORNER)
    normal = tuple(-value for value in pi)
    return (f"{display(normal[0])}t + {display(normal[1])}f = "
            f"{display(-pi0)}")


def probe_at(frame):
    stage, progress = STAGES(frame)
    if stage == 0:
        return interpolate(START, CORNER, Fraction(str(progress)))
    if stage == 1:
        return CORNER
    return interpolate(CORNER, END, Fraction(str(progress)))


def draw_region_and_walls(ax):
    boundary = ordered(mill.MILL)
    ax.fill([p[0] for p in boundary], [p[1] for p in boundary],
            color=PLAN, alpha=0.11, zorder=1, linewidth=0)
    line_where(ax, mill.MILL.A[0], mill.MILL.b[0],
               color=TEXT, linewidth=1.25, zorder=3)
    line_where(ax, mill.MILL.A[1], mill.MILL.b[1],
               color=TEXT, linewidth=1.25, zorder=3)


def closest_gif():
    fig, ax = figure(8.2, 6.7)
    fig.subplots_adjust(left=0.1, right=0.96, top=0.81, bottom=0.19)
    note = margin_note(fig, y=0.02, size=8.8)

    def update(i):
        i = min(i, STAGES.total - 1)
        stage, _ = STAGES(i)
        probe = probe_at(i)
        separation = (ORDER[0] - probe[0], ORDER[1] - probe[1])
        distance_squared = sum((v * v for v in separation), Fraction(0))
        distance = sqrt(float(distance_squared))
        at_corner = stage == 1
        final = i == STAGES.total - 1
        _, _, wall_anchor = closest_label_anchors(probe)

        ax.clear()
        draw_axes(ax)
        ax.set_ylim(0, 22)
        ax.set_yticks(range(0, 23, 4))
        draw_region_and_walls(ax)
        segment_end = CORNER if final else probe
        ax.plot([float(ORDER[0]), float(segment_end[0])],
                [float(ORDER[1]), float(segment_end[1])],
                color=TEXT_DIM, linewidth=1.2,
                linestyle="-" if at_corner or final else (0, (3, 3)),
                zorder=4)
        ax.plot([float(probe[0])], [float(probe[1])], "o", color=PLAN,
                markeredgecolor=SURFACE, markeredgewidth=1.5,
                markersize=9, zorder=7)
        ax.plot([float(ORDER[0])], [float(ORDER[1])], "o", color=WARN,
                markeredgecolor=SURFACE, markeredgewidth=1.3,
                markersize=8, zorder=7)

        if at_corner or final:
            ax.plot([float(CORNER[0])], [float(CORNER[1])], "o",
                    color=PLAN, markeredgecolor=SURFACE, markeredgewidth=1.5,
                    markersize=9, zorder=8)
            ax.annotate(f"{display_point(CORNER)}: nearest plan",
                        xy=tuple(map(float, CORNER)),
                        xytext=(-9, -15), textcoords="offset points",
                        color=PLAN, fontsize=8.5, ha="right", va="top",
                        bbox=dict(boxstyle="square,pad=0.15",
                                  facecolor=SURFACE, edgecolor="none"),
                        zorder=9)

        order_anchor, probe_anchor, _ = closest_label_anchors(probe)
        ax.annotate(
            "order x = (11, 16)", xy=tuple(map(float, order_anchor)),
            xytext=(10, 10), textcoords="offset points",
            color=WARN, fontsize=8.5, ha="left", va="bottom",
            bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                      edgecolor=WARN, linewidth=0.55),
            zorder=9,
        )
        probe_dx = -10 if probe[0] > 18 else 8
        probe_dy = 9 if probe[1] < 16 else -12
        ax.annotate(
            "probe", xy=tuple(map(float, probe_anchor)),
            xytext=(probe_dx, probe_dy), textcoords="offset points",
            color=PLAN, fontsize=8.5,
            ha="right" if probe_dx < 0 else "left",
            va="bottom" if probe_dy > 0 else "top",
            bbox=dict(boxstyle="square,pad=0.14", facecolor=SURFACE,
                      edgecolor="none"),
            zorder=9,
        )

        if final:
            pi, pi0 = separator(ORDER, CORNER)
            line_where(ax, pi, pi0, color=PRICE, linewidth=1.8, zorder=6)
            ax.annotate(
                wall_equation_label(), xy=tuple(map(float, wall_anchor)),
                xytext=(8, 8), textcoords="offset points",
                color=PRICE, fontsize=8.8, ha="left", va="bottom",
                bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE,
                          edgecolor=PRICE, linewidth=0.6),
                arrowprops=dict(arrowstyle="-", color=PRICE, linewidth=0.65,
                                shrinkA=2, shrinkB=1),
                zorder=10,
            )
            midpoint = tuple((a + b) / 2 for a, b in zip(ORDER, CORNER))
            ax.plot([float(midpoint[0])], [float(midpoint[1])], "o",
                    color=TEXT_DIM, markersize=4, zorder=8)
            normal_length = sqrt(float(sum((value * value
                                            for value in NORMAL), Fraction(0))))
            normal_unit = (float(NORMAL[0]) / normal_length,
                           float(NORMAL[1]) / normal_length)
            right_angle(ax, tuple(map(float, midpoint)),
                        normal_unit, (normal_unit[1], -normal_unit[0]),
                        s=0.55,
                        color=TEXT_DIM)
            ax.text(1.0, 3.3,
                    f"every plan: {display(NORMAL[0])}t + "
                    f"{display(NORMAL[1])}f ≤ {display(MAX_PLAN_VALUE)}",
                    color=PLAN, fontsize=8.2, ha="left",
                    bbox=dict(boxstyle="square,pad=0.14",
                              facecolor=SURFACE, edgecolor="none"),
                    zorder=9)
            claim(ax, TITLE)
            subtitle = (
                f"the order gives {display(ORDER_VALUE)}; every plan is at "
                f"most {display(MAX_PLAN_VALUE)}"
            )
            ax.text(0, 1.025, subtitle, transform=ax.transAxes, fontsize=9.2,
                    color=TEXT_DIM, ha="left", va="bottom")
        else:
            subtitles = (
                "the probe follows the mill's edge",
                "the shortest distance is 5.00",
                "past the corner, the distance grows again",
            )
            claim(ax, TITLE, subtitles[stage])

        note.set_text(
            f"distance from x to probe = {distance:.2f}"
            + (f"\nwall: {wall_equation_label()}; order gives "
               f"{display(ORDER_VALUE)}, plans at most {display(MAX_PLAN_VALUE)}"
               if final else "")
        )
        return []

    animate(fig, update, STAGES.total, OUT / "closest.gif", fps=12, hold=3.0)


if __name__ == "__main__":
    closest_gif()
