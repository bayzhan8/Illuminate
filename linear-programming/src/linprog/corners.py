"""Exact row-based tests for corners and rank-increasing walks."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations

from .lp import F, solve_square


def _matrix(rows, dimension=None):
    matrix = tuple(tuple(F(value) for value in row) for row in rows)
    inferred = len(matrix[0]) if matrix else dimension
    if inferred is None:
        inferred = 0
    if (dimension is not None and inferred != dimension) or \
            any(len(row) != inferred for row in matrix):
        raise ValueError("all rows must have the same length")
    return matrix, inferred


def _system(A, b):
    matrix, dimension = _matrix(A)
    rhs = tuple(F(value) for value in b)
    if len(matrix) != len(rhs):
        raise ValueError("A and b must have the same number of rows")
    return matrix, rhs, dimension


def _dot(row, point):
    return sum((a * x for a, x in zip(row, point)), Fraction(0))


def _reduced(rows, dimension=None):
    matrix, dimension = _matrix(rows, dimension)
    reduced = [list(row) for row in matrix]
    pivots = []
    pivot_row = 0
    for column in range(dimension):
        pivot = next(
            (row for row in range(pivot_row, len(reduced))
             if reduced[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        reduced[pivot_row], reduced[pivot] = reduced[pivot], reduced[pivot_row]
        scale = reduced[pivot_row][column]
        reduced[pivot_row] = [value / scale for value in reduced[pivot_row]]
        for row in range(len(reduced)):
            if row == pivot_row:
                continue
            factor = reduced[row][column]
            if factor:
                reduced[row] = [
                    value - factor * pivot_value
                    for value, pivot_value in zip(
                        reduced[row], reduced[pivot_row]
                    )
                ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(reduced):
            break
    return tuple(tuple(row) for row in reduced), tuple(pivots), dimension


def rank(rows):
    """Return the exact row rank."""
    _, pivots, _ = _reduced(rows)
    return len(pivots)


def nullspace(rows, n=None):
    """Return a basis built by setting each free column to one in turn."""
    reduced, pivots, dimension = _reduced(rows, n)
    pivot_set = set(pivots)
    basis = []
    for free in range(dimension):
        if free in pivot_set:
            continue
        vector = [Fraction(0)] * dimension
        vector[free] = Fraction(1)
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free]
        basis.append(tuple(vector))
    return tuple(basis)


def tight(A, b, x):
    """Return the indices of rows that hold with equality at x."""
    matrix, rhs, dimension = _system(A, b)
    point = tuple(F(value) for value in x)
    if len(point) != dimension:
        raise ValueError("x must have one entry per column of A")
    return tuple(
        index for index, (row, bound) in enumerate(zip(matrix, rhs))
        if _dot(row, point) == bound
    )


def _feasible(matrix, rhs, point):
    return all(_dot(row, point) <= bound for row, bound in zip(matrix, rhs))


def is_bfs(A, b, x):
    """Whether x is feasible and its tight rows have full column rank."""
    matrix, rhs, dimension = _system(A, b)
    point = tuple(F(value) for value in x)
    if len(point) != dimension:
        raise ValueError("x must have one entry per column of A")
    if not _feasible(matrix, rhs, point):
        return False
    indices = tight(matrix, rhs, point)
    return rank(matrix[index] for index in indices) == dimension


def is_degenerate(A, b, x):
    """Whether a feasible basic point has more tight rows than dimensions."""
    matrix, rhs, dimension = _system(A, b)
    point = tuple(F(value) for value in x)
    if len(point) != dimension:
        raise ValueError("x must have one entry per column of A")
    return is_bfs(matrix, rhs, point) and len(tight(matrix, rhs, point)) > dimension


def bases(A, b):
    """Return every independent n-row basis as (indices, point, feasible)."""
    matrix, rhs, dimension = _system(A, b)
    found = []
    for indices in combinations(range(len(matrix)), dimension):
        rows = tuple(matrix[index] for index in indices)
        if rank(rows) != dimension:
            continue
        point = solve_square(rows, tuple(rhs[index] for index in indices))
        if point is not None:
            found.append((indices, point, _feasible(matrix, rhs, point)))
    return found


def basic_points(A, b):
    """Return unique n-row intersections as (point, feasible) pairs."""
    matrix, rhs, dimension = _system(A, b)
    found = []
    seen = set()
    for indices in combinations(range(len(matrix)), dimension):
        point = solve_square(
            [matrix[index] for index in indices],
            [rhs[index] for index in indices],
        )
        if point is None or point in seen:
            continue
        seen.add(point)
        found.append((point, _feasible(matrix, rhs, point)))
    return found


def is_direction(A, d):
    """Whether Ad <= 0, the exact recession-direction test."""
    matrix, dimension = _matrix(A)
    direction = tuple(F(value) for value in d)
    if len(direction) != dimension:
        raise ValueError("d must have one entry per column of A")
    return all(_dot(row, direction) <= 0 for row in matrix)


def _default_choose(basis, c):
    direction = basis[0]
    if _dot(c, direction) > 0:
        return tuple(-value for value in direction)
    return direction


def _state(matrix, rhs, objective, point):
    indices = tight(matrix, rhs, point)
    return (
        point,
        indices,
        rank(matrix[index] for index in indices),
        _dot(objective, point),
    )


def crash(A, b, c, x, choose=None):
    """Walk to a BFS, or report an unbounded improving ray or a line."""
    matrix, rhs, dimension = _system(A, b)
    objective = tuple(F(value) for value in c)
    point = tuple(F(value) for value in x)
    if len(objective) != dimension or len(point) != dimension:
        raise ValueError("c and x must have one entry per column of A")
    if not _feasible(matrix, rhs, point):
        raise ValueError("crash must start at a feasible point")

    path = [_state(matrix, rhs, objective, point)]
    while True:
        _, indices, current_rank, _ = path[-1]
        if current_rank == dimension:
            return path, "bfs"

        tight_rows = tuple(matrix[index] for index in indices)
        basis = nullspace(tight_rows, dimension)
        direction = tuple(F(value) for value in (
            choose(basis, objective) if choose is not None
            else _default_choose(basis, objective)
        ))
        if len(direction) != dimension or not any(direction):
            raise ValueError("choose must return a nonzero direction")
        if any(_dot(row, direction) != 0 for row in tight_rows):
            raise ValueError("choose must return a tight-row nullspace vector")
        change = _dot(objective, direction)
        if change > 0:
            raise ValueError("choose must not increase the minimization value")

        rates = tuple(_dot(row, direction) for row in matrix)
        blockers = [
            (bound - _dot(row, point)) / rate
            for row, bound, rate in zip(matrix, rhs, rates)
            if rate > 0
        ]
        if not blockers:
            if change < 0:
                return path, "unbounded"
            direction = tuple(-value for value in direction)
            rates = tuple(_dot(row, direction) for row in matrix)
            blockers = [
                (bound - _dot(row, point)) / rate
                for row, bound, rate in zip(matrix, rhs, rates)
                if rate > 0
            ]
            if not blockers:
                return path, "line"

        step = min(blockers)
        if step <= 0:
            raise ArithmeticError("a blocking row must be strictly ahead")
        point = tuple(
            value + step * delta for value, delta in zip(point, direction)
        )
        if not _feasible(matrix, rhs, point):
            raise ArithmeticError("crash stepped outside the polyhedron")
        state = _state(matrix, rhs, objective, point)
        if state[2] <= current_rank:
            raise ArithmeticError("a blocking row did not raise the rank")
        path.append(state)
