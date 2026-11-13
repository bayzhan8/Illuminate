"""Exact primal-dual and Hungarian methods for linear programs."""

from dataclasses import dataclass
from fractions import Fraction

from .lp import F
from .simplex import two_phase


@dataclass(frozen=True)
class HungarianRound:
    u: tuple[Fraction, ...]
    v: tuple[Fraction, ...]
    bound: Fraction
    tight: tuple[tuple[int, int], ...]
    matching: tuple[tuple[int, int], ...]
    S: tuple[int, ...]
    N: tuple[int, ...]
    theta: Fraction | None
    theta_pair: tuple[int, int] | None


@dataclass(frozen=True)
class HungarianResult:
    assignment: dict[int, int]
    cost: Fraction
    u: tuple[Fraction, ...]
    v: tuple[Fraction, ...]
    rounds: tuple[HungarianRound, ...]


@dataclass(frozen=True)
class PrimalDualRound:
    pi: tuple[Fraction, ...]
    tight: tuple[int, ...]
    lambda_: tuple[Fraction, ...] | None
    theta: Fraction | None
    bound: Fraction
    limiting_column: int | None = None


@dataclass(frozen=True)
class PrimalDualResult:
    status: str
    x: tuple[Fraction, ...] | None
    pi: tuple[Fraction, ...]
    value: Fraction | None
    rounds: tuple[PrimalDualRound, ...]
    certificate: tuple[Fraction, ...] = ()


def _dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def _maximum_matching(tight, size):
    adjacency = [[] for _ in range(size)]
    for row, column in tight:
        adjacency[row].append(column)
    for columns in adjacency:
        columns.sort()

    matched_column = {}

    def augment(row, seen):
        for column in adjacency[row]:
            if column in seen:
                continue
            seen.add(column)
            if column not in matched_column \
                    or augment(matched_column[column], seen):
                matched_column[column] = row
                return True
        return False

    for row in range(size):
        augment(row, set())
    return {row: column for column, row in matched_column.items()}


def _obstruction(tight, matching, size):
    matched_row = {row: column for row, column in matching.items()}
    row_for_column = {column: row for row, column in matching.items()}
    rows = {row for row in range(size) if row not in matched_row}
    columns = set()
    frontier = list(sorted(rows))
    adjacency = [[] for _ in range(size)]
    for row, column in tight:
        adjacency[row].append(column)
    for neighbors in adjacency:
        neighbors.sort()

    while frontier:
        row = frontier.pop(0)
        for column in adjacency[row]:
            if matched_row.get(row) == column or column in columns:
                continue
            columns.add(column)
            if column in row_for_column:
                next_row = row_for_column[column]
                if next_row not in rows:
                    rows.add(next_row)
                    frontier.append(next_row)
    return tuple(sorted(rows)), tuple(sorted(columns))


def hungarian(C):
    costs = tuple(tuple(F(value) for value in row) for row in C)
    size = len(costs)
    if size == 0 or any(len(row) != size for row in costs):
        raise ValueError("C must be a nonempty square cost matrix")

    u = tuple(min(row) for row in costs)
    v = (Fraction(0),) * size
    rounds = []
    while True:
        tight = tuple(sorted(
            (row, column)
            for row in range(size)
            for column in range(size)
            if u[row] + v[column] == costs[row][column]
        ))
        matching = _maximum_matching(tight, size)
        matching_pairs = tuple(sorted(matching.items()))
        bound = sum(u, Fraction(0)) + sum(v, Fraction(0))
        if len(matching) == size:
            rounds.append(HungarianRound(
                u, v, bound, tight, matching_pairs, (), (), None, None
            ))
            assignment = dict(matching_pairs)
            cost = sum(
                (costs[row][column]
                 for row, column in assignment.items()),
                Fraction(0),
            )
            return HungarianResult(
                assignment, cost, u, v, tuple(rounds)
            )

        rows, columns = _obstruction(tight, matching, size)
        candidates = [
            (
                costs[row][column] - u[row] - v[column],
                row,
                column,
            )
            for row in rows
            for column in range(size)
            if column not in columns
        ]
        theta, limit_row, limit_column = min(candidates)
        rounds.append(HungarianRound(
            u, v, bound, tight, matching_pairs, rows, columns,
            theta, (limit_row, limit_column),
        ))
        updated_u = list(u)
        updated_v = list(v)
        for row in rows:
            updated_u[row] += theta
        for column in columns:
            updated_v[column] -= theta
        u, v = tuple(updated_u), tuple(updated_v)


def primal_dual(A, b, c, pi):
    matrix = tuple(tuple(F(value) for value in row) for row in A)
    rhs = tuple(F(value) for value in b)
    costs = tuple(F(value) for value in c)
    prices = tuple(F(value) for value in pi)
    if not matrix or not matrix[0] \
            or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("A must be a nonempty rectangular matrix")
    row_count, variable_count = len(matrix), len(matrix[0])
    if len(rhs) != row_count or len(prices) != row_count \
            or len(costs) != variable_count:
        raise ValueError("A, b, c, and pi have incompatible dimensions")
    if any(value < 0 for value in rhs):
        raise ValueError("primal-dual requires b >= 0")

    columns = tuple(
        tuple(matrix[row][column] for row in range(row_count))
        for column in range(variable_count)
    )
    reduced_costs = tuple(
        costs[column] - _dot(columns[column], prices)
        for column in range(variable_count)
    )
    if any(value < 0 for value in reduced_costs):
        raise ValueError("primal_dual requires dual-feasible prices")

    rounds = []
    if not any(rhs):
        tight = tuple(
            column for column, value in enumerate(reduced_costs)
            if value == 0
        )
        point = (Fraction(0),) * variable_count
        bound = _dot(prices, rhs)
        rounds.append(PrimalDualRound(
            prices, tight, None, None, bound
        ))
        return PrimalDualResult(
            "optimal", point, prices, _dot(costs, point), tuple(rounds)
        )

    while True:
        tight = tuple(
            column for column, value in enumerate(reduced_costs)
            if value == 0
        )
        restricted_columns = tight if tight else (None,)
        restricted_A = tuple(
            tuple(
                Fraction(0) if column is None else row[column]
                for column in restricted_columns
            )
            for row in matrix
        )
        restricted = two_phase(
            restricted_A, rhs, (Fraction(0),) * len(restricted_columns),
            rule="bland",
        )
        bound = _dot(prices, rhs)
        if restricted.status == "optimal":
            point = [Fraction(0)] * variable_count
            for index, column in enumerate(tight):
                point[column] = restricted.x[index]
            point = tuple(point)
            rounds.append(PrimalDualRound(
                prices, tight, None, None, bound
            ))
            value = _dot(costs, point)
            if value != bound:
                raise ArithmeticError("tight primal and dual values disagree")
            return PrimalDualResult(
                "optimal", point, prices, value, tuple(rounds)
            )
        if restricted.status != "infeasible":
            raise ArithmeticError(
                f"restricted Phase I ended with status {restricted.status}"
            )

        direction = tuple(-value for value in restricted.certificate)
        if _dot(direction, rhs) <= 0 or any(
                _dot(direction, columns[column]) > 0 for column in tight):
            raise ArithmeticError(
                "restricted Phase I returned an invalid Farkas certificate"
            )
        limiting = [
            column for column in range(variable_count)
            if _dot(direction, columns[column]) > 0
        ]
        if not limiting:
            rounds.append(PrimalDualRound(
                prices, tight, direction, None, bound
            ))
            return PrimalDualResult(
                "infeasible", None, prices, None, tuple(rounds), direction
            )

        ratios = {
            column: reduced_costs[column]
            / _dot(direction, columns[column])
            for column in limiting
        }
        theta = min(ratios.values())
        limiting_column = min(
            column for column, ratio in ratios.items() if ratio == theta
        )
        if theta <= 0:
            raise ArithmeticError("a dual-feasible price update must be positive")
        rounds.append(PrimalDualRound(
            prices, tight, direction, theta, bound, limiting_column
        ))
        prices = tuple(
            price + theta * change
            for price, change in zip(prices, direction)
        )
        reduced_costs = tuple(
            costs[column] - _dot(columns[column], prices)
            for column in range(variable_count)
        )
