"""The other route: stay strictly inside, and follow the centre inwards.

Simplex refuses to leave the boundary. A barrier method refuses to touch it.
Add to the objective a penalty that becomes infinite at every wall,

    minimise   c'x  -  mu * ( sum of log(slack in each rule)
                              + sum of log(each variable) )

and the minimiser is pushed away from all the walls at once. Large `mu` puts it
near the middle of the region. Shrink `mu` towards zero and the penalty stops
mattering, so it slides towards the true optimum -- which is on the boundary,
and which it approaches without ever arriving.

The curve it traces as `mu` shrinks is the **central path**, and it is the
object the guide draws. Everything here is two-variable and solved by Newton's
method, because the point is to see the path rather than to solve anything at
scale.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Region:
    """max profit'x subject to Ax <= b, x >= 0, held as floats for Newton."""

    A: np.ndarray
    b: np.ndarray
    profit: np.ndarray

    @staticmethod
    def build(A, b, profit) -> "Region":
        return Region(np.asarray(A, float), np.asarray(b, float),
                      np.asarray(profit, float))

    def slack(self, x: np.ndarray) -> np.ndarray:
        """How much room is left in each rule, and in each variable's floor."""
        return np.concatenate([self.b - self.A @ x, x])

    def interior(self, x: np.ndarray) -> bool:
        return bool(np.all(self.slack(x) > 0))

    @property
    def walls(self) -> np.ndarray:
        """One row per wall: the rules, then the two axes, as `Wx <= w`."""
        return np.vstack([self.A, -np.eye(len(self.profit))])

    @property
    def limits(self) -> np.ndarray:
        return np.concatenate([self.b, np.zeros(len(self.profit))])


def barrier_value(region: Region, x: np.ndarray, mu: float) -> float:
    room = region.slack(x)
    if np.any(room <= 0):
        return np.inf
    return float(-region.profit @ x - mu * np.sum(np.log(room)))


def _gradient_and_hessian(region: Region, x: np.ndarray, mu: float):
    W, w = region.walls, region.limits
    room = w - W @ x
    inv = 1.0 / room
    gradient = -region.profit + mu * (W.T @ inv)
    hessian = mu * (W.T * inv ** 2) @ W
    return gradient, hessian


def centre_for(region: Region, mu: float, start: np.ndarray,
               steps: int = 200, tol: float = 1e-13) -> np.ndarray:
    """The point on the central path for this `mu`, by damped Newton.

    Damping matters: a full Newton step will happily walk through a wall,
    where the objective is not merely worse but undefined. Halving until the
    step lands somewhere legal is the whole of the safeguard.
    """
    x = np.array(start, float)
    for _ in range(steps):
        gradient, hessian = _gradient_and_hessian(region, x, mu)
        try:
            direction = np.linalg.solve(hessian, -gradient)
        except np.linalg.LinAlgError:
            break
        length = 1.0
        for _ in range(80):
            trial = x + length * direction
            if region.interior(trial) and \
                    barrier_value(region, trial, mu) <= barrier_value(region, x, mu):
                break
            length /= 2
        else:
            break
        x = x + length * direction
        if np.linalg.norm(length * direction) < tol:
            break
    return x


def central_path(region: Region, start: np.ndarray,
                 mu_from: float = 400.0, mu_to: float = 1e-9,
                 points: int = 60) -> np.ndarray:
    """The whole path, from the middle of the region out to the answer.

    Each point warm-starts from the last, which is what a real interior point
    method does and what keeps Newton inside its region of good behaviour.
    """
    mus = np.geomspace(mu_from, mu_to, points)
    x = np.array(start, float)
    path = []
    for mu in mus:
        x = centre_for(region, mu, x)
        path.append(x.copy())
    return np.array(path)


def analytic_centre(region: Region, start: np.ndarray) -> np.ndarray:
    """The point furthest from every wall at once, ignoring the objective.

    Where the path begins when `mu` is enormous. It has nothing to do with
    what you are optimising: it is a property of the shape alone.
    """
    zeroed = Region(region.A, region.b, np.zeros_like(region.profit))
    return centre_for(zeroed, 1.0, start)


def duality_gap(region: Region, x: np.ndarray, mu: float) -> float:
    """How far from optimal a point on the path is guaranteed to be.

    On the central path the gap is `mu` times the number of walls, which is
    why shrinking `mu` by a factor is exactly shrinking the guarantee by that
    factor, and why the method's progress is so predictable compared with a
    walk whose step count nobody can forecast.
    """
    return mu * len(region.limits)
