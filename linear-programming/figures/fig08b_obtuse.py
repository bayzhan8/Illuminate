"""Plans make an obtuse angle at their nearest point."""

from fractions import Fraction
from math import acos, atan2, cos, degrees, hypot, radians, sin

from matplotlib.patches import Arc

from illuminate.draw import (PLAN, SURFACE, TEXT, TEXT_DIM, WARN,
                             animate, chapter_dir, figure, margin_note)
from linprog import mill as mill
from linprog.lp import vertices
from linprog.separation import project_to_polygon

if __package__:
    from .scene import Stages, claim, draw_axes, line_where, ordered
else:
    from scene import Stages, claim, draw_axes, line_where, ordered

OUT = chapter_dir("08-separation")
ORDER = (Fraction(11), Fraction(16))
POLYGON_A = mill.MILL.A + ((Fraction(-1), Fraction(0)),
                           (Fraction(0), Fraction(-1)))
POLYGON_B = mill.MILL.b + (Fraction(0), Fraction(0))
STAR = project_to_polygon(ORDER, POLYGON_A, POLYGON_B)[0]
NORMAL = tuple(o - s for o, s in zip(ORDER, STAR))
BOUND = sum((a * b for a, b in zip(NORMAL, STAR)), Fraction(0))
CORNERS = vertices(mill.MILL)
START = next(p for p in CORNERS if p[0] == 0 and p[1] > 0)
BOTTOM = next(p for p in CORNERS if p[0] == 0 and p[1] == 0)
RIGHT = next(p for p in CORNERS if p[0] > 0 and p[1] == 0)
INSIDE_PATH = (STAR, START, BOTTOM, RIGHT, STAR)
OUTSIDE = (STAR[0] + 4, STAR[1] + 2)
WALK_MIDPOINT = tuple((a + b) / 2 for a, b in zip(STAR, OUTSIDE))
OUTSIDE_DISTANCE_SQUARED = sum(
    ((a - b) ** 2 for a, b in zip(ORDER, WALK_MIDPOINT)), Fraction(0)
)
STAR_DISTANCE_SQUARED = sum(
    ((a - b) ** 2 for a, b in zip(ORDER, STAR)), Fraction(0)
)
STAGES = Stages((0, 10), (48, 12), (1, 0))
TITLE = "no feasible plan points acutely towards the order"


def display(value):
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{float(value):.1f}".rstrip("0").rstrip(".")


def display_point(point):
    return f"({display(point[0])}, {display(point[1])})"


def product_formula():
    return (f"{display(NORMAL[0])}t + {display(NORMAL[1])}f − "
            f"{display(BOUND)}")


def obtuse_label_anchors(plan):
    return ORDER, STAR, tuple(plan), WALK_MIDPOINT


def path_point(progress):
    scaled = progress * (len(INSIDE_PATH) - 1)
    segment = min(int(scaled), len(INSIDE_PATH) - 2)
    local = scaled - segment
    start, end = INSIDE_PATH[segment:segment + 2]
    return tuple(a + local * (b - a) for a, b in zip(start, end))


def readout(plan):
    return sum((a * (s - q) for a, s, q in zip(NORMAL, plan, STAR)),
               Fraction(0))


def angle_data(plan):
    direction = tuple(s - q for s, q in zip(plan, STAR))
    if direction == (Fraction(0), Fraction(0)):
        return None
    product = sum((a * b for a, b in zip(NORMAL, direction)), Fraction(0))
    norm_a = hypot(float(NORMAL[0]), float(NORMAL[1]))
    norm_b = hypot(float(direction[0]), float(direction[1]))
    angle = degrees(acos(max(-1.0, min(1.0,
                                       float(product) / (norm_a * norm_b)))))
    theta_a = degrees(atan2(float(NORMAL[1]), float(NORMAL[0])))
    theta_b = degrees(atan2(float(direction[1]), float(direction[0])))
    delta = (theta_b - theta_a + 180) % 360 - 180
    return angle, theta_a, delta


def draw_region_and_walls(ax):
    boundary = ordered(mill.MILL)
    ax.fill([p[0] for p in boundary], [p[1] for p in boundary],
            color=PLAN, alpha=0.11, zorder=1, linewidth=0)
    for row, bound in zip(mill.MILL.A, mill.MILL.b):
        line_where(ax, row, bound, color=TEXT, linewidth=1.2, zorder=3)


def obtuse_gif():
    fig, ax = figure(8.2, 6.7)
    fig.subplots_adjust(left=0.1, right=0.96, top=0.81, bottom=0.19)
    note = margin_note(fig, y=0.02, size=8.6)

    def update(i):
        i = min(i, STAGES.total - 1)
        stage, progress = STAGES(i)
        amount = Fraction(str(progress))
        if stage == 0:
            plan = STAR
        elif stage == 1:
            plan = path_point(amount)
        else:
            plan = OUTSIDE
        final = stage == 2
        anchor_order, anchor_star, anchor_plan, walk_anchor = (
            obtuse_label_anchors(plan)
        )
        value = readout(plan)
        angles = angle_data(plan)

        ax.clear()
        draw_axes(ax)
        ax.set_ylim(0, 22)
        ax.set_yticks(range(0, 23, 4))
        draw_region_and_walls(ax)
        ax.plot([float(anchor_order[0])], [float(anchor_order[1])], "o",
                color=WARN, markeredgecolor=SURFACE, markeredgewidth=1.3,
                markersize=8, zorder=7)
        order_offset = (-12, 10) if final else (9, 10)
        ax.annotate("order x", xy=tuple(map(float, anchor_order)),
                    xytext=order_offset, textcoords="offset points",
                    color=WARN, fontsize=8.5,
                    ha="right" if final else "left", va="bottom",
                    bbox=dict(boxstyle="square,pad=0.14",
                              facecolor=SURFACE, edgecolor=WARN,
                              linewidth=0.5), zorder=9)
        ax.plot([float(anchor_star[0])], [float(anchor_star[1])], "o",
                color=PLAN, markeredgecolor=SURFACE, markeredgewidth=1.5,
                markersize=9, zorder=7)
        ax.annotate(f"s* = {display_point(anchor_star)}",
                    xy=tuple(map(float, anchor_star)),
                    xytext=(-8, -15), textcoords="offset points", color=PLAN,
                    fontsize=8.5, ha="right", va="top",
                    bbox=dict(boxstyle="square,pad=0.14",
                              facecolor=SURFACE, edgecolor="none"), zorder=9)

        if final:
            assert OUTSIDE_DISTANCE_SQUARED < STAR_DISTANCE_SQUARED
            ax.plot([float(anchor_star[0]), float(anchor_plan[0])],
                    [float(anchor_star[1]), float(anchor_plan[1])],
                    color=WARN, linewidth=1.4, linestyle=(0, (3, 3)),
                    zorder=5)
            ax.plot([float(anchor_plan[0])], [float(anchor_plan[1])], "o",
                    color=WARN, markeredgecolor=SURFACE, markeredgewidth=1.2,
                    markersize=8, zorder=8)
            ax.annotate(
                "", xy=tuple(map(float, walk_anchor)),
                xytext=tuple(map(float, anchor_star)),
                arrowprops=dict(arrowstyle="-|>", color=WARN, linewidth=1.2,
                                linestyle=(0, (3, 3))),
                zorder=6,
            )
            ax.plot([float(walk_anchor[0])], [float(walk_anchor[1])], "o",
                    color=WARN, markeredgecolor=SURFACE, markeredgewidth=1.2,
                    markersize=7, zorder=8)
            ax.annotate(
                "only possible outside S", xy=tuple(map(float, walk_anchor)),
                xytext=(-48, 13), textcoords="offset points", color=WARN,
                fontsize=8.3, ha="right", va="bottom",
                bbox=dict(boxstyle="square,pad=0.15", facecolor=SURFACE,
                          edgecolor=WARN, linewidth=0.5),
                arrowprops=dict(arrowstyle="-", color=WARN, linewidth=0.65),
                zorder=10,
            )
            ax.text(15.0, 11.2, "acute walk leaves the region",
                    color=WARN, fontsize=8.0, ha="left",
                    bbox=dict(boxstyle="square,pad=0.13",
                              facecolor=SURFACE, edgecolor="none"),
                    zorder=9)
            claim(ax, TITLE, "the first step toward s′ gets closer, but s′ is not a plan")
        else:
            if plan != STAR:
                ax.annotate("", xy=tuple(map(float, anchor_order)),
                            xytext=tuple(map(float, anchor_star)),
                            arrowprops=dict(arrowstyle="-|>", color=WARN,
                                            linewidth=1.25), zorder=5)
                ax.annotate("", xy=tuple(map(float, anchor_plan)),
                            xytext=tuple(map(float, anchor_star)),
                            arrowprops=dict(arrowstyle="-|>", color=PLAN,
                                            linewidth=1.55), zorder=6)
                ax.plot([float(anchor_plan[0])], [float(anchor_plan[1])], "o",
                        color=PLAN, markeredgecolor=SURFACE,
                        markeredgewidth=1.2, markersize=7.5, zorder=8)
                ax.annotate("s", xy=tuple(map(float, anchor_plan)),
                            xytext=(8, 8), textcoords="offset points",
                            color=PLAN, fontsize=8.8, ha="left", va="bottom",
                            bbox=dict(boxstyle="square,pad=0.12",
                                      facecolor=SURFACE, edgecolor="none"),
                            zorder=9)
                angle, theta_a, delta = angles
                theta_end = theta_a + delta
                ax.add_patch(Arc(tuple(map(float, STAR)), 3.1, 3.1,
                                 theta1=min(theta_a, theta_end),
                                 theta2=max(theta_a, theta_end),
                                 color=TEXT_DIM, linewidth=1.0, zorder=7))
                theta_mid = radians(theta_a + delta / 2)
                ax.text(float(STAR[0]) + 1.9 * cos(theta_mid),
                        float(STAR[1]) + 1.9 * sin(theta_mid),
                        f"{angle:.0f}°", color=TEXT_DIM, fontsize=8.0,
                        ha="center", va="center",
                        bbox=dict(boxstyle="square,pad=0.1",
                                  facecolor=SURFACE, edgecolor="none"),
                        zorder=9)
            else:
                ax.annotate("s = s*", xy=tuple(map(float, STAR)),
                            xytext=(10, -5), textcoords="offset points",
                            color=PLAN, fontsize=8.5, ha="left", va="top",
                            bbox=dict(boxstyle="square,pad=0.12",
                                      facecolor=SURFACE, edgecolor="none"),
                            zorder=9)
            subtitle = ("at s*, the dot product is zero"
                        if stage == 0 else
                        "for every other feasible s, the angle is obtuse")
            claim(ax, TITLE, subtitle)

        ax.plot([float(anchor_plan[0])], [float(anchor_plan[1])], "o",
                color=WARN if final else PLAN,
                markeredgecolor=SURFACE, markeredgewidth=1.2,
                markersize=7.5, zorder=8)
        if final:
            ax.annotate("s′", xy=tuple(map(float, anchor_plan)),
                        xytext=(9, -11), textcoords="offset points",
                        color=WARN, fontsize=8.8, ha="left", va="top",
                        bbox=dict(boxstyle="square,pad=0.12",
                                  facecolor=SURFACE, edgecolor="none"),
                        zorder=9)
        note.set_text(
            f"(x − s*)·(s − s*) = {product_formula()} = {value}"
            + (f"   angle {angles[0]:.0f}°"
               if angles is not None else "   s = s*: zero direction")
        )
        return []

    animate(fig, update, STAGES.total, OUT / "obtuse.gif", fps=12, hold=3.0)


if __name__ == "__main__":
    obtuse_gif()
