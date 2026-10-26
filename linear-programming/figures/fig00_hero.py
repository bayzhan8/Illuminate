"""Chapter 0: the walk the simplex method takes at the mill, corner to corner.

Staged: each leg is one pivot, a running log records every corner reached, and
the readout shows which walls are hit at every moment.
"""

from illuminate.draw import OK, PLAN, TEXT_DIM, animate, chapter_dir, figure, margin_note, tag
from linprog import mill as f
from scene import Stages, claim, draw_axes, draw_region, draw_wall, mark, roubles

OUT = chapter_dir("00-what-this-is")
C = [tuple(float(v) for v in p) for p in f.WALK.corners]
TITLE = "the simplex method walks from corner to corner, always uphill"
SUBS = ["start at the corner with nothing made",
        "step 1 · make 5-ply until the lathe hours run out",
        "step 2 · trade 5-ply for 3-ply until the press hours run out too"]
END = "no neighbouring corner has more value, so the walk stops here"
STAGES = Stages((0, 12), (18, 12), (18, 0))


def hero_gif():
    fig, ax = figure(7.0, 6.4)
    fig.subplots_adjust(left=0.1, right=0.97, top=0.86, bottom=0.17)
    note = margin_note(fig, y=0.02, size=9.5)
    frames = STAGES.total
    (ta, fa), (pa, pb) = ((float(v) for v in r) for r in f.MILL.A)
    T, P = (float(v) for v in f.MILL.b)

    def update(i):
        i = min(i, frames - 1)
        done = i == frames - 1
        k, s = STAGES(i)
        if done:
            s = 1.0
        ax.clear()
        draw_axes(ax)
        draw_wall(ax, 0, "lathe wall", at=18.5, color=TEXT_DIM)
        draw_wall(ax, 1, "press wall", at=4.5, color=TEXT_DIM)
        draw_region(ax)
        leg, t = (max(k - 1, 0), s if k else 0.0)
        a, b = C[leg], C[leg + 1]
        here = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
        trail = C[:leg + 1] + [here]
        ax.plot([p[0] for p in trail], [p[1] for p in trail], color=PLAN, lw=2.6, zorder=6)
        reached = leg + (1 if k and s >= 1 else 0)
        log = ["corners reached"]
        for j in range(reached + 1):
            v = f.MILL.value(f.WALK.corners[j])
            mark(ax, C[j], size=8)
            log.append(f"({C[j][0]:g}, {C[j][1]:g})  {roubles(v)}")
        tag(ax, 12.6, 17.9, "\n".join(log), color=PLAN, size=9.5, va="top")
        mark(ax, here, size=11)
        claim(ax, TITLE, END if done else SUBS[k])
        if done:
            tag(ax, 12.6, 13.6, "stop: best plan found", color=OK, size=9.5, va="top")
        t, five = here
        note.set_text(f"3-ply {t:4.1f}  5-ply {five:4.1f}    lathe hours {ta * t + fa * five:4.1f} of {T:g}"
                      f"    press hours {pa * t + pb * five:4.1f} of {P:g}\n"
                      f"value 3 × {t:4.1f} + 5 × {five:4.1f} = {roubles(3 * t + 5 * five)}")
        return []

    animate(fig, update, frames, OUT / "walk.gif", fps=12, hold=3.5)


if __name__ == "__main__":
    hero_gif()
