"""Exact basis sensitivity for standard-form linear programs."""

from fractions import Fraction

from .lp import F
from .simplex import dictionary


def _arguments(A, b, c, basis):
    matrix = tuple(tuple(F(value) for value in row) for row in A)
    rhs = tuple(F(value) for value in b)
    objective = tuple(F(value) for value in c)
    basis = tuple(basis)
    state = dictionary(matrix, rhs, objective, basis)
    return matrix, rhs, objective, basis, state


def _optimal_dictionary(A, b, c, basis):
    data = _arguments(A, b, c, basis)
    state = data[-1]
    if any(value < 0 for value in state.x_B) or any(
            value > 0 for value in state.reduced_costs):
        raise ValueError("sensitivity ranges require an optimal basis")
    return data


def _unit(size, index):
    return tuple(Fraction(int(row == index)) for row in range(size))


def basis_inverse(A, b, c, basis):
    matrix, rhs, objective, basis, _ = _arguments(A, b, c, basis)
    size = len(matrix)
    columns = tuple(
        dictionary(matrix, _unit(size, column), objective, basis).x_B
        for column in range(size)
    )
    return tuple(
        tuple(columns[column][row] for column in range(size))
        for row in range(size)
    )


def _range_from_slopes(base_value, values, slopes):
    low = None
    high = None
    for value, slope in zip(values, slopes):
        if slope > 0:
            bound = -value / slope
            low = bound if low is None else max(low, bound)
        elif slope < 0:
            bound = -value / slope
            high = bound if high is None else min(high, bound)
    return (
        None if low is None else base_value + low,
        None if high is None else base_value + high,
    )


def rhs_range(A, b, c, basis, i):
    matrix, rhs, objective, basis, state = _optimal_dictionary(A, b, c, basis)
    if not isinstance(i, int) or not 0 <= i < len(rhs):
        raise ValueError("i must be a valid right-hand-side index")
    inverse = basis_inverse(matrix, rhs, objective, basis)
    slopes = tuple(inverse[row][i] for row in range(len(matrix)))
    return _range_from_slopes(rhs[i], state.x_B, slopes)


def cost_range(A, b, c, basis, j):
    _, _, objective, basis, state = _optimal_dictionary(A, b, c, basis)
    if not isinstance(j, int) or not 0 <= j < len(objective):
        raise ValueError("j must be a valid objective-coefficient index")
    if j not in basis:
        return None, objective[j] - state.reduced_costs[j]
    row = basis.index(j)
    nonbasic = tuple(index for index in range(len(objective))
                     if index not in basis)
    return _range_from_slopes(
        objective[j],
        tuple(-state.reduced_costs[index] for index in nonbasic),
        tuple(state.rows[row][index] for index in nonbasic),
    )


def new_column(A, b, c, basis, column, value):
    matrix, rhs, objective, basis, state = _arguments(A, b, c, basis)
    column = tuple(F(entry) for entry in column)
    if len(column) != len(matrix):
        raise ValueError("column must have one entry per constraint")
    inverse = basis_inverse(matrix, rhs, objective, basis)
    transformed = tuple(
        sum((inverse[row][index] * column[index]
             for index in range(len(matrix))), Fraction(0))
        for row in range(len(matrix))
    )
    reduced_cost = F(value) - sum(
        (state.y[index] * column[index] for index in range(len(matrix))),
        Fraction(0),
    )
    return reduced_cost, transformed
