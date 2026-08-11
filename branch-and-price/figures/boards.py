"""Drawing a board and the cuts taken out of it.

A pattern is a way of slicing one board, so the honest picture of a pattern is
a board with the slices marked on it.  Several chapters draw the same thing, so
it lives here.

Pieces are shaded by width rather than coloured by width: the guide's two
colours already mean "plan" and "price" everywhere else, and inventing a third
and fourth hue for item types would quietly break that. Each piece carries its
width as a number instead, which is what the reader actually needs to read.
"""

from __future__ import annotations

from illuminate.draw import TEXT, TEXT_DIM, TEXT_FAINT, SURFACE, PLAN, PRICE, HAIRLINE

# The shades run light to dark with the piece width, so a wide piece looks
# heavier than a narrow one and the eye can sort a pattern without a legend.
SHADES = ["#dfe6f0", "#b9c9e0", "#8fa8cd", "#5f80b4"]


def shade_for(width: int, widths) -> str:
    order = sorted(widths)
    return SHADES[min(order.index(width), len(SHADES) - 1)]


def draw_board(ax, y, pattern, inst, height=0.62, label=None, show_waste=True,
               dim=False, number_pieces=True):
    """One board at height *y*, with its cuts, drawn in the instance's units."""
    x = 0.0
    for i, count in enumerate(pattern):
        width = inst.widths[i]
        for _ in range(count):
            ax.add_patch(_piece(x, y, width, height,
                                shade_for(width, inst.widths), dim))
            if number_pieces and width >= 4:
                ax.text(x + width / 2, y + height / 2, str(width),
                        ha="center", va="center", fontsize=8.5,
                        color=TEXT_FAINT if dim else TEXT,
                        alpha=0.5 if dim else 1.0, zorder=6)
            x += width
    waste = inst.width - x
    if show_waste and waste > 0:
        ax.add_patch(_piece(x, y, waste, height, SURFACE, dim, hatch="////"))
        if waste >= 4:
            ax.text(x + waste / 2, y + height / 2, "waste", ha="center",
                    va="center", fontsize=7.5, color=TEXT_FAINT, zorder=6)
    if label:
        ax.text(-0.9, y + height / 2, label, ha="right", va="center",
                fontsize=9.5, color=TEXT_FAINT if dim else TEXT_DIM, zorder=6)
    return waste


def _piece(x, y, width, height, colour, dim, hatch=None):
    from matplotlib.patches import Rectangle
    return Rectangle((x, y), width, height, facecolor=colour,
                     edgecolor=TEXT_FAINT if dim else TEXT,
                     linewidth=0.9, alpha=0.45 if dim else 1.0,
                     hatch=hatch, zorder=4)


def board_axes(ax, inst, rows, row_gap=1.0, left=-0.9):
    ax.set_xlim(left - 7.5, inst.width + 1.2)
    ax.set_ylim(-0.45, rows * row_gap + 0.15)
    ax.set_xticks([])
    ax.set_yticks([])
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    return ax
