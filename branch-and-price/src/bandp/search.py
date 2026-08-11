"""Column generation inside a search tree: branch-and-price.

The relaxation says 452¼ rolls.  Nobody cuts a quarter of a roll, and rounding
the fractional answer up is not reliably right, so the fractional answer has to
be branched away.  What makes this branch-and-*price* rather than plain
branch-and-bound is that the relaxation at every node is itself solved by
generating columns, so the tree never holds the full pattern list at any point.

A note on the branching rule, because it matters and is easy to gloss over.
This module branches on a single pattern's count: one child is told to use it
at most floor(x) times, the other at least ceil(x).  It keeps the pricing
problem unchanged and it is the rule that makes the idea legible in a chapter.
It is also a weak rule -- the at-most side can be undone by pricing out a very
slightly different pattern, so trees grow -- and practice uses Ryan-Foster
branching, which branches on whether two pieces share a roll and pushes the
restriction down into the pricing problem instead.

Two traps in this rule cost real answers before the tests caught them, and both
are worth knowing about because neither announces itself:

1. A branching row carries its own dual, so the knapsack can keep nominating a
   pattern the master already holds and has pinned at its bound.  Treating that
   as "no improving column exists" leaves the node's relaxation unsolved and
   its bound too high, and for a minimisation a bound that is too high prunes
   the optimum.
2. A restricted master can be infeasible at a node that is perfectly feasible,
   because the columns that would have met the demand have not been generated
   yet.  Reading that as an infeasible node throws away real solutions.

The first is handled in `solve_node`, the second by the emergency columns in
`restricted_master`.  With both, this agrees with brute-force integer optima on
every one of the 1230 instances `tests/test_search.py` puts through it; the
first version of this file, which had neither, disagreed on 476 of them while
looking entirely reasonable.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction

from lpduality.lp import LP, solve

from .cutting import (Instance, all_patterns, price, starting_patterns)


@dataclass(frozen=True)
class Bound:
    """One branching decision: this pattern, at most or at least this many."""

    pattern: tuple[int, ...]
    limit: int
    direction: str    # "<=" or ">="

    def describe(self, inst: Instance) -> str:
        word = "at most" if self.direction == "<=" else "at least"
        return f"{inst.describe(self.pattern)} used {word} {self.limit}×"


def emergency_price(inst: Instance) -> int:
    """What one piece costs if it has to be conjured from nowhere.

    Any genuine answer cuts at most one roll per piece ordered, so a price
    above that total makes conjuring strictly worse than every real plan.  The
    number is therefore high enough to never be chosen when a real plan exists,
    and small enough to keep the arithmetic readable.
    """
    return sum(inst.demands) + 1


def restricted_master(inst: Instance, patterns, bounds: tuple[Bound, ...]) -> LP:
    """The master over the patterns held so far, plus this node's decisions.

    Two things are added to the textbook master.

    A branching row per decision.  Each mentions exactly one pattern, so any
    column generated later takes a zero in it, which is why the pricing problem
    never has to know which node it is being called from.

    An emergency column per item width, which supplies one piece of that width
    at a punitive price.  Without them a restricted master can be infeasible
    while the node it represents is perfectly feasible -- the columns that would
    have satisfied the demand simply have not been generated yet -- and reading
    that as "this node is infeasible" throws away real solutions.  With them the
    master always has an answer, pricing gets duals to work from, and the
    emergency columns fall out of the basis on their own as real patterns
    arrive.  Any still in use at the end mean the node really is infeasible.
    """
    rows = [[p[i] for p in patterns] for i in range(inst.m)]
    rhs = list(inst.demands)
    ops = [">="] * inst.m
    names = [f"pieces of width {w}" for w in inst.widths]
    cost = [1] * len(patterns)

    for i in range(inst.m):                      # the emergency columns
        for row_index in range(inst.m):
            rows[row_index].append(1 if row_index == i else 0)
        cost.append(emergency_price(inst))

    for bound in bounds:
        row = [1 if p == bound.pattern else 0 for p in patterns] + [0] * inst.m
        rows.append(row)
        rhs.append(bound.limit)
        ops.append(bound.direction)
        names.append(bound.describe(inst))

    labels = tuple(inst.describe(p) for p in patterns) + \
        tuple(f"conjure a piece of width {w}" for w in inst.widths)
    return LP.build(c=cost, A=rows, b=rhs, op=ops, sense="min",
                    var_names=labels, row_names=tuple(names))


def best_new_pattern(inst: Instance, duals, patterns):
    """The most valuable pattern that is *not* already in the master.

    This scans the whole pattern list, which is exactly the thing column
    generation exists to avoid, and it is only ever reached in the situation
    described below.  It is a stand-in for a proper branching rule, and it is
    why this module is for understanding branch-and-price rather than for
    running it at scale.
    """
    known = set(patterns)
    best_value, best = None, None
    for candidate in all_patterns(inst):
        if candidate in known:
            continue
        value = sum(Fraction(d) * n for d, n in zip(duals, candidate))
        if best_value is None or value > best_value:
            best_value, best = value, candidate
    return best_value, best


def solve_node(inst: Instance, bounds: tuple[Bound, ...], patterns=None,
               limit: int = 200):
    """Solve one node's relaxation by column generation, to optimality.

    The knapsack prices columns using the demand rows' duals only, because a
    branching row mentions one existing pattern and any new column takes a zero
    in it.

    The subtle case, and the one that made an earlier version of this quietly
    return wrong answers: a branching row ``x_s <= u`` contributes its own dual
    to *its own* column's reduced cost, so the knapsack can keep nominating a
    pattern that is already in the master and pinned at its bound.  Stopping
    there leaves the node's relaxation unsolved and its bound too high, which
    for a minimisation prunes away the real optimum.  So when the winner is a
    pattern already held, the search continues among patterns that are not --
    that, and not the knapsack's answer, is the condition column generation is
    actually allowed to stop on.
    """
    patterns = list(patterns if patterns is not None else starting_patterns(inst))
    # a node that insists on using a pattern must be able to see it
    for bound in bounds:
        if bound.pattern not in patterns:
            patterns.append(bound.pattern)
    for _ in range(limit):
        here = solve(restricted_master(inst, patterns, bounds))
        if not here.ok:
            return here, patterns
        value, pattern = price(inst, here.prices[:inst.m])
        if value > 1 and pattern in patterns:
            value, pattern = best_new_pattern(inst, here.prices[:inst.m], patterns)
            if pattern is None:
                return here, patterns
        if value <= 1 or pattern in patterns:
            return _without_emergency(here, len(patterns)), patterns
        patterns.append(pattern)
    raise RuntimeError("column generation did not settle at a node")


def _without_emergency(here, count: int):
    """Trim the emergency columns off a solved master.

    If any of them is still carrying load, no combination of the patterns this
    node is allowed to use can meet the orders, and the node is infeasible for
    real rather than merely under-supplied with columns.
    """
    from dataclasses import replace
    if any(v != 0 for v in here.x[count:]):
        return replace(here, status="infeasible", x=(), value=None)
    return replace(here, x=tuple(here.x[:count]))


@dataclass
class Node:
    bounds: tuple[Bound, ...]
    depth: int
    bound: Fraction | None = None
    x: tuple[Fraction, ...] = ()
    patterns: list = field(default_factory=list)
    status: str = "open"     # open | integral | pruned | infeasible


@dataclass
class Report:
    best: Fraction | None
    plan: dict
    nodes: list[Node]
    root_bound: Fraction | None

    @property
    def explored(self) -> int:
        return len(self.nodes)


def is_integral(x) -> bool:
    return all(Fraction(v).denominator == 1 for v in x)


def branch_and_price(inst: Instance, node_limit: int = 400) -> Report:
    """Exact integer answer, without ever listing the patterns."""
    root = Node(bounds=(), depth=0)
    queue = [root]
    seen: list[Node] = []
    incumbent: Fraction | None = None
    best_plan: dict = {}
    root_bound = None

    while queue:
        node = queue.pop()
        if len(seen) >= node_limit:
            raise RuntimeError("the tree grew past its limit")
        here, patterns = solve_node(inst, node.bounds)
        node.patterns = patterns
        seen.append(node)

        if not here.ok:
            node.status = "infeasible"
            continue
        node.bound = here.value
        node.x = here.x
        if root_bound is None:
            root_bound = here.value

        # a node cannot beat the incumbent if its relaxation already needs
        # more rolls than the incumbent uses, and rolls come in whole numbers
        if incumbent is not None and math.ceil(here.value) >= incumbent:
            node.status = "pruned"
            continue

        if is_integral(here.x):
            node.status = "integral"
            if incumbent is None or here.value < incumbent:
                incumbent = here.value
                best_plan = {patterns[j]: int(v) for j, v in enumerate(here.x) if v}
            continue

        j = next(k for k, v in enumerate(here.x) if Fraction(v).denominator != 1)
        level = Fraction(here.x[j])
        pattern = patterns[j]
        for direction, limit in (("<=", math.floor(level)), (">=", math.ceil(level))):
            queue.append(Node(bounds=node.bounds + (Bound(pattern, limit, direction),),
                              depth=node.depth + 1))

    return Report(best=incumbent, plan=best_plan, nodes=seen, root_bound=root_bound)


# --- something to check it against -----------------------------------------

def integer_optimum_by_enumeration(inst: Instance) -> Fraction:
    """The answer, found the slow honest way: every pattern, then branch and bound.

    Only usable on the toy instances, which is the point -- it exists so the
    tests can disagree with `branch_and_price` rather than trust it.
    """
    patterns = all_patterns(inst)
    lp = LP.build(c=[1] * len(patterns),
                  A=[[p[i] for p in patterns] for i in range(inst.m)],
                  b=list(inst.demands), op=">=", sense="min")
    best: Fraction | None = None
    stack: list[tuple[tuple[tuple[int, str, int], ...], None]] = [((), None)]
    while stack:
        bounds, _ = stack.pop()
        rows = list(lp.A)
        rhs = list(lp.b)
        ops = list(lp.op)
        for index, direction, limit in bounds:
            rows.append([1 if k == index else 0 for k in range(len(patterns))])
            rhs.append(limit)
            ops.append(direction)
        here = solve(LP.build(c=lp.c, A=rows, b=rhs, op=ops, sense="min"))
        if not here.ok:
            continue
        if best is not None and math.ceil(here.value) >= best:
            continue
        if is_integral(here.x):
            best = here.value if best is None else min(best, here.value)
            continue
        j = next(k for k, v in enumerate(here.x) if Fraction(v).denominator != 1)
        level = Fraction(here.x[j])
        stack.append((bounds + ((j, "<=", math.floor(level)),), None))
        stack.append((bounds + ((j, ">=", math.ceil(level)),), None))
    return best
