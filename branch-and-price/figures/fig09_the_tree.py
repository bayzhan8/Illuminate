"""Chapter 10: the search tree, with a whole column generation run at each node."""

import math

from bandp import mill as m
from bandp.search import branch_and_price
from illuminate.draw import (TEXT, TEXT_DIM, TEXT_FAINT, OK, SURFACE, PLAN, PRICE, HAIRLINE,
                             chapter_dir, figure, heading, save, tag)

OUT = chapter_dir("10-branch-and-price")


def tree_png():
    """The tree for the bigger order: eleven nodes, each one a full loop.

    Laid out by depth, with each node showing what its relaxation came back
    with. The point of the picture is that every one of those boxes hides a
    complete solve-price-add cycle, and that the tree stays small because the
    bound it starts from is already tight.
    """
    report = m.SCALE_SEARCH
    inst = m.SCALE
    nodes = report.nodes

    by_depth: dict[int, list] = {}
    for node in nodes:
        by_depth.setdefault(node.depth, []).append(node)
    depth_max = max(by_depth)

    fig, ax = figure(8.6, 4.8)
    fig.subplots_adjust(left=0.04, right=0.97, top=0.84, bottom=0.06)
    heading(ax, "one column generation run per box")
    ax.set_xlim(-0.5, 1.06)
    ax.set_ylim(-0.6, depth_max + 0.7)
    ax.invert_yaxis()
    ax.set_xticks([]); ax.set_yticks([])
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)

    placed = {}
    for depth, row in by_depth.items():
        for k, node in enumerate(row):
            x = (k + 1) / (len(row) + 1)
            placed[id(node)] = (x, depth)

    # a child's bounds extend its parent's, so the parent is the node whose
    # bound tuple is this one's prefix
    for node in nodes:
        if not node.bounds:
            continue
        parent = next((other for other in nodes
                       if other.bounds == node.bounds[:-1]
                       and other.depth == node.depth - 1), None)
        if parent is None:
            continue
        x0, y0 = placed[id(parent)]
        x1, y1 = placed[id(node)]
        ax.plot([x0, x1], [y0 + 0.16, y1 - 0.16], color=TEXT_FAINT, linewidth=0.9,
                zorder=2)

    colours = {"integral": OK, "pruned": TEXT_FAINT, "infeasible": TEXT_FAINT, "open": PLAN}
    for node in nodes:
        x, y = placed[id(node)]
        colour = colours[node.status]
        if node.bound is None:
            text = "no plan\nusing these"
        else:
            text = f"{m.decimal(node.bound, 2)}"
            if node.status == "integral":
                text += "\nwhole"
            elif node.status == "pruned":
                text += "\ncannot win"
            else:
                text += "\nsplit"
        ax.text(x, y, text, ha="center", va="center", fontsize=8.5,
                color=colour, zorder=6, linespacing=1.35,
                bbox=dict(boxstyle="square,pad=0.42", facecolor=SURFACE,
                          edgecolor=colour, linewidth=1.2))

    root = next(n for n in nodes if not n.bounds)
    tag(ax, -0.46, 0, f"the relaxation:\n{m.decimal(root.bound, 3)} boards",
        color=TEXT_DIM, size=9.5)
    tag(ax, -0.46, depth_max,
        f"{report.explored} nodes,\nanswer {report.best} boards",
        color=TEXT_DIM, size=9.5)
    save(fig, OUT / "tree.png", tight=False)


if __name__ == "__main__":
    tree_png()
