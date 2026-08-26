"""The examples the guide runs on, and every number it quotes about them.

Two problems, doing two jobs.

`WORKSHOP` is the same workshop as the duality guide: three shelves, two
products, best plan 9 tables and 4 chairs worth $350. Using it again is not
economy. It means the answer is already known exactly, in rationals, from a
method that shares no line of code with anything here, so every claim about
what a first-order method found can be checked rather than asserted.

The toy the guide draws -- one variable, one rule, x >= 3 -- is the smallest
problem that still spirals, and its whole trajectory lives in a plane. It is
defined in `figures/fig04_the_spiral.py` rather than here, because that is the
only place it is used.
"""

from __future__ import annotations

import numpy as np

from lpduality import workshop as w
from lpduality.lp import solve

from .methods import (Problem, arithmetic_intensity, gradient_descent_ascent,
                      pdhg, spiral_anatomy, steps_for, usable_fraction)

# --- the workshop, restated for a method that wants matrices ---------------

WORKSHOP = Problem.maximise(
    A=[[4, 2], [2, 3], [3, 1]],      # planks, hours, saw time per product
    b=[44, 30, 32],
    profit=[30, 20],
)

_exact = solve(w.PRIMAL)
TRUE_PLAN = np.array([float(v) for v in _exact.x])          # (9, 4)
TRUE_VALUE = float(_exact.value)                            # 350
TRUE_PRICES = np.array([float(v) for v in _exact.prices])   # (6.25, 2.5, 0)

TAU, SIGMA = steps_for(WORKSHOP)

# --- the toy, which is small enough to draw --------------------------------

# minimise nothing, subject to x = 3, written as two inequalities so the
# machinery is the same one the workshop uses
# Removed: a `TOY` Problem written as the pair x <= 3, -x <= -3. Nothing read
# it, and it did not match the toy the guide actually draws -- fig04 implements
# x >= 3, whose price moves the other way. Two different toys under one name is
# a trap for whoever wires it up next. The drawn one lives in
# figures/fig04_the_spiral.py, which is the only place it is used.

# The spiral is analysed on the bare one-equality map, where the clamp never
# binds and the iteration is exactly a rotation-and-shrink.
SPIRAL_STEP = 0.2
SPIRAL = spiral_anatomy(a=1.0, tau=SPIRAL_STEP, sigma=SPIRAL_STEP)


# --- what each method does on the workshop ---------------------------------

def cycling_run(iterations: int = 4000):
    return gradient_descent_ascent(WORKSHOP, iterations)


def converging_run(iterations: int = 4000, restart_every: int = 0):
    return pdhg(WORKSHOP, iterations, restart_every=restart_every)


def cycle_period(trace, settled: int = 2000, window: int = 200) -> int:
    """How many steps the oscillation takes to return to where it was.

    Measured rather than assumed: take a state well past the transient, and
    find the smallest later step at which the whole iterate repeats.
    """
    both = np.hstack([trace.xs, trace.ys])[settled:]
    gaps = np.linalg.norm(both - both[0], axis=1)
    return int(np.argmin(gaps[5:window]) + 5)


_cycle = cycling_run()
CYCLE_PERIOD = cycle_period(_cycle)
_cycle_values = -(WORKSHOP.c @ _cycle.xs.T)
CYCLE_LOW = float(_cycle_values[-1000:].min())
CYCLE_HIGH = float(_cycle_values[-1000:].max())
CYCLE_WORST_VIOLATION = float(max(WORKSHOP.violation(x) for x in _cycle.xs[-1000:]))

_converged = converging_run()
FOUND_PLAN, FOUND_PRICES = _converged.last
FOUND_VALUE = -float(WORKSHOP.c @ FOUND_PLAN)


def distance_curve(trace) -> np.ndarray:
    return trace.distance_to(TRUE_PLAN, TRUE_PRICES)


# --- the price of using it -------------------------------------------------

def feasibility_ladder(steps=(10, 50, 100, 500, 1000, 5000)) -> list[tuple]:
    """How far outside the rules the proposed plan still is, as work goes in.

    A simplex iterate is a corner of the feasible region and is therefore legal
    at every step. A first-order iterate is not legal until it has converged,
    and chapter 9 is about which of those two facts matters to you.
    """
    out = []
    for n in steps:
        x, _ = pdhg(WORKSHOP, n).last
        out.append((n, -float(WORKSHOP.c @ x), WORKSHOP.violation(x)))
    return out


# A tie: every point on the segment from (1,0) to (0,1) is optimal. Simplex
# must return one of the two corners. PDHG returns the middle, which is just as
# optimal and is not a corner -- and a branch-and-bound tree needs a corner.
TIE = Problem.maximise(A=[[1, 1]], b=[1], profit=[1, 1])


def tie_answers():
    from lpduality.lp import LP, solve as exact_solve
    interior, _ = pdhg(TIE, 20000).last
    corner = exact_solve(LP.build(c=[1, 1], A=[[1, 1]], b=[1], op="<=", sense="max"))
    return interior, np.array([float(v) for v in corner.x])


# --- how hard the kernel works the machine ---------------------------------

INTENSITY = arithmetic_intensity()        # flops performed per byte fetched


def usable_fraction_for(flops: float, bandwidth: float) -> float:
    """Share of a machine's arithmetic a bandwidth-bound kernel can reach."""
    return usable_fraction(flops, bandwidth)


def machine_usage(flops: float, bandwidth: float) -> dict:
    """What a bandwidth-bound kernel can reach on a machine with these numbers."""
    return {
        "balance": flops / bandwidth,
        "usable": usable_fraction(flops, bandwidth),
        "ceiling": bandwidth * INTENSITY,
    }


def number(x, places: int = 2) -> str:
    return f"{x:,.{places}f}".rstrip("0").rstrip(".") if places else f"{x:,.0f}"
