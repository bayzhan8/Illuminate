"""Exact Fourier–Motzkin elimination with row provenance."""

from dataclasses import dataclass
from fractions import Fraction
from typing import Iterable


def _fraction(value) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(
        str(value) if isinstance(value, float) else value
    )


@dataclass(frozen=True)
class Row:
    coeffs: tuple[Fraction, ...]
    rhs: Fraction
    mult: tuple[Fraction, ...]

    def __post_init__(self):
        object.__setattr__(self, "coeffs", tuple(map(_fraction, self.coeffs)))
        object.__setattr__(self, "rhs", _fraction(self.rhs))
        object.__setattr__(self, "mult", tuple(map(_fraction, self.mult)))


def _validated(rows: Iterable[Row]) -> tuple[list[Row], int, int]:
    rows = list(rows)
    if not rows:
        return rows, 0, 0
    dimension = len(rows[0].coeffs)
    original_count = len(rows[0].mult)
    if any(len(row.coeffs) != dimension or len(row.mult) != original_count
           for row in rows):
        raise ValueError("all rows must have the same coefficient and multiplier lengths")
    return rows, dimension, original_count


def eliminate(rows: Iterable[Row], k: int) -> list[Row]:
    """Eliminate coefficient ``k``, retaining zero rows before upper/lower pairs.

    A positive coefficient is an upper bound and a negative coefficient is a
    lower bound. Each pair is added with positive factors that cancel the
    eliminated coefficient; no rows are normalized or pruned.
    """
    rows, dimension, _ = _validated(rows)
    if not rows:
        return []
    if not isinstance(k, int) or not 0 <= k < dimension:
        raise IndexError("elimination index is outside the row dimension")

    zero, upper, lower = [], [], []
    for row in rows:
        coefficient = row.coeffs[k]
        if coefficient > 0:
            upper.append(row)
        elif coefficient < 0:
            lower.append(row)
        else:
            zero.append(row)

    remaining = tuple(i for i in range(dimension) if i != k)
    result = [
        Row(tuple(row.coeffs[i] for i in remaining), row.rhs, row.mult)
        for row in zero
    ]
    for upper_row in upper:
        upper_coefficient = upper_row.coeffs[k]
        for lower_row in lower:
            lower_coefficient = lower_row.coeffs[k]
            upper_factor = -lower_coefficient
            lower_factor = upper_coefficient
            coeffs = tuple(
                upper_factor * upper_row.coeffs[i]
                + lower_factor * lower_row.coeffs[i]
                for i in remaining
            )
            rhs = upper_factor * upper_row.rhs + lower_factor * lower_row.rhs
            mult = tuple(
                upper_factor * upper_multiplier
                + lower_factor * lower_multiplier
                for upper_multiplier, lower_multiplier
                in zip(upper_row.mult, lower_row.mult)
            )
            result.append(Row(coeffs, rhs, mult))
    return result


def project(rows: Iterable[Row], keep: Iterable[int]) -> list[Row]:
    """Eliminate every variable not in ``keep`` and order columns as requested."""
    rows, dimension, _ = _validated(rows)
    if not rows:
        return []

    if isinstance(keep, (set, frozenset)):
        keep = tuple(sorted(keep))
    else:
        keep = tuple(keep)
    if any(not isinstance(index, int) or not 0 <= index < dimension
           for index in keep):
        raise IndexError("kept index is outside the row dimension")
    if len(set(keep)) != len(keep):
        raise ValueError("kept indices must be unique")

    kept = set(keep)
    current = list(range(dimension))
    for original_index in range(dimension):
        if original_index not in kept:
            position = current.index(original_index)
            rows = eliminate(rows, position)
            current.pop(position)

    if current != list(keep):
        order = tuple(current.index(index) for index in keep)
        rows = [
            Row(tuple(row.coeffs[i] for i in order), row.rhs, row.mult)
            for row in rows
        ]
    return rows
