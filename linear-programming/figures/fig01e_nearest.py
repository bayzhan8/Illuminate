"""The perpendicular foot is the nearest point on a wall."""

from fractions import Fraction

from illuminate.draw import PLAN, TEXT, TEXT_DIM, WARN, animate, chapter_dir, figure, margin_note
from linprog import mill as f
from linprog.lp import solve_square
from scene import Stages, claim, draw_axes, mark, right_angle, unit

OUT = chapter_dir("01-inside-the-walls")
A = f.MILL.A[0]
B = f.MILL.b[0]
X = (Fraction(6), Fraction(14))
G = sum((u * v for u, v in zip(A, X)), Fraction(0)) - B
AA = sum((u * u for u in A), Fraction(0))
Y_STAR = tuple(X[i] - G * A[i] / AA for i in range(2))
Y_FIVE = solve_square([A, (Fraction(1), Fraction(0))], [B, 0])
Y_THREE = solve_square([A, (Fraction(0), Fraction(1))], [B, 0])
STAGES = Stages((38, 10), (32, 10), (38, 12))
SUBS = ["from all 5-ply towards all 3-ply: the distance falls",
        "past the nearest point: the distance grows again",
        "return to the minimum and hold at a right angle"]
TITLE = "the perpendicular point is nearest to the wall"


def nearest_gif():
    fig, ax = figure(7.2, 6.4)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.84, bottom=0.18)
    note = margin_note(fig, y=0.025, size=9.5)
    frames = STAGES.total
    x = tuple(float(v) for v in X)
    y0 = tuple(float(v) for v in Y_FIVE)
    y1 = tuple(float(v) for v in Y_THREE)
    ys = tuple(float(v) for v in Y_STAR)
    a = tuple(float(v) for v in A)
    b = float(B)

    def update(i):
        i = min(i, frames - 1)
        k, s = STAGES(i)
        if i == frames - 1:
            s = 1.0
        if k == 0:
            y = tuple(y0[j] + s * (ys[j] - y0[j]) for j in range(2))
        elif k == 1:
            y = tuple(ys[j] + s * (y1[j] - ys[j]) for j in range(2))
        else:
            y = tuple(y1[j] + s * (ys[j] - y1[j]) for j in range(2))

        ax.clear()
        draw_axes(ax)
        ax.set_xlim(-1, 34)
        ax.set_ylim(-1, 19)
        ax.set_xticks(range(0, 35, 8))
        ax.set_yticks(range(0, 20, 4))
        wall_x = (-1.0, 34.0)
        ax.plot(wall_x, [(b - a[0] * t) / a[1] for t in wall_x],
                color=TEXT, lw=1.6, zorder=2)
        ax.text(15.5, (b - a[0] * 15.5) / a[1] + 0.55, "lathe wall",
                color=TEXT, fontsize=9.5, ha="center", zorder=6,
                bbox=dict(boxstyle="square,pad=0.2", facecolor="#fffff8",
                          edgecolor="none"))
        ax.plot([x[0], y[0]], [x[1], y[1]], color=TEXT_DIM, lw=1.2,
                dashes=(4, 3), zorder=4)
        mark(ax, x, "x = (6, 14)", color=WARN, size=10, dx=0.6, dy=0.6)
        mark(ax, y0, "all 5-ply", size=8.5, dx=0.55, dy=0.6)
        mark(ax, y1, "all 3-ply", size=8.5, dx=-0.55, dy=0.65, ha="right")
        mark(ax, y, "y", size=8.5, dx=0.45, dy=-0.65)

        at_nearest = abs(y[0] - ys[0]) < 0.02 and abs(y[1] - ys[1]) < 0.02
        if at_nearest:
            right_angle(ax, y, unit((x[0] - y[0], x[1] - y[1])),
                        unit((y1[0] - y0[0], y1[1] - y0[1])), s=0.45)
            ax.text(y[0] - 0.7, y[1] - 0.65, "(5.6, 13.2)", color=PLAN,
                    fontsize=9.2, ha="right", va="top", zorder=8)
        distance = ((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2) ** 0.5
        claim(ax, TITLE, "the point y slides along the lathe wall" if k == 0
              else SUBS[k])
        note.set_text(f"distance from x to y = {distance:.2f} batches\n"
                      f"minimum = 2 ÷ √5 ≈ {2 / float(AA) ** 0.5:.2f} batches")
        return []

    animate(fig, update, frames, OUT / "nearest.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    nearest_gif()
