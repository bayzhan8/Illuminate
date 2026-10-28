"""The largest complete-set order is ten batches of each sheet."""

from illuminate.draw import (PLAN, PLAN_FILL, SURFACE, TEXT_DIM, WARN, animate, chapter_dir,
                             figure, margin_note)
from linprog import mill as f
from scene import WINDOW, WINDOW_POLY, Stages, claim, clip, draw_axes, draw_region, fill

OUT = chapter_dir("03-writing-it-down")
LATHE = f.MILL.A[0]
PRESS = f.MILL.A[1]
LATHE_HOURS = float(f.MILL.b[0])
PRESS_HOURS = float(f.MILL.b[1])
X_MAX, Y_MAX = WINDOW[1], WINDOW[3]
STAGES = Stages((24, 12), (24, 12), (12, 12), (12, 18))
TITLE = "the most complete sets is 10"
SUBS = (
    "raise the required number of complete sets from 0 to 5",
    "raise it from 5 to 10: the press wall is next",
    "11 sets: the tip (11, 11) needs 22 press hours",
    "",
)
FINAL = "10 complete sets, at 10 batches of each"


def one_decimal(value):
    return f"{value:.1f}".removesuffix(".0")


def quadrant(z):
    poly = clip(WINDOW_POLY, (1, 0), z, keep_le=False)
    return clip(poly, (0, 1), z, keep_le=False)


def sets_gif():
    fig, ax = figure(7.0, 6.6)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.85, bottom=0.18)
    note = margin_note(fig, y=0.025, size=9.2)
    frames = STAGES.total

    def update(i):
        i = min(i, frames - 1)
        stage, s = STAGES(i)
        if i == frames - 1:
            s = 1.0
        if stage == 0:
            z = 5 * s
        elif stage == 1:
            z = 5 + 5 * s
        elif stage == 2:
            z = 10 + s
        else:
            z = 11 - s
        warning = z > 10
        color = WARN if warning else PLAN

        ax.clear()
        draw_axes(ax)
        draw_region(ax, alpha=0.11)
        ax.plot([0, min(X_MAX, Y_MAX)], [0, min(X_MAX, Y_MAX)],
                color=TEXT_DIM, linewidth=1.0, dashes=(4, 3), zorder=2)
        ax.text(15.4, 15.8, "t = f", color=TEXT_DIM, fontsize=9,
                ha="left", va="bottom", zorder=6,
                bbox=dict(boxstyle="square,pad=0.16", facecolor=SURFACE,
                          edgecolor="none"))

        fill(ax, quadrant(z), PLAN_FILL if not warning else WARN, 0.14 if not warning else 0.12,
             z=1.8)
        ax.plot([z, X_MAX], [z, z], color=color, linewidth=2.0, zorder=4)
        ax.plot([z, z], [z, Y_MAX], color=color, linewidth=2.0, zorder=4)
        ax.plot([z], [z], "o", color=color, markeredgecolor=SURFACE,
                markeredgewidth=1.5, markersize=8.5, zorder=7)

        if i == frames - 1:
            claim(ax, TITLE)
            ax.text(0, 1.025, FINAL, transform=ax.transAxes, fontsize=8.8,
                    color=TEXT_DIM, ha="left", va="bottom")
        else:
            claim(ax, TITLE, SUBS[stage])
        lathe_at_tip = float(sum(LATHE)) * z
        press_at_tip = float(sum(PRESS)) * z
        note.set_text(
            f"z = {one_decimal(z)}   lathe at (z, z): 3z = {one_decimal(lathe_at_tip)} "
            f"of {LATHE_HOURS:g}   press: 2z = {one_decimal(press_at_tip)} "
            f"of {PRESS_HOURS:g}"
        )
        return []

    animate(fig, update, frames, OUT / "sets.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    sets_gif()
