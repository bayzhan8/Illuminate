"""A best plan on an edge can slide to a corner without losing value."""

from fractions import Fraction

from illuminate.draw import PLAN, TEXT, TEXT_DIM, animate, chapter_dir, figure, margin_note
from linprog import mill as f
from scene import Stages, arrow, claim, draw_axes, draw_region, draw_wall, mark

OUT = chapter_dir("02-best-is-a-corner")
C = (Fraction(1), Fraction(1))
D = (Fraction(1), Fraction(-1))
END_PLUS = max(f.CORNERS, key=lambda p: p[0])
END_MINUS = f.BEST
START = tuple((END_PLUS[i] + END_MINUS[i]) / 2 for i in range(2))
LATHE_RATE = sum((a * d for a, d in zip(f.MILL.A[0], tuple(-v for v in D))),
                 Fraction(0))
S_TO_LATHE = f.MILL.slack(0, START) / LATHE_RATE
MID = tuple(START[i] - S_TO_LATHE * D[i] for i in range(2))
VALUE = sum((c * x for c, x in zip(C, START)), Fraction(0))
STAGES = Stages((0, 12), (36, 12), (48, 14))
SUBS = ["±d along the press wall: press change 0, value change 0",
        "slide to (8, 12): lathe hours 26 → 32, value stays 20,000 roubles",
        "continue along the edge to (20, 0)"]
TITLE = "an edge-best plan can slide to a best corner"
FINAL = "a best plan that is not a corner slides, without losing value, to one that is."


def slide_gif():
    fig, ax = figure(7.2, 6.4)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.84, bottom=0.19)
    note = margin_note(fig, y=0.025, size=9.5)
    frames = STAGES.total
    start = tuple(float(v) for v in START)
    minus = tuple(float(v) for v in MID)
    plus = tuple(float(v) for v in END_PLUS)
    d = tuple(float(v) for v in D)
    value = float(VALUE)

    def update(i):
        i = min(i, frames - 1)
        k, s = STAGES(i)
        if i == frames - 1:
            s = 1.0
        if k == 0:
            point = start
        elif k == 1:
            point = tuple(start[j] + s * (minus[j] - start[j]) for j in range(2))
        else:
            point = tuple(minus[j] + s * (plus[j] - minus[j]) for j in range(2))

        ax.clear()
        draw_axes(ax)
        ax.set_xlim(-1, 23)
        ax.set_ylim(-1, 19)
        draw_region(ax)
        draw_wall(ax, 0, "lathe wall", at=3, color=TEXT_DIM)
        draw_wall(ax, 1, "press wall", at=3.5, color=TEXT_DIM)
        if k == 0:
            arrow(ax, start, (2 * d[0], 2 * d[1]), TEXT, "+d", dx=0.2, dy=-0.45)
            arrow(ax, start, (-2 * d[0], -2 * d[1]), TEXT, "−d",
                  dx=-0.35, dy=0.35, ha="right")
        else:
            ax.plot([start[0], point[0]], [start[1], point[1]], color=PLAN,
                    lw=2.0, alpha=0.55, zorder=5)
            ax.plot([minus[0], plus[0]], [minus[1], plus[1]], color=TEXT_DIM,
                    lw=1.1, dashes=(3, 3), zorder=4)
        mark(ax, point, "(14, 6)" if k == 0 else "moving best plan",
             size=9.5, dx=0.42, dy=0.55)
        if k >= 1:
            mark(ax, minus, "(8, 12)", size=8, dx=-1.2, dy=-1.0, ha="right")
        if k >= 2:
            mark(ax, plus, "(20, 0)", size=8, dx=-1.8, dy=1.2, ha="right")
        if i == frames - 1:
            claim(ax, TITLE)
            ax.text(0, 1.025, FINAL, transform=ax.transAxes, fontsize=8.0,
                    color=TEXT_DIM, ha="left", va="bottom")
        else:
            claim(ax, TITLE, SUBS[k])
        lathe = float(sum((a * point[j] for j, a in enumerate(f.MILL.A[0])),
                          Fraction(0)))
        note.set_text(f"press change along d = 0   value change along d = 0\n"
                      f"lathe hours at moving plan = {lathe:.1f}   value = "
                      f"{value * 1000:,.0f} roubles")
        return []

    animate(fig, update, frames, OUT / "slide.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    slide_gif()
