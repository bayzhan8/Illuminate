"""Chapter 0: the walk the simplex method takes on the farm, corner to corner.

Animated because the walk is the thing being promised: three stops, each worth
more than the last, ending where nothing nearby is better.
"""

from illuminate.draw import PLAN, TEXT_DIM, animate, chapter_dir, figure, margin_note
from linprog import farm as f
from scene import draw_axes, draw_region, draw_wall, heading, mark

OUT = chapter_dir("00-what-this-is")
STEPS = [tuple(float(v) for v in p) for p in f.WALK.corners]
PER_LEG = 14


def hero_gif():
    fig, ax = figure(7.6, 5.0)
    fig.subplots_adjust(left=0.1, right=0.98, top=0.9, bottom=0.2)
    note = margin_note(fig, y=0.02)
    legs = len(STEPS) - 1
    frames = legs * PER_LEG + 1

    def update(i):
        i = min(i, frames - 1)
        ax.clear()
        draw_axes(ax)
        heading(ax, "walking the edges of the farm, uphill")
        draw_wall(ax, 0, "water runs out", at=18.5, color=TEXT_DIM)
        draw_wall(ax, 1, "land runs out", at=4.5, color=TEXT_DIM)
        draw_region(ax)
        leg, t = divmod(i, PER_LEG)
        if leg >= legs:
            leg, t = legs - 1, PER_LEG
        s = t / PER_LEG
        s = s * s * (3 - 2 * s)
        (x0, y0), (x1, y1) = STEPS[leg], STEPS[leg + 1]
        here = (x0 + s * (x1 - x0), y0 + s * (y1 - y0))
        done = STEPS[:leg + 1] + [here]
        ax.plot([p[0] for p in done], [p[1] for p in done], color=PLAN, lw=2.6, zorder=6)
        for k, p in enumerate(STEPS[:leg + 1 + (s == 1)]):
            mark(ax, p, f.money(f.FARM.value(f.WALK.corners[k])), size=8,
                 dx=0.5, dy=0.6 if k < 2 else 0.4)
        mark(ax, here, size=11)
        note.set_text(f"{here[0]:4.1f} acres wheat, {here[1]:4.1f} acres corn")
        return []

    animate(fig, update, frames, OUT / "walk.gif", fps=12, hold=3.0)


if __name__ == "__main__":
    hero_gif()
