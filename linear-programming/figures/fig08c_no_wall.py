"""Neither convexity nor closedness can be dropped from separation."""

from fractions import Fraction

from illuminate.draw import (PLAN, SURFACE, TEXT, TEXT_DIM, WARN,
                             chapter_dir, figure, save)
from linprog import mill as mill
from linprog.lp import LP, vertices

if __package__:
    from .scene import WINDOW, draw_axes, line_where, ordered
else:
    from scene import WINDOW, draw_axes, line_where, ordered

OUT = chapter_dir("08-separation")
CAP_LP = LP.build((0, 0), mill.MILL.A + ((0, -1),),
                  mill.MILL.b + (Fraction(-14),))
CAP_CORNERS = vertices(CAP_LP)
LOW_ENDPOINT = next(p for p in vertices(mill.MILL)
                    if p[1] == 0 and p[0] > 0)
HIGH_ENDPOINT = next(p for p in CAP_CORNERS
                     if p[1] == 14 and p[0] > 0)
ENDPOINTS = (LOW_ENDPOINT, HIGH_ENDPOINT)
MIDPOINT = tuple((a + b) / 2 for a, b in zip(*ENDPOINTS))
TRIAL_NORMALS = ((Fraction(1), Fraction(0)),
                 (Fraction(0), Fraction(1)),
                 (Fraction(1), Fraction(1)))
MISSING_EDGE_ROW = mill.MILL.A[1]
MISSING_EDGE_BOUND = mill.MILL.b[1]
EQUAL_COORDINATE = MISSING_EDGE_BOUND / sum(MISSING_EDGE_ROW)
MISSING_EDGE_POINT = (EQUAL_COORDINATE, EQUAL_COORDINATE)


def display(value):
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{float(value):.2f}".rstrip("0").rstrip(".")


def display_point(point):
    return f"({display(point[0])}, {display(point[1])})"


def dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def trial_wall_label_anchors():
    anchors = []
    for normal in TRIAL_NORMALS:
        level = dot(normal, MIDPOINT)
        if normal[1] == 0:
            anchors.append((level / normal[0],
                            Fraction(str(WINDOW[3])) - Fraction(3, 2)))
        elif normal[0] == 0:
            anchors.append((Fraction(str(WINDOW[1])) - 2,
                            level / normal[1]))
        else:
            t = Fraction(2)
            anchors.append((t, (level - normal[0] * t) / normal[1]))
    return tuple(anchors)


def trial_wrong_endpoint(normal):
    midpoint_value = dot(normal, MIDPOINT)
    return min(ENDPOINTS, key=lambda point: dot(normal, point) - midpoint_value)


def open_press_label_anchor():
    t = 8 * MISSING_EDGE_POINT[0] / 5
    f = ((MISSING_EDGE_BOUND - MISSING_EDGE_ROW[0] * t)
         / MISSING_EDGE_ROW[1])
    return t, f


def approach_points():
    return tuple((MISSING_EDGE_POINT[0] - Fraction(1, 10 ** k),) * 2
                 for k in (1, 2, 3))


def panel_heading(ax, title, subtitle):
    ax.text(0, 1.085, title, transform=ax.transAxes, fontsize=9.3,
            color=TEXT, ha="left", va="bottom", fontweight="semibold")
    ax.text(0, 1.025, subtitle, transform=ax.transAxes, fontsize=8.2,
            color=TEXT_DIM, ha="left", va="bottom")


def draw_trial_wall(ax, normal, anchor, index):
    level = dot(normal, MIDPOINT)
    x0, x1 = map(Fraction, WINDOW[:2])
    y0, y1 = map(Fraction, WINDOW[2:])
    if normal[1] == 0:
        xs = (level / normal[0], level / normal[0])
        ys = (y0, y1)
    else:
        xs = (x0, x1)
        ys = tuple((level - normal[0] * x) / normal[1] for x in xs)
    ax.plot([float(x) for x in xs], [float(y) for y in ys],
            color=TEXT_DIM, linewidth=0.9, linestyle=((0, (3, 2)),
                                                       (0, (5, 2, 1, 2)),
                                                       (0, (1, 2)))[index],
            alpha=0.82, zorder=2)
    ax.annotate(
        f"trial {index + 1}", xy=tuple(map(float, anchor)),
        xytext=(5, 4), textcoords="offset points", color=TEXT_DIM,
        fontsize=7.1, ha="left", va="bottom",
        bbox=dict(boxstyle="square,pad=0.11", facecolor=SURFACE,
                  edgecolor="none"),
        zorder=8,
    )


def no_wall_figure():
    fig, ax = figure(11.6, 6.0)
    fig.delaxes(ax)
    left = fig.add_subplot(1, 2, 1)
    right = fig.add_subplot(1, 2, 2)
    fig.subplots_adjust(left=0.07, right=0.98, top=0.8, bottom=0.17,
                        wspace=0.32)
    for panel in (left, right):
        draw_axes(panel)

    panel_heading(left, "NOT CONVEX",
                  "the midpoint of two allowed plans is missing")
    left.plot([0, float(LOW_ENDPOINT[0])], [0, 0], color=PLAN,
              linewidth=4.0,
              solid_capstyle="round", zorder=4)
    cap = ordered(CAP_LP)
    left.fill([p[0] for p in cap], [p[1] for p in cap],
              color=PLAN, alpha=0.16, zorder=2)
    left.plot([p[0] for p in cap] + [cap[0][0]],
              [p[1] for p in cap] + [cap[0][1]],
              color=PLAN, linewidth=1.6, zorder=4)
    a, b = ENDPOINTS
    left.plot([float(a[0]), float(b[0])], [float(a[1]), float(b[1])],
              color=TEXT_DIM, linewidth=1.0, linestyle=(0, (4, 3)),
              zorder=3)
    for point, label, offset in (
        (a, display_point(a), (-2, 10)),
        (b, display_point(b), (7, 8)),
    ):
        left.plot([float(point[0])], [float(point[1])], "o", color=PLAN,
                  markeredgecolor=SURFACE, markeredgewidth=1.3,
                  markersize=7.5, zorder=6)
        left.annotate(label, xy=tuple(map(float, point)), xytext=offset,
                      textcoords="offset points", color=PLAN, fontsize=8.0,
                      ha="left" if offset[0] >= 0 else "right",
                      va="bottom",
                      bbox=dict(boxstyle="square,pad=0.12",
                                facecolor=SURFACE, edgecolor="none"),
                      zorder=8)
    left.plot([float(MIDPOINT[0])], [float(MIDPOINT[1])], "o", color=WARN,
              markeredgecolor=SURFACE, markeredgewidth=1.4,
              markersize=8.0, zorder=8)
    left.annotate(f"{display_point(MIDPOINT)}: midpoint",
                  xy=tuple(map(float, MIDPOINT)),
                  xytext=(8, -13), textcoords="offset points", color=WARN,
                  fontsize=8.0, ha="left", va="top",
                  bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                            edgecolor=WARN, linewidth=0.45), zorder=9)
    anchors = trial_wall_label_anchors()
    for index, (normal, anchor) in enumerate(zip(TRIAL_NORMALS, anchors)):
        draw_trial_wall(left, normal, anchor, index)
        wrong = trial_wrong_endpoint(normal)
        left.plot([float(wrong[0])], [float(wrong[1])], "x",
                  color=WARN, markersize=10, markeredgewidth=2.2, zorder=10)
    left.text(0.5, 18.05, "amber crosses: a plan on the wrong side",
              fontsize=7.3, color=WARN, ha="left",
              bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                        edgecolor="none"), zorder=9)
    left.text(0.5, 15.4, f"allowed: f ≥ {display(-CAP_LP.b[-1])}",
              fontsize=7.4, color=PLAN, ha="left",
              bbox=dict(boxstyle="square,pad=0.12", facecolor=SURFACE,
                        edgecolor="none"), zorder=8)
    left.text(1.0, 0.7, "allowed: f = 0", fontsize=7.4, color=PLAN,
              ha="left", bbox=dict(boxstyle="square,pad=0.12",
                                   facecolor=SURFACE, edgecolor="none"),
              zorder=8)
    left.text(0.02, -0.22, "not convex: the midpoint cannot be cut off",
              transform=left.transAxes, fontsize=8.6, color=TEXT,
              ha="left", va="top")

    panel_heading(right, "NOT CLOSED",
                  "the press edge is left out; plans approach it")
    boundary = ordered(mill.MILL)
    right.fill([p[0] for p in boundary], [p[1] for p in boundary],
               color=PLAN, alpha=0.10, zorder=1)
    line_where(right, mill.MILL.A[0], mill.MILL.b[0],
               color=TEXT, linewidth=1.2, zorder=4)
    line_where(right, mill.MILL.A[1], mill.MILL.b[1],
               color=TEXT_DIM, linewidth=1.35, dashes=(4, 3), zorder=5)
    press_anchor = open_press_label_anchor()
    right.annotate(
        "press edge missing", xy=tuple(map(float, press_anchor)),
        xytext=(8, 8), textcoords="offset points", color=TEXT_DIM,
        fontsize=7.6, ha="left", va="bottom",
        bbox=dict(boxstyle="square,pad=0.13", facecolor=SURFACE,
                  edgecolor=TEXT_DIM, linewidth=0.45),
        arrowprops=dict(arrowstyle="-", color=TEXT_DIM, linewidth=0.55),
        zorder=8,
    )
    order = MISSING_EDGE_POINT
    right.plot([float(order[0])], [float(order[1])], "o", color=WARN,
               markeredgecolor=SURFACE, markeredgewidth=1.4,
               markersize=8.5, zorder=9)
    right.annotate(display_point(order), xy=tuple(map(float, order)),
                   xytext=(-11, 11), textcoords="offset points",
                   color=WARN, fontsize=8.0, ha="right", va="bottom",
                   bbox=dict(boxstyle="square,pad=0.13", facecolor=SURFACE,
                             edgecolor=WARN, linewidth=0.45), zorder=10)
    approaches = approach_points()
    for point in approaches:
        right.plot([float(point[0])], [float(point[1])], "o", color=PLAN,
                   markeredgecolor=SURFACE, markeredgewidth=0.8,
                   markersize=5.5, zorder=9)
    right.annotate(
        f"s1 = {display_point(approaches[0])}  →  "
        f"s2 = {display_point(approaches[1])}  →  …",
        xy=tuple(map(float, approaches[0])), xytext=(-2, -45),
        textcoords="offset points", color=PLAN, fontsize=6.8,
        ha="left", va="top",
        bbox=dict(boxstyle="square,pad=0.16", facecolor=SURFACE,
                  edgecolor=PLAN, linewidth=0.45),
        arrowprops=dict(arrowstyle="-", color=PLAN, linewidth=0.6),
        zorder=10,
    )
    inset = right.inset_axes([0.53, 0.55, 0.42, 0.39])
    inset.set_facecolor(SURFACE)
    inset_low = float(order[0]) - 0.14
    inset_high = float(order[0]) + 0.015
    inset.set_xlim(inset_low, inset_high)
    inset.set_ylim(inset_low, inset_high)
    inset.plot([inset_low, inset_high],
               [(float(MISSING_EDGE_BOUND) - float(MISSING_EDGE_ROW[0]) * x)
                / float(MISSING_EDGE_ROW[1])
                for x in (inset_low, inset_high)],
               color=TEXT_DIM,
               linestyle=(0, (3, 2)), linewidth=0.8, clip_on=True)
    for point in approaches:
        inset.plot([float(point[0])], [float(point[1])], "o", color=PLAN,
                   markeredgecolor=SURFACE, markeredgewidth=0.6,
                   markersize=5.0, zorder=4)
    inset.plot([float(order[0])], [float(order[1])], "o", color=WARN,
               markeredgecolor=SURFACE, markeredgewidth=0.6,
               markersize=5.5, zorder=5)
    inset.set_xticks((float(approaches[0][0]), float(order[0])),
                     (display(approaches[0][0]), display(order[0])))
    inset.set_yticks((float(approaches[0][1]), float(order[1])),
                     (display(approaches[0][1]), display(order[1])))
    inset.tick_params(labelsize=6.0, colors=TEXT_DIM, length=2)
    for spine in inset.spines.values():
        spine.set_color(TEXT_DIM)
        spine.set_linewidth(0.6)
    inset.set_title(f"zoom: s_n → {display_point(order)}", fontsize=6.8,
                    color=TEXT_DIM, pad=2)
    right.text(0.02, -0.22, "not closed: no nearest point, no strict wall",
               transform=right.transAxes, fontsize=8.6, color=TEXT,
               ha="left", va="top")

    save(fig, OUT / "no_wall.png", tight=False)


if __name__ == "__main__":
    no_wall_figure()
