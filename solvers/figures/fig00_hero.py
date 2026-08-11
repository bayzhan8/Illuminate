"""Chapter 0: the poster. The model shrinking, round by round, before anything
is solved.

Columns are grouped by product and rows by the constraints belonging to it, so
the blocks are visible. Product C is the one nobody ordered, and watching its
whole block go out at once is most of the chapter.
"""

from matplotlib.patches import Rectangle

from illuminate.draw import (HAIRLINE, PLAN, SURFACE, TEXT, TEXT_DIM,
                             TEXT_FAINT, animate, chapter_dir, figure, heading,
                             margin_note)
from solvers import library as L
from solvers.presolve import presolve

OUT = chapter_dir("00-what-this-is")

MODEL = L.SMALL
ROUNDS = L.SMALL_PRESOLVED.rounds
COLS_PER_PRODUCT = 7          # make x2, hold x3, open x2
ROWS_PER_PRODUCT = 6          # start, end, and a balance and link per period


def _survivors():
    return [(set(p.kept_rows), set(p.kept_cols))
            for p in (presolve(MODEL, stop_after=k) for k in range(ROUNDS + 1))]


def hero_gif(fps=6):
    cells = {(i, j) for i, row in enumerate(MODEL.rows) for j, _ in row.coefs}
    stages = _survivors()
    shapes = [presolve(MODEL, stop_after=k).after for k in range(ROUNDS + 1)]
    n_rows, n_cols = MODEL.n_rows, MODEL.n_cols

    fig, ax = figure(7.0, 5.9)
    fig.subplots_adjust(left=0.10, right=0.97, bottom=0.16, top=0.80)
    heading(ax, "one model, before any algorithm is allowed to run")

    ax.set_xlim(-0.5, n_cols + 0.5)
    ax.set_ylim(n_rows + 2.2, -1.5)            # first row at the top
    ax.set_aspect("equal")
    ax.axis("off")

    # the lattice, so the empty places read as empty rather than as absent
    for j in range(n_cols + 1):
        ax.plot([j - 0.07, j - 0.07], [-0.07, n_rows - 0.07], color=HAIRLINE,
                linewidth=0.35, alpha=0.5, zorder=1)
    for i in range(n_rows + 1):
        ax.plot([-0.07, n_cols - 0.07], [i - 0.07, i - 0.07], color=HAIRLINE,
                linewidth=0.35, alpha=0.5, zorder=1)

    # product blocks, and the two capacity rows that belong to no product
    for k, name in enumerate(L.PRODUCTS):
        x0 = k * COLS_PER_PRODUCT
        ax.plot([x0 - 0.07, x0 - 0.07], [-0.07, n_rows - 0.07], color=TEXT_FAINT,
                linewidth=0.9, alpha=0.65, zorder=2)
        ax.text(x0 + COLS_PER_PRODUCT / 2 - 0.6, -0.9, name, fontsize=11,
                color=TEXT_DIM, ha="center", va="bottom")
        y0 = k * ROWS_PER_PRODUCT
        ax.plot([-0.07, n_cols - 0.07], [y0 - 0.07, y0 - 0.07], color=TEXT_FAINT,
                linewidth=0.9, alpha=0.65, zorder=2)
    ax.text(n_cols / 2 - 0.6, n_rows + 1.4, "columns, grouped by product",
            fontsize=9.5, color=TEXT_FAINT, ha="center", va="center")

    patches = {}
    for (i, j) in cells:
        r = Rectangle((j - 0.42, i - 0.42), 0.72, 0.72, linewidth=0, zorder=4)
        ax.add_patch(r)
        patches[(i, j)] = r

    note = margin_note(fig, x=0.10, y=0.045, size=10.5)

    def update(k):
        k = min(k, ROUNDS)
        live_rows, live_cols = stages[k]
        for (i, j), patch in patches.items():
            alive = i in live_rows and j in live_cols
            patch.set_facecolor(PLAN if alive else HAIRLINE)
            patch.set_alpha(1.0 if alive else 0.30)
        rows, cols, nz = shapes[k]
        head = "as written" if k == 0 else f"after round {k}"
        note.set_text(f"{head}     {rows} rows   {cols} columns   {nz} nonzeros")
        note.set_color(TEXT if k == 0 else TEXT_DIM)
        return []

    animate(fig, update, ROUNDS + 1, OUT / "hero.gif", fps=fps, hold=3.6)


if __name__ == "__main__":
    hero_gif()
