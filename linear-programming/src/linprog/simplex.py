"""Exact tableau dictionaries and simplex walks for standard-form LPs."""

from dataclasses import dataclass
from fractions import Fraction
from typing import NamedTuple

from .corners import rank
from .lp import F


class Dictionary(NamedTuple):
    x_B: tuple[Fraction, ...]
    y: tuple[Fraction, ...]
    reduced_costs: tuple[Fraction, ...]
    rows: tuple[tuple[Fraction, ...], ...]


@dataclass(frozen=True)
class PivotResult:
    status: str
    entering: int | None = None
    ratios: tuple[Fraction | None, ...] = ()
    leaving: int | None = None
    theta: Fraction | None = None
    ray: tuple[Fraction, ...] | None = None


@dataclass(frozen=True)
class SimplexIteration:
    basis: tuple[int, ...]
    dictionary: Dictionary
    x: tuple[Fraction, ...]
    value: Fraction
    pivot: PivotResult


@dataclass(frozen=True)
class SimplexResult:
    steps: tuple[SimplexIteration, ...]
    status: str
    certificate: tuple[Fraction, ...]
    basis: tuple[int, ...]
    x: tuple[Fraction, ...]
    value: Fraction


@dataclass(frozen=True)
class TwoPhaseResult:
    status: str
    phase1: SimplexResult
    phase2: SimplexResult | None
    certificate: tuple[Fraction, ...]
    basis: tuple[int, ...]
    x: tuple[Fraction, ...]
    value: Fraction
    artificial_indices: tuple[int, ...]
    artificial_rows: tuple[int, ...]


def _system(A, b, c):
    matrix = tuple(tuple(F(value) for value in row) for row in A)
    rhs = tuple(F(value) for value in b)
    objective = tuple(F(value) for value in c)
    if not matrix:
        raise ValueError("A must contain at least one equation")
    dimension = len(matrix[0])
    if dimension == 0 or any(len(row) != dimension for row in matrix):
        raise ValueError("all rows of A must have the same positive length")
    if len(rhs) != len(matrix) or len(objective) != dimension:
        raise ValueError("A, b, and c have incompatible dimensions")
    if rank(matrix) != len(matrix):
        raise ValueError("the rows of A must be independent")
    return matrix, rhs, objective, len(matrix), dimension


def _inverse(matrix):
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("the basis matrix must be square")
    augmented = [
        list(row) + [F(int(i == j)) for j in range(size)]
        for i, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size)
             if augmented[row][column] != 0),
            None,
        )
        if pivot is None:
            raise ValueError("basis matrix is singular")
        augmented[column], augmented[pivot] = (
            augmented[pivot], augmented[column]
        )
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            factor = augmented[row][column]
            if factor:
                augmented[row] = [
                    value - factor * pivot_value
                    for value, pivot_value
                    in zip(augmented[row], augmented[column])
                ]
    return tuple(tuple(row[size:]) for row in augmented)


def _dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def dictionary(A, b, c, basis):
    matrix, rhs, objective, row_count, variable_count = _system(A, b, c)
    basis = tuple(basis)
    if len(basis) != row_count or len(set(basis)) != row_count \
            or any(not isinstance(index, int)
                   or not 0 <= index < variable_count for index in basis):
        raise ValueError("basis must contain one distinct column per row")
    basis_matrix = tuple(
        tuple(matrix[row][column] for column in basis)
        for row in range(row_count)
    )
    inverse = _inverse(basis_matrix)
    rows = tuple(
        tuple(
            sum((inverse[row][k] * matrix[k][column]
                 for k in range(row_count)), Fraction(0))
            for column in range(variable_count)
        )
        for row in range(row_count)
    )
    x_B = tuple(
        sum((inverse[row][k] * rhs[k] for k in range(row_count)),
            Fraction(0))
        for row in range(row_count)
    )
    y = tuple(
        sum((objective[basis[row]] * inverse[row][column]
             for row in range(row_count)), Fraction(0))
        for column in range(row_count)
    )
    reduced_costs = tuple(
        objective[column] - sum(
            (y[row] * matrix[row][column] for row in range(row_count)),
            Fraction(0),
        )
        for column in range(variable_count)
    )
    return Dictionary(x_B, y, reduced_costs, rows)


def _choose_entering(reduced_costs, basis, rule):
    if rule not in {"dantzig", "bland"}:
        raise ValueError("rule must be 'dantzig' or 'bland'")
    basic = set(basis)
    eligible = [
        index for index, cost in enumerate(reduced_costs)
        if index not in basic and cost > 0
    ]
    if not eligible:
        return None
    if rule == "bland":
        return min(eligible)
    return min(eligible, key=lambda index: (-reduced_costs[index], index))


def _full_point(x_B, basis, variable_count):
    point = [Fraction(0)] * variable_count
    for index, value in zip(basis, x_B):
        point[index] = value
    return tuple(point)


def pivot_step(A, b, c, basis, rule="dantzig"):
    matrix, rhs, objective, row_count, variable_count = _system(A, b, c)
    basis = tuple(basis)
    state = dictionary(matrix, rhs, objective, basis)
    if any(value < 0 for value in state.x_B):
        raise ValueError("pivot_step requires a feasible basis")
    entering = _choose_entering(state.reduced_costs, basis, rule)
    if entering is None:
        return PivotResult("optimal")

    column = tuple(row[entering] for row in state.rows)
    ratios = tuple(
        state.x_B[row] / coefficient if coefficient > 0 else None
        for row, coefficient in enumerate(column)
    )
    limiting = [
        row for row, ratio in enumerate(ratios) if ratio is not None
    ]
    if not limiting:
        ray = [Fraction(0)] * variable_count
        ray[entering] = Fraction(1)
        for row, basic in enumerate(basis):
            ray[basic] = -column[row]
        return PivotResult("unbounded", entering=entering,
                           ratios=ratios, ray=tuple(ray))

    leaving_row = min(limiting, key=lambda row: (ratios[row], basis[row]))
    return PivotResult(
        "pivot", entering, ratios, basis[leaving_row], ratios[leaving_row]
    )


def simplex(A, b, c, basis, rule="dantzig"):
    matrix, rhs, objective, row_count, variable_count = _system(A, b, c)
    basis = tuple(basis)
    if len(basis) != row_count or len(set(basis)) != row_count \
            or any(not isinstance(index, int)
                   or not 0 <= index < variable_count for index in basis):
        raise ValueError("basis must contain one distinct column per row")
    steps = []
    visited = set()
    while True:
        if basis in visited:
            raise RuntimeError("simplex repeated a basis; try Bland's rule")
        visited.add(basis)
        state = dictionary(matrix, rhs, objective, basis)
        if any(value < 0 for value in state.x_B):
            raise ValueError("simplex must start from a feasible basis")
        point = _full_point(state.x_B, basis, variable_count)
        value = _dot(objective, point)
        pivot = pivot_step(matrix, rhs, objective, basis, rule)
        steps.append(SimplexIteration(basis, state, point, value, pivot))
        if pivot.status == "optimal":
            return SimplexResult(
                tuple(steps), "optimal", state.y, basis, point, value
            )
        if pivot.status == "unbounded":
            return SimplexResult(
                tuple(steps), "unbounded", pivot.ray, basis, point, value
            )
        basis = tuple(
            pivot.entering if basic == pivot.leaving else basic
            for basic in basis
        )


def two_phase(A, b, c, rule="dantzig"):
    matrix, rhs, objective, row_count, variable_count = _system(A, b, c)
    signs = tuple(F(-1) if value < 0 else F(1) for value in rhs)
    normalized_A = tuple(
        tuple(sign * value for value in row)
        for sign, row in zip(signs, matrix)
    )
    normalized_b = tuple(sign * value for sign, value in zip(signs, rhs))

    natural_basis = [None] * row_count
    for row in range(row_count):
        for column in range(variable_count):
            if all(
                normalized_A[index][column] == F(int(index == row))
                for index in range(row_count)
            ):
                natural_basis[row] = column
                break

    artificial_rows = tuple(
        row for row, column in enumerate(natural_basis) if column is None
    )
    artificial_indices = tuple(
        variable_count + index for index in range(len(artificial_rows))
    )
    augmented_A = tuple(
        tuple(row) + tuple(F(int(row_index == artificial_row))
                           for artificial_row in artificial_rows)
        for row_index, row in enumerate(normalized_A)
    )
    basis = tuple(
        column if column is not None
        else artificial_indices[artificial_rows.index(row)]
        for row, column in enumerate(natural_basis)
    )
    phase1_c = (Fraction(0),) * variable_count + \
        (Fraction(-1),) * len(artificial_indices)
    phase1 = simplex(augmented_A, normalized_b, phase1_c, basis, rule)
    if phase1.status != "optimal":
        raise ArithmeticError("Phase I objective unexpectedly became unbounded")

    if phase1.value < 0:
        certificate = tuple(
            sign * value
            for sign, value in zip(signs, phase1.certificate)
        )
        return TwoPhaseResult(
            "infeasible", phase1, None, certificate, phase1.basis,
            phase1.x[:variable_count], phase1.value,
            artificial_indices, artificial_rows,
        )
    if phase1.value > 0:
        raise ArithmeticError("Phase I objective must not exceed zero")

    basis = list(phase1.basis)
    while any(column in artificial_indices for column in basis):
        state = dictionary(augmented_A, normalized_b, phase1_c, basis)
        row = next(index for index, column in enumerate(basis)
                   if column in artificial_indices)
        if state.x_B[row] != 0:
            raise ArithmeticError("a positive artificial variable survived Phase I")
        basic = set(basis)
        entering = next(
            (column for column in range(variable_count)
             if column not in basic and state.rows[row][column] != 0),
            None,
        )
        if entering is None:
            raise ArithmeticError("independent equations must pivot out artificials")
        basis[row] = entering

    phase2 = simplex(normalized_A, normalized_b, objective, basis, rule)
    certificate = phase2.certificate
    if phase2.status == "optimal":
        certificate = tuple(
            sign * value for sign, value in zip(signs, certificate)
        )
    return TwoPhaseResult(
        phase2.status, phase1, phase2, certificate, phase2.basis,
        phase2.x, phase2.value, artificial_indices, artificial_rows,
    )
