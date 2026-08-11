"""The method that was polynomial first, and lost anyway.

Khachiyan's 1979 result made linear programming a polynomial problem, and the
method behind it does something neither of the other two does: it ignores the
region's shape entirely. Wrap the region in an ellipsoid. Ask whether the
centre is inside. If it is not, some rule you have violated tells you which
half of the ellipsoid the region cannot be in, so throw that half away and
wrap the survivor in a new ellipsoid. Repeat.

The guarantee is that each step shrinks the volume by at least a fixed factor,
so after enough steps the ellipsoid is smaller than any region that has room
in it, and if you have not found a point by then there was none to find. That
is a genuine bound and it is honestly obtained. It is also the slowest thing
imaginable, because the factor is barely below one and it does not care how
easy the problem was: it takes its worst case every time.

Implemented here in two dimensions, for feasibility rather than optimisation,
because that is the version worth drawing.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Step:
    """One iteration: the ellipsoid, and the rule that cut it (None if done)."""

    centre: np.ndarray
    shape: np.ndarray                  # P, with the ellipsoid {x : (x-c)'P^-1(x-c) <= 1}
    cut: int | None

    @property
    def volume(self) -> float:
        """Area, in two dimensions: pi * sqrt(det P)."""
        return float(np.pi * np.sqrt(max(np.linalg.det(self.shape), 0.0)))


def shrink_factor(n: int) -> float:
    """The volume ratio one cut is guaranteed to achieve, in n dimensions.

    exp(-1 / (2n)) is the usual bound. The point of quoting it is how close to
    1 it is: in two dimensions each step is guaranteed to remove only about a
    fifth of the area, and that guarantee is the whole of the method's speed.
    """
    return float(np.exp(-1.0 / (2 * n)))


def _violated(walls: np.ndarray, limits: np.ndarray, x: np.ndarray) -> int | None:
    """The index of a rule this point breaks, or None if it breaks none."""
    slack = limits - walls @ x
    worst = int(np.argmin(slack))
    return worst if slack[worst] < 0 else None


def run(walls, limits, centre, radius: float, steps: int = 200) -> list[Step]:
    """Central-cut ellipsoid, from a disc of the given radius.

    `walls @ x <= limits` is the region. The returned list is every ellipsoid
    the method considered, so a figure can draw the sequence; the last one has
    `cut is None` exactly when its centre is feasible.
    """
    walls = np.asarray(walls, float)
    limits = np.asarray(limits, float)
    n = walls.shape[1]
    x = np.array(centre, float)
    P = np.eye(n) * radius ** 2
    history = []
    for _ in range(steps):
        broken = _violated(walls, limits, x)
        history.append(Step(x.copy(), P.copy(), broken))
        if broken is None:
            return history
        a = walls[broken]
        Pa = P @ a
        scale = float(np.sqrt(a @ Pa))
        if scale <= 0:
            return history
        g = Pa / scale
        x = x - g / (n + 1)
        P = (n ** 2 / (n ** 2 - 1)) * (P - (2.0 / (n + 1)) * np.outer(g, g))
    return history
