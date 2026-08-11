"""The cutting-stock problem, and the pieces branch-and-price is built from.

A mill has rolls of one width and orders for narrower pieces.  Every way of
slicing one roll is a *pattern*.  Choosing how many rolls to cut with each
pattern is a tiny-looking integer program with one enormous problem: the number
of patterns explodes, and for a real instance you cannot write them all down.

Everything here is exact.  The linear programs are solved by the same
fraction-arithmetic simplex the duality topic is built on -- this topic is that
one under load, so it reuses its solver rather than carrying a second copy.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

from lpduality.lp import LP, Solution, solve


@dataclass(frozen=True)
class Instance:
    """Rolls of width `width`, and orders for pieces of the listed widths."""

    width: int
    widths: tuple[int, ...]
    demands: tuple[int, ...]
    name: str = ""

    @property
    def m(self) -> int:
        return len(self.widths)

    def waste(self, pattern) -> int:
        return self.width - sum(w * s for w, s in zip(self.widths, pattern))

    def fits(self, pattern) -> bool:
        return self.waste(pattern) >= 0

    def is_maximal(self, pattern) -> bool:
        """No further piece could be squeezed into the leftover."""
        return self.waste(pattern) < min(self.widths)

    def describe(self, pattern) -> str:
        parts = [f"{n}×{w}" for w, n in zip(self.widths, pattern) if n]
        return " + ".join(parts) if parts else "nothing"


# --- every pattern, for the instances small enough to allow it -------------

def all_patterns(inst: Instance, maximal_only: bool = True) -> list[tuple[int, ...]]:
    """Enumerate the patterns.

    Only ever called on the toy instances the guide draws.  The whole point of
    column generation is that this function is the thing you cannot call, so it
    exists here to show the reader the number it would have to return.
    """
    out: list[tuple[int, ...]] = []

    def extend(index: int, left: int, sofar: tuple[int, ...]):
        if index == inst.m:
            if any(sofar) and (not maximal_only or left < min(inst.widths)):
                out.append(sofar)
            return
        for count in range(left // inst.widths[index] + 1):
            extend(index + 1, left - count * inst.widths[index], sofar + (count,))

    extend(0, inst.width, ())
    return out


def count_patterns(width: int, widths: tuple[int, ...]) -> int:
    """How many patterns exist, without building them.

    The guide quotes this number for instances whose patterns would not fit on
    a page, so it is counted rather than listed.
    """

    @lru_cache(maxsize=None)
    def ways(index: int, left: int) -> int:
        if index == len(widths):
            return 1
        return sum(ways(index + 1, left - k * widths[index])
                   for k in range(left // widths[index] + 1))

    return ways(0, width) - 1  # drop the empty pattern


# --- the master problem ----------------------------------------------------

def master(inst: Instance, patterns: list[tuple[int, ...]]) -> LP:
    """Use as few rolls as possible while meeting every order.

    One variable per pattern, one row per item width.  Written with >= on the
    demand rows because over-producing a piece is allowed and never helps; the
    dual of that row is what a piece is worth, and it wants to be non-negative.
    """
    return LP.build(
        c=[1] * len(patterns),
        A=[[p[i] for p in patterns] for i in range(inst.m)],
        b=list(inst.demands),
        op=">=",
        sense="min",
        var_names=tuple(inst.describe(p) for p in patterns),
        row_names=tuple(f"pieces of width {w}" for w in inst.widths),
    )


def solve_master(inst: Instance, patterns: list[tuple[int, ...]]) -> Solution:
    return solve(master(inst, patterns))


# --- the pricing problem ---------------------------------------------------

def price(inst: Instance, duals) -> tuple[Fraction, tuple[int, ...]]:
    """The most valuable pattern at these prices, and what it is worth.

    An unbounded knapsack: fill one roll with pieces to maximise the total
    price of what comes off it.  Solved exactly by dynamic programming over
    integer widths, so the answer is a pattern rather than an estimate.

    A value above one means that pattern's column has negative reduced cost --
    the roll it needs costs one roll, and the pieces it yields are worth more
    than that -- and the master is not finished.
    """
    duals = [Fraction(v) for v in duals]
    best = [Fraction(0)] * (inst.width + 1)
    choice: list[int | None] = [None] * (inst.width + 1)
    for capacity in range(1, inst.width + 1):
        for i, w in enumerate(inst.widths):
            if w <= capacity and best[capacity - w] + duals[i] > best[capacity]:
                best[capacity] = best[capacity - w] + duals[i]
                choice[capacity] = i
    pattern = [0] * inst.m
    capacity = inst.width
    while choice[capacity] is not None:
        i = choice[capacity]
        pattern[i] += 1
        capacity -= inst.widths[i]
    return best[inst.width], tuple(pattern)


def reduced_cost(value: Fraction) -> Fraction:
    """A roll costs one; the pieces it yields are worth `value` at these prices."""
    return Fraction(1) - value


# --- the loop --------------------------------------------------------------

@dataclass
class Round:
    patterns: list[tuple[int, ...]]
    value: Fraction                    # rolls the restricted master needs
    duals: tuple[Fraction, ...]
    best_pattern: tuple[int, ...]
    best_value: Fraction               # what that pattern is worth at these prices
    added: bool

    @property
    def reduced_cost(self) -> Fraction:
        return reduced_cost(self.best_value)


def starting_patterns(inst: Instance) -> list[tuple[int, ...]]:
    """One pattern per width: fill a whole roll with copies of that piece.

    Always enough to be feasible, because every order can be met by cutting
    dedicated rolls, and that is all a starting set has to be.
    """
    out = []
    for i, w in enumerate(inst.widths):
        pattern = [0] * inst.m
        pattern[i] = inst.width // w
        out.append(tuple(pattern))
    return out


def column_generation(inst: Instance, patterns=None, limit: int = 60) -> list[Round]:
    """Alternate between the restricted master and the knapsack until it stops.

    Returns every round, not just the answer, because the guide animates the
    loop and the tests check that it terminates for the right reason.
    """
    patterns = list(patterns if patterns is not None else starting_patterns(inst))
    rounds: list[Round] = []
    for _ in range(limit):
        here = solve_master(inst, patterns)
        assert here.ok, "the restricted master must stay feasible"
        value, pattern = price(inst, here.prices)
        # exact arithmetic, so "is it better than one" needs no tolerance
        improving = value > 1 and pattern not in patterns
        rounds.append(Round(list(patterns), here.value, here.prices,
                            pattern, value, improving))
        if not improving:
            return rounds
        patterns.append(pattern)
    raise RuntimeError("column generation did not settle")


def lp_bound(inst: Instance) -> Fraction:
    """The best the LP relaxation can do, found without enumerating patterns."""
    return column_generation(inst)[-1].value
