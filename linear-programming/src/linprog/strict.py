"""Exact strictly complementary optimal pairs for inequality-form LPs."""

from dataclasses import dataclass
from fractions import Fraction

from .lp import F
from .simplex import two_phase


@dataclass(frozen=True)
class StrictPair:
    x: tuple[Fraction, ...]
    y: tuple[Fraction, ...]
    plan_witnesses: tuple[tuple[Fraction, ...] | None, ...]
    price_witnesses: tuple[tuple[Fraction, ...] | None, ...]


def _dot(left, right):
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def _positive_witness(result, score, description, gain_score=None):
    if result.status == "optimal":
        if score(result.x) > 0:
            return result.x
        if score(result.x) < 0:
            raise ArithmeticError(f"{description} has a negative maximum")
        return None

    if result.status == "unbounded":
        point = result.x
        ray = result.certificate
        initial = score(point)
        gain = (gain_score or score)(ray)
        if initial > 0:
            return point
        if gain <= 0:
            raise ArithmeticError(f"{description} has no improving ray")
        amount = -initial / gain + 1
        witness = tuple(
            value + amount * change for value, change in zip(point, ray)
        )
        if score(witness) <= 0:
            raise ArithmeticError(f"{description} ray did not give a witness")
        return witness

    raise ArithmeticError(
        f"{description} ended with status {result.status}"
    )


def _average(points, fallback):
    points = tuple(point for point in points if point is not None)
    if not points:
        return fallback
    return tuple(
        sum((point[index] for point in points), Fraction(0)) / len(points)
        for index in range(len(fallback))
    )


def _validate_plan(matrix, rhs, costs, value, point):
    if any(entry < 0 for entry in point):
        raise ArithmeticError("a plan witness is not nonnegative")
    if any(_dot(row, point) > bound
           for row, bound in zip(matrix, rhs)):
        raise ArithmeticError("a plan witness is not feasible")
    if _dot(costs, point) != value:
        raise ArithmeticError("a plan witness is not optimal")


def _validate_price(matrix, rhs, costs, value, point):
    if any(entry < 0 for entry in point):
        raise ArithmeticError("a price witness is not nonnegative")
    columns = tuple(
        tuple(matrix[row][column] for row in range(len(matrix)))
        for column in range(len(costs))
    )
    if any(_dot(point, column) < cost
           for column, cost in zip(columns, costs)):
        raise ArithmeticError("a price witness is not fair")
    if _dot(point, rhs) != value:
        raise ArithmeticError("a price witness is not optimal")


def strict_pair(A, b, c):
    """Return an exactly complementary optimal pair and its witnesses."""
    matrix = tuple(tuple(F(value) for value in row) for row in A)
    rhs = tuple(F(value) for value in b)
    costs = tuple(F(value) for value in c)
    if not matrix or not matrix[0] \
            or any(len(row) != len(matrix[0]) for row in matrix):
        raise ValueError("A must be a nonempty rectangular matrix")
    row_count, variable_count = len(matrix), len(matrix[0])
    if len(rhs) != row_count or len(costs) != variable_count:
        raise ValueError("A, b, and c have incompatible dimensions")

    primal_matrix = tuple(
        tuple(row) + tuple(F(int(index == row_index))
                           for index in range(row_count))
        for row_index, row in enumerate(matrix)
    )
    primal_costs = costs + (Fraction(0),) * row_count
    optimum = two_phase(primal_matrix, rhs, primal_costs, rule="bland")
    if optimum.status != "optimal":
        raise ValueError("strict_pair requires a finite primal optimum")
    value = optimum.value
    initial_plan = optimum.x[:variable_count]
    initial_price = optimum.certificate
    if len(initial_price) != row_count:
        raise ArithmeticError("the primal solve returned an invalid price")
    _validate_plan(matrix, rhs, costs, value, initial_plan)
    _validate_price(matrix, rhs, costs, value, initial_price)

    plan_variables = variable_count + row_count + 1
    plan_rows = tuple(
        tuple(row)
        + tuple(F(int(index == row_index))
                for index in range(row_count))
        + (Fraction(0),)
        for row_index, row in enumerate(matrix)
    ) + (
        tuple(-coefficient for coefficient in costs)
        + (Fraction(0),) * row_count + (Fraction(1),),
    )
    plan_rhs = rhs + (-value,)

    price_variables = row_count + variable_count + 1
    price_rows = tuple(
        tuple(matrix[row][column] for row in range(row_count))
        + tuple(-F(int(index == column))
                for index in range(variable_count))
        + (Fraction(0),)
        for column in range(variable_count)
    ) + (
        rhs + (Fraction(0),) * variable_count + (Fraction(1),),
    )
    price_rhs = costs + (value,)

    plan_witnesses = [None] * (row_count + variable_count)
    price_witnesses = [None] * (row_count + variable_count)

    for row_index in range(row_count):
        objective = [Fraction(0)] * plan_variables
        objective[variable_count + row_index] = Fraction(1)
        result = two_phase(
            plan_rows, plan_rhs, objective, rule="bland"
        )
        witness = _positive_witness(
            result,
            lambda point, index=variable_count + row_index: point[index],
            f"slack row {row_index}",
        )
        if witness is not None:
            point = witness[:variable_count]
            _validate_plan(matrix, rhs, costs, value, point)
            if rhs[row_index] - _dot(matrix[row_index], point) <= 0:
                raise ArithmeticError("a row plan witness is not slack")
            plan_witnesses[row_index] = point
        else:
            objective = [Fraction(0)] * price_variables
            objective[row_index] = Fraction(1)
            result = two_phase(
                price_rows, price_rhs, objective, rule="bland"
            )
            witness = _positive_witness(
                result,
                lambda point, index=row_index: point[index],
                f"price row {row_index}",
            )
            if witness is None:
                raise ArithmeticError(
                    f"row {row_index} has no strict-complementarity witness"
                )
            point = witness[:row_count]
            _validate_price(matrix, rhs, costs, value, point)
            if point[row_index] <= 0:
                raise ArithmeticError("a row price witness is not positive")
            price_witnesses[row_index] = point

    for column in range(variable_count):
        objective = [Fraction(0)] * plan_variables
        objective[column] = Fraction(1)
        result = two_phase(
            plan_rows, plan_rhs, objective, rule="bland"
        )
        witness = _positive_witness(
            result,
            lambda point, index=column: point[index],
            f"plan column {column}",
        )
        witness_index = row_count + column
        if witness is not None:
            point = witness[:variable_count]
            _validate_plan(matrix, rhs, costs, value, point)
            if point[column] <= 0:
                raise ArithmeticError("a column plan witness is not positive")
            plan_witnesses[witness_index] = point
        else:
            objective = (
                tuple(matrix[row][column] for row in range(row_count))
                + (Fraction(0),) * (variable_count + 1)
            )
            result = two_phase(
                price_rows, price_rhs, objective, rule="bland"
            )
            witness = _positive_witness(
                result,
                lambda point, index=column: (
                    _dot(
                        tuple(matrix[row][index]
                              for row in range(row_count)),
                        point[:row_count],
                    ) - costs[index]
                ),
                f"loss column {column}",
                gain_score=lambda point, index=column: _dot(
                    tuple(matrix[row][index]
                          for row in range(row_count)),
                    point[:row_count],
                ),
            )
            if witness is None:
                raise ArithmeticError(
                    f"column {column} has no strict-complementarity witness"
                )
            point = witness[:row_count]
            _validate_price(matrix, rhs, costs, value, point)
            loss = sum(
                (point[row] * matrix[row][column]
                 for row in range(row_count)),
                Fraction(0),
            ) - costs[column]
            if loss <= 0:
                raise ArithmeticError("a column loss witness is not positive")
            price_witnesses[witness_index] = point

    plan_points = tuple(
        point for point in plan_witnesses if point is not None
    )
    price_points = tuple(
        point for point in price_witnesses if point is not None
    )
    x = _average(plan_points, initial_plan)
    y = _average(price_points, initial_price)
    _validate_plan(matrix, rhs, costs, value, x)
    _validate_price(matrix, rhs, costs, value, y)

    for row_index, row in enumerate(matrix):
        slack = rhs[row_index] - _dot(row, x)
        if (slack > 0) == (y[row_index] > 0):
            raise ArithmeticError("a row is not strictly complementary")
    for column in range(variable_count):
        loss = sum(
            (y[row] * matrix[row][column] for row in range(row_count)),
            Fraction(0),
        ) - costs[column]
        if (x[column] > 0) == (loss > 0):
            raise ArithmeticError("a column is not strictly complementary")

    return StrictPair(
        x, y, tuple(plan_witnesses), tuple(price_witnesses)
    )
