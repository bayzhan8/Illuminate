"""Two first-order methods for linear programming, differing by one term.

Both solve

    min c'x  subject to  Ax <= b,  x >= 0

by treating it as a saddle point. Introduce a price y >= 0 for each row and
write

    L(x, y) = c'x + y'(Ax - b),

then look for the point where x cannot go lower and y cannot go higher. The
plan minimises, the prices maximise, and the answer is where neither can move.

The only operations either method performs are `A @ x`, `A.T @ y`, adding
vectors, and clamping at zero. There is no factorisation, no pivoting, no basis
and no ordering. That is the entire reason this family is interesting on
parallel hardware, and it is why chapter 3 spends its time on what the
iteration does *not* contain.

Everything here is float, not Fraction, and that is deliberate: a first-order
method has no exact answer to be exact about. Its whole subject is how close it
has got. The exact arithmetic lives in `lpduality`, which the tests use as the
truth to measure against.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class Problem:
    """min c'x subject to Ax <= b, x >= 0."""

    A: np.ndarray
    b: np.ndarray
    c: np.ndarray

    @staticmethod
    def build(A, b, c) -> "Problem":
        return Problem(np.asarray(A, float), np.asarray(b, float),
                       np.asarray(c, float))

    @staticmethod
    def maximise(A, b, profit) -> "Problem":
        """The same thing written the way a workshop would state it."""
        return Problem.build(A, b, -np.asarray(profit, float))

    @property
    def norm(self) -> float:
        """The largest amount `A` can stretch a vector.

        The step sizes have to satisfy `tau * sigma * norm**2 < 1` or the
        iteration is not guaranteed to converge, so this is the one global
        quantity either method needs. It costs a handful of matrix-vector
        products to estimate and is then never touched again.
        """
        return float(np.linalg.norm(self.A, 2))

    def objective(self, x) -> float:
        return float(self.c @ np.asarray(x, float))

    def violation(self, x) -> float:
        """How far outside the rules a proposed plan is, at worst.

        Zero for anything the simplex method returns, because simplex only ever
        stands on corners of the feasible region. Not zero for a first-order
        iterate, which approaches feasibility from outside rather than walking
        around inside. Chapter 9 is about what that costs.
        """
        x = np.asarray(x, float)
        return float(max(0.0, np.max(self.A @ x - self.b), -np.min(x)))


@dataclass
class Trace:
    """Everything one run produced, kept so the figures can replay it."""

    xs: np.ndarray                 # one row per iteration: the plan
    ys: np.ndarray                 # one row per iteration: the prices
    restarts: list = field(default_factory=list)

    @property
    def last(self):
        return self.xs[-1], self.ys[-1]

    def distance_to(self, x_star, y_star) -> np.ndarray:
        target = np.concatenate([np.asarray(x_star, float),
                                 np.asarray(y_star, float)])
        both = np.hstack([self.xs, self.ys])
        return np.linalg.norm(both - target, axis=1)


def steps_for(problem: Problem, safety: float = 0.9) -> tuple[float, float]:
    """A step size for each side, chosen so the product stays under the limit."""
    step = safety / problem.norm
    return step, step


# --- the obvious method, which does not work -------------------------------

def gradient_descent_ascent(problem: Problem, iterations: int,
                            start=None, tau=None, sigma=None) -> Trace:
    """Push the plan downhill and the prices uphill, at the same time.

    This is what anybody would write first, and on a saddle it spirals
    *outward*. The reason is visible in the update itself: the prices are told
    to respond to `x^k`, the plan the solver has already abandoned, so each
    side is always reacting to where the other one just was. Chapter 4 draws
    the result.
    """
    tau_, sigma_ = steps_for(problem)
    tau = tau or tau_
    sigma = sigma or sigma_
    x = np.zeros(len(problem.c)) if start is None else np.asarray(start[0], float).copy()
    y = np.zeros(len(problem.b)) if start is None else np.asarray(start[1], float).copy()

    xs, ys = [x.copy()], [y.copy()]
    for _ in range(iterations):
        x_new = np.maximum(x - tau * (problem.c + problem.A.T @ y), 0.0)
        y_new = np.maximum(y + sigma * (problem.A @ x - problem.b), 0.0)  # x^k
        x, y = x_new, y_new
        xs.append(x.copy())
        ys.append(y.copy())
    return Trace(np.array(xs), np.array(ys))


# --- the method that does work ---------------------------------------------

def pdhg(problem: Problem, iterations: int, start=None,
         tau=None, sigma=None, restart_every: int = 0) -> Trace:
    """The same iteration, with the prices told where the plan is *going*.

    One term changes. The dual update uses `2 x^{k+1} - x^k` in place of `x^k`:
    the new plan, plus the step it just took again. It is the cheapest possible
    guess at where the plan will be next, and it converts a method that spirals
    outward into one that spirals inward.

    `restart_every` averages the epoch and begins again from the average.
    Averaging over a whole revolution cancels the rotation, which is the entire
    trick of chapter 7; passing 0 turns it off.
    """
    tau_, sigma_ = steps_for(problem)
    tau = tau or tau_
    sigma = sigma or sigma_
    x = np.zeros(len(problem.c)) if start is None else np.asarray(start[0], float).copy()
    y = np.zeros(len(problem.b)) if start is None else np.asarray(start[1], float).copy()

    xs, ys, restarts = [x.copy()], [y.copy()], []
    run_x, run_y, seen = np.zeros_like(x), np.zeros_like(y), 0

    for step in range(1, iterations + 1):
        x_new = np.maximum(x - tau * (problem.c + problem.A.T @ y), 0.0)
        lead = 2 * x_new - x                       # <- the whole difference
        y = np.maximum(y + sigma * (problem.A @ lead - problem.b), 0.0)
        x = x_new

        run_x += x
        run_y += y
        seen += 1
        if restart_every and seen == restart_every:
            x, y = run_x / seen, run_y / seen
            run_x, run_y, seen = np.zeros_like(x), np.zeros_like(y), 0
            restarts.append(step)

        xs.append(x.copy())
        ys.append(y.copy())
    return Trace(np.array(xs), np.array(ys), restarts)


# --- what the spiral is doing, in closed form ------------------------------

def spiral_matrix(a: float, tau: float, sigma: float) -> np.ndarray:
    """The one-step map of PDHG on the smallest possible problem.

    For a single equality `a x = rhs` with no objective and no clamping, the
    iteration is linear, and in coordinates measured from the answer it is
    multiplication by this matrix. Everything chapter 6 says about rotation and
    contraction is read off its eigenvalues.
    """
    return np.array([[1.0, tau * a],
                     [-sigma * a, 1.0 - 2 * tau * sigma * a * a]])


def spiral_anatomy(a: float, tau: float, sigma: float) -> dict:
    """How far the spiral turns, and how much it shrinks, per iteration.

    The eigenvalues are a conjugate pair whenever `tau*sigma*a^2` is between 0
    and 1, which is exactly the range the step-size rule allows. Their modulus
    is the contraction per step and their argument is the rotation per step,
    and both have closed forms worth stating because they explain the whole
    difficulty: the rule that keeps the method stable is the same rule that
    makes it barely contract.
    """
    t = tau * sigma * a * a
    if not 0 < t < 1:
        raise ValueError("the step sizes must satisfy 0 < tau*sigma*a^2 < 1")
    values = np.linalg.eigvals(spiral_matrix(a, tau, sigma))
    lead = values[np.argmax(values.imag)]
    return {
        "eigenvalues": values,
        "contraction": float(abs(lead)),           # = sqrt(1 - t)
        "contraction_closed_form": float(np.sqrt(1 - t)),
        "rotation_degrees": float(np.degrees(np.angle(lead))),
        "rotation_closed_form": float(np.degrees(np.arctan(np.sqrt(t / (1 - t))))),
        "iterations_per_turn": float(360.0 / np.degrees(np.angle(lead))),
    }


# --- how hard the kernel works the machine ---------------------------------

BYTES_PER_NONZERO = 12       # an 8-byte value and a 4-byte column index
FLOPS_PER_NONZERO = 2        # one multiply and one add


def arithmetic_intensity(bytes_per_nonzero: int = BYTES_PER_NONZERO,
                         flops_per_nonzero: int = FLOPS_PER_NONZERO) -> float:
    """Arithmetic performed per byte fetched, for a sparse matrix-vector product.

    Roughly one sixth of a floating-point operation per byte. The comparison
    that matters is against a machine's own ratio of arithmetic throughput to
    memory bandwidth: divide one by the other and you get the fraction of the
    machine's arithmetic the kernel can possibly use.

    The count deliberately ignores reads of the vector being multiplied and
    writes of the result, both of which depend on the sparsity pattern and on
    cache behaviour. Including them lowers the intensity further, so this is
    the optimistic end, and the conclusion does not depend on which end you
    take.
    """
    return flops_per_nonzero / bytes_per_nonzero


def usable_fraction(flops_per_second: float, bytes_per_second: float,
                    intensity: float | None = None) -> float:
    """What share of a machine's arithmetic a bandwidth-bound kernel can reach.

    A machine that can perform `balance = flops / bytes` operations per byte
    delivered will sit idle for most of them if the kernel only asks for
    `intensity` of them. The ratio is the answer, and it is the reason a
    sparse solve reports a laughable percentage of peak on any machine, and a
    worse one on the machine with more arithmetic.
    """
    intensity = arithmetic_intensity() if intensity is None else intensity
    balance = flops_per_second / bytes_per_second
    return intensity / balance
