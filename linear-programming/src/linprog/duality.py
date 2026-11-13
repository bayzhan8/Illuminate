"""Exact duality for linear programs in general row and variable forms."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .lp import F, LP

ROW_SENSES = {"<=", ">=", "="}
VARIABLE_SIGNS = {">=0", "<=0", "free"}


@dataclass(frozen=True)
class GeneralLP:
    sense: str
    c: tuple[Fraction, ...]
    A: tuple[tuple[Fraction, ...], ...]
    rows: tuple[str, ...]
    b: tuple[Fraction, ...]
    signs: tuple[str, ...]

    def __post_init__(self):
        object.__setattr__(self, "c", tuple(map(F, self.c)))
        object.__setattr__(
            self, "A", tuple(tuple(map(F, row)) for row in self.A)
        )
        object.__setattr__(self, "rows", tuple(self.rows))
        object.__setattr__(self, "b", tuple(map(F, self.b)))
        object.__setattr__(self, "signs", tuple(self.signs))

        if self.sense not in {"max", "min"}:
            raise ValueError(f"unknown objective sense: {self.sense}")
        if len(self.A) != len(self.rows) or len(self.rows) != len(self.b):
            raise ValueError("one row sense and right-hand side are required per row")
        if any(len(row) != len(self.c) for row in self.A):
            raise ValueError("each row must have one coefficient per variable")
        if len(self.signs) != len(self.c):
            raise ValueError("one sign is required per variable")
        if any(row not in ROW_SENSES for row in self.rows):
            raise ValueError(f"row senses must be one of {sorted(ROW_SENSES)}")
        if any(sign not in VARIABLE_SIGNS for sign in self.signs):
            raise ValueError(
                f"variable signs must be one of {sorted(VARIABLE_SIGNS)}"
            )


def dual(p: GeneralLP) -> GeneralLP:
    """Return the exact dual, using the row and variable sign table."""
    is_max = p.sense == "max"
    row_sign = (
        {"<=": ">=0", ">=": "<=0", "=": "free"}
        if is_max
        else {"<=": "<=0", ">=": ">=0", "=": "free"}
    )
    column_sense = (
        {">=0": ">=", "<=0": "<=", "free": "="}
        if is_max
        else {">=0": "<=", "<=0": ">=", "free": "="}
    )
    return GeneralLP(
        sense="min" if is_max else "max",
        c=p.b,
        A=tuple(tuple(p.A[i][j] for i in range(len(p.rows)))
                for j in range(len(p.c))),
        rows=tuple(column_sense[sign] for sign in p.signs),
        b=p.c,
        signs=tuple(row_sign[row] for row in p.rows),
    )


def to_canonical(p: GeneralLP) -> LP:
    """Rewrite a general LP as a maximization with ``A x <= b, x >= 0``."""
    direction = Fraction(1) if p.sense == "max" else Fraction(-1)
    columns = []
    names = []
    objective = []
    for j, sign in enumerate(p.signs):
        if sign == ">=0":
            choices = ((Fraction(1), f"x{j}"),)
        elif sign == "<=0":
            choices = ((Fraction(-1), f"-x{j}"),)
        else:
            choices = ((Fraction(1), f"x{j}+"),
                       (Fraction(-1), f"x{j}-"))
        for factor, name in choices:
            columns.append((j, factor))
            names.append(name)
            objective.append(direction * factor * p.c[j])

    rows = []
    for coefficients, sense, bound in zip(p.A, p.rows, p.b):
        if sense == "<=":
            rows.append((coefficients, bound))
        elif sense == ">=":
            rows.append((tuple(-value for value in coefficients), -bound))
        else:
            rows.append((coefficients, bound))
            rows.append((tuple(-value for value in coefficients), -bound))

    matrix = tuple(tuple(row[j] * factor for j, factor in columns)
                   for row, _ in rows)
    bounds = tuple(bound for _, bound in rows)
    return LP.build(objective, matrix, bounds, var_names=names)
