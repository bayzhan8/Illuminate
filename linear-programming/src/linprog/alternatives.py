"""Exact alternative theorems built from Fourier–Motzkin elimination."""

from __future__ import annotations

from fractions import Fraction
from typing import TypeAlias

from .elimination import Row, eliminate
from .lp import F

Result: TypeAlias = tuple[str, tuple[Fraction, ...]]


def _matrix(A, b):
    matrix = tuple(tuple(F(value) for value in row) for row in A)
    rhs = tuple(F(value) for value in b)
    if len(matrix) != len(rhs):
        raise ValueError("A and b must have the same number of rows")
    dimension = len(matrix[0]) if matrix else 0
    if any(len(row) != dimension for row in matrix):
        raise ValueError("all rows of A must have the same length")
    return matrix, rhs, dimension


def farkas(A, b) -> Result:
    """Return a feasible x for Ax <= b, or pi >= 0 with pi A = 0, pi b < 0."""
    matrix, rhs, dimension = _matrix(A, b)
    rows = [
        Row(coeffs, bound,
            tuple(F(int(i == j)) for j in range(len(matrix))))
        for i, (coeffs, bound) in enumerate(zip(matrix, rhs))
    ]

    steps = []
    for k in range(dimension - 1, -1, -1):
        steps.append((rows, k))
        rows = eliminate(rows, k)

    contradiction = next((row for row in rows if row.rhs < 0), None)
    if contradiction is not None:
        return "certificate", contradiction.mult

    x: tuple[Fraction, ...] = ()
    for before, k in reversed(steps):
        lower, upper = [], []
        for row in before:
            coefficient = row.coeffs[k]
            residual = row.rhs - sum(
                (row.coeffs[i] * x[i] for i in range(k)), Fraction(0)
            )
            if coefficient > 0:
                upper.append(residual / coefficient)
            elif coefficient < 0:
                lower.append(residual / coefficient)
            elif residual < 0:
                raise ArithmeticError("elimination admitted a false zero row")

        lo = max(lower) if lower else None
        hi = min(upper) if upper else None
        if lo is not None and hi is not None and lo > hi:
            raise ArithmeticError("elimination admitted incompatible bounds")
        value = lo if lo is not None else hi if hi is not None else Fraction(0)
        x += (value,)

    if any(sum((a * value for a, value in zip(row, x)), Fraction(0)) > bound
           for row, bound in zip(matrix, rhs)):
        raise ArithmeticError("back-substitution did not recover a feasible point")
    return "solution", x


def cone_farkas(A, b) -> Result:
    """Return x >= 0 with Ax = b, or y with yA >= 0 and y·b < 0."""
    matrix, rhs, dimension = _matrix(A, b)
    row_count = len(matrix)
    equality_rows = matrix + tuple(
        tuple(-value for value in row) for row in matrix
    )
    equality_rhs = rhs + tuple(-value for value in rhs)
    nonnegative_rows = tuple(
        tuple(F(-int(i == j)) for j in range(dimension))
        for i in range(dimension)
    )
    status, result = farkas(
        equality_rows + nonnegative_rows,
        equality_rhs + (Fraction(0),) * dimension,
    )
    if status == "solution":
        return status, result

    multipliers = result
    y = tuple(
        multipliers[i] - multipliers[row_count + i]
        for i in range(row_count)
    )
    return "certificate", y


def gordan(A) -> Result:
    """Return d with Ad < 0, or pi >= 0, pi != 0, with pi A = 0."""
    matrix = tuple(tuple(F(value) for value in row) for row in A)
    dimension = len(matrix[0]) if matrix else 0
    if any(len(row) != dimension for row in matrix):
        raise ValueError("all rows of A must have the same length")
    status, result = farkas(matrix, (Fraction(-1),) * len(matrix))
    return status, result
