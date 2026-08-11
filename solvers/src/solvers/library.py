"""The two instances the guide is built on, and every number it quotes.

The small one is a lot-sizing model of the kind somebody writes on a first
pass: three products over two periods, opening and closing inventory written
as constraints rather than bounds, a setup switch per product per period, and
a capacity row. It is deliberately not tidied up, because presolve exists to
tidy up models nobody tidied up.

The large one is the same generator at eight products over six periods, kept
so the guide can say what the reductions do at a size nobody would read.
"""

from __future__ import annotations

from fractions import Fraction as F

from .model import Model, build
from .presolve import presolve
from .solve import relax, solve_mip

HOLD_COST = 1
SETUP_COST = 20


def lot_sizing(products, periods, demand, capacity, big_m, make_cost,
               hold_cost=HOLD_COST, setup=SETUP_COST) -> Model:
    """Make it, hold it, or do without it, with a switch for setting up."""
    cols: list[tuple] = []
    cost: list[int] = []

    def col(name, lo, hi, integer, c):
        cols.append((name, lo, hi, integer))
        cost.append(c)

    for p in products:
        for t in periods:
            col(f"make{p}{t}", 0, None, True, make_cost[p])
        for t in [periods[0] - 1, *periods]:
            col(f"hold{p}{t}", 0, None, True, 0 if t == periods[0] - 1 else hold_cost)
        for t in periods:
            col(f"open{p}{t}", 0, 1, True, setup)

    rows = []
    first, last = periods[0], periods[-1]
    for p in products:
        # the two habits that give presolve its first foothold: an opening and
        # a closing inventory level, written as rows because that is how they
        # come out of a modelling language
        rows.append((f"start{p}", {f"hold{p}{first - 1}": 1}, 0, 0))
        rows.append((f"end{p}", {f"hold{p}{last}": 1}, 0, 0))
        for t in periods:
            rows.append((f"bal{p}{t}",
                         {f"hold{p}{t - 1}": 1, f"make{p}{t}": 1, f"hold{p}{t}": -1},
                         demand[(p, t)], demand[(p, t)]))
            rows.append((f"link{p}{t}",
                         {f"make{p}{t}": 1, f"open{p}{t}": -big_m}, None, 0))
    for t in periods:
        rows.append((f"cap{t}", {f"make{p}{t}": 1 for p in products}, None, capacity[t]))

    return build(cost=cost, rows=rows, cols=cols, sense="min")


# --- the small instance, the one the guide prints in full -------------------

PRODUCTS = ("A", "B", "C")
PERIODS = (1, 2)
DEMAND = {("A", 1): 0, ("A", 2): 40,
          ("B", 1): 25, ("B", 2): 25,
          ("C", 1): 0, ("C", 2): 0}          # C is on the sheet and nobody wants it
CAPACITY = {1: 100, 2: 100}
BIG_M = 100
MAKE_COST = {"A": 2, "B": 3, "C": 5}

SMALL = lot_sizing(PRODUCTS, PERIODS, DEMAND, CAPACITY, BIG_M, MAKE_COST)
SMALL_PRESOLVED = presolve(SMALL)
SMALL_REDUCED = SMALL_PRESOLVED.model

SMALL_ANSWER = solve_mip(SMALL)
SMALL_REDUCED_ANSWER = solve_mip(SMALL_REDUCED)
SMALL_RELAXATION = relax(SMALL).value
SMALL_REDUCED_RELAXATION = relax(SMALL_REDUCED).value


# --- the large instance, quoted only for its shape --------------------------

BIG_PRODUCTS = tuple("ABCDEFGH")
BIG_PERIODS = tuple(range(1, 7))
BIG_DEMAND_TABLE = {
    "A": (0, 20, 40, 0, 0, 30),
    "B": (0, 0, 0, 0, 0, 0),
    "C": (30, 0, 0, 0, 20, 20),
    "D": (0, 0, 0, 0, 0, 0),
    "E": (0, 0, 0, 0, 0, 0),
    "F": (30, 0, 0, 40, 40, 30),
    "G": (30, 30, 20, 0, 0, 0),
    "H": (0, 10, 20, 0, 30, 0),
}
BIG_DEMAND = {(p, t): BIG_DEMAND_TABLE[p][t - 1]
              for p in BIG_PRODUCTS for t in BIG_PERIODS}
BIG_MAKE_COST = {"A": 6, "B": 4, "C": 6, "D": 3, "E": 2, "F": 6, "G": 6, "H": 3}

BIG = lot_sizing(BIG_PRODUCTS, BIG_PERIODS, BIG_DEMAND,
                 {t: 300 for t in BIG_PERIODS}, 300, BIG_MAKE_COST)
BIG_PRESOLVED = presolve(BIG)


# --- formatting helpers the figures and the prose share ---------------------

def percent_removed(before: int, after: int) -> str:
    return f"{round(100 * (before - after) / before)}%"


def shape_words(shape) -> str:
    rows, cols, nz = shape
    return f"{rows} rows, {cols} columns, {nz} nonzeros"


def money(value: F) -> str:
    return f"${int(value)}" if F(value).denominator == 1 else f"${float(value):.2f}"


def plan(answer, model: Model) -> dict[str, F]:
    """The non-zero part of a solution, which is the part worth printing."""
    return {c.name: v for c, v in zip(model.cols, answer.x) if v != 0}
