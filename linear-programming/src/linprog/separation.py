"""Exact projection onto a two-dimensional polygon and its separating wall."""

from fractions import Fraction
from itertools import combinations

from .lp import solve_square


def _fraction(value):
    return value if isinstance(value, Fraction) else Fraction(
        str(value) if isinstance(value, float) else value
    )


def _dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def _polygon(A, b):
    rows = tuple(tuple(_fraction(value) for value in row) for row in A)
    bounds = tuple(_fraction(value) for value in b)
    if len(rows) != len(bounds) or any(len(row) != 2 for row in rows):
        raise ValueError("a polygon needs one 2-D row for each bound")
    return rows, bounds


def _feasible(point, A, b):
    return all(_dot(row, point) <= bound for row, bound in zip(A, b))


def _distance_squared(left, right):
    return sum(((a - b) ** 2 for a, b in zip(left, right)), Fraction(0))


def project_to_polygon(x, A, b):
    """Return the nearest point in ``{s: A s <= b}`` and exact distance².

    The polygon's vertices and feasible perpendicular feet on its walls contain
    the nearest point. The input point itself is included when it is feasible.
    """
    point = tuple(_fraction(value) for value in x)
    rows, bounds = _polygon(A, b)
    if len(point) != 2:
        raise ValueError("projection is defined for a 2-D point")

    candidates = []
    if _feasible(point, rows, bounds):
        candidates.append(point)

    for first, second in combinations(range(len(rows)), 2):
        vertex = solve_square((rows[first], rows[second]),
                              (bounds[first], bounds[second]))
        if vertex is not None and _feasible(vertex, rows, bounds):
            candidates.append(vertex)

    for row, bound in zip(rows, bounds):
        norm_squared = _dot(row, row)
        if norm_squared == 0:
            continue
        scale = (_dot(row, point) - bound) / norm_squared
        foot = tuple(point[i] - scale * row[i] for i in range(2))
        if _feasible(foot, rows, bounds):
            candidates.append(foot)

    if not candidates:
        raise ValueError("the constraints do not define a nonempty polygon")

    nearest = min(candidates, key=lambda candidate: (
        _distance_squared(point, candidate), candidate
    ))
    return nearest, _distance_squared(point, nearest)


def separator(x, s_star):
    """Return ``(pi, pi0)`` for the midpoint wall between ``x`` and ``s_star``."""
    point = tuple(_fraction(value) for value in x)
    nearest = tuple(_fraction(value) for value in s_star)
    if len(point) != 2 or len(nearest) != 2:
        raise ValueError("a separating wall needs two 2-D points")
    pi = tuple(s - o for o, s in zip(point, nearest))
    midpoint = tuple((o + s) / 2 for o, s in zip(point, nearest))
    return pi, _dot(pi, midpoint)
