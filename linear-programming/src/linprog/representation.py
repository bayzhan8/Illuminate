"""Exact conversions between row and corner-plus-ray representations."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import gcd, lcm

from .corners import basic_points, is_direction, nullspace, rank, tight
from .elimination import Row, project
from .lp import F


def _matrix(A):
    matrix = tuple(tuple(F(value) for value in row) for row in A)
    if not matrix:
        raise ValueError("A must contain at least one row")
    dimension = len(matrix[0])
    if dimension == 0 or any(len(row) != dimension for row in matrix):
        raise ValueError("all rows must have the same positive length")
    return matrix, dimension


def _dot(row, point):
    return sum((a * x for a, x in zip(row, point)), Fraction(0))


def recession_cone(A):
    """Return the rows and zero bounds defining {d : A d <= 0}."""
    matrix, _ = _matrix(A)
    return matrix, (Fraction(0),) * len(matrix)


@dataclass(frozen=True)
class DecompositionStep:
    point: tuple[Fraction, ...]
    direction: tuple[Fraction, ...]
    positive_step: Fraction
    negative_step: Fraction | None
    positive_point: tuple[Fraction, ...]
    negative_point: tuple[Fraction, ...] | None


def _primitive(vector):
    denominator = lcm(*(value.denominator for value in vector))
    integers = [int(value * denominator) for value in vector]
    divisor = gcd(*(abs(value) for value in integers))
    return tuple(Fraction(value // divisor) for value in integers)


def _positive_orientation(vector):
    vector = _primitive(vector)
    first = next(value for value in vector if value)
    return vector if first > 0 else tuple(-value for value in vector)


def _ordered_nullspace(tight_rows, dimension):
    basis = nullspace(tight_rows, dimension)
    if not tight_rows and dimension > 1:
        first = tuple(sum((vector[index] for vector in basis), Fraction(0))
                      for index in range(dimension))
        return (first,) + basis[1:]
    return basis


def _limit(matrix, rhs, point, direction):
    distances = [
        (bound - _dot(row, point)) / rate
        for row, bound in zip(matrix, rhs)
        if (rate := _dot(row, direction)) > 0
    ]
    return min(distances) if distances else None


def _advance(point, direction, step):
    return tuple(value + step * delta
                 for value, delta in zip(point, direction))


def _combine(first, second, first_weight, second_weight):
    result = {}
    for decomposition, factor in ((first, first_weight),
                                  (second, second_weight)):
        for point, weight in decomposition.items():
            result[point] = result.get(point, Fraction(0)) + factor * weight
    return {point: weight for point, weight in result.items() if weight}


def decompose(A, b, x, choose=None):
    """Write a feasible point as a corner mixture plus a recession direction.

    ``choose`` receives the current nullspace basis and returns a nonzero
    direction from its span. The result is ``((weights, d), steps)``, with
    ``weights`` mapping corner points to exact convex weights.
    """
    matrix, dimension = _matrix(A)
    rhs = tuple(F(value) for value in b)
    point = tuple(F(value) for value in x)
    if len(rhs) != len(matrix):
        raise ValueError("A and b must have the same number of rows")
    if len(point) != dimension:
        raise ValueError("x must have one entry per column of A")
    if any(_dot(row, point) > bound for row, bound in zip(matrix, rhs)):
        raise ValueError("decompose must start at a feasible point")
    if rank(matrix) != dimension:
        raise ValueError("decompose requires a pointed polyhedron")

    steps = []
    zero = (Fraction(0),) * dimension

    def visit(current):
        indices = tight(matrix, rhs, current)
        tight_rows = tuple(matrix[index] for index in indices)
        current_rank = rank(tight_rows)
        if current_rank == dimension:
            return {current: Fraction(1)}, zero

        basis = _ordered_nullspace(tight_rows, dimension)
        if not basis:
            raise ArithmeticError("a non-corner must have a free direction")
        if choose is None:
            direction = _positive_orientation(basis[0])
        else:
            direction = tuple(F(value) for value in choose(basis))
        if len(direction) != dimension or not any(direction):
            raise ValueError("choose must return a nonzero direction")
        if any(_dot(row, direction) != 0 for row in tight_rows):
            raise ValueError("choose must return a tight-row nullspace vector")

        positive = _limit(matrix, rhs, current, direction)
        negative_direction = tuple(-value for value in direction)
        negative = _limit(matrix, rhs, current, negative_direction)
        if positive is None and negative is None:
            raise ValueError("decompose requires a pointed polyhedron")
        if positive is None:
            direction = negative_direction
            positive, negative = negative, None
        positive_point = _advance(current, direction, positive)
        negative_point = (
            _advance(current, tuple(-value for value in direction), negative)
            if negative is not None else None
        )
        endpoints = (positive_point,) + (
            (negative_point,) if negative_point is not None else ()
        )
        if any(rank(matrix[index] for index in tight(matrix, rhs, endpoint))
               <= current_rank for endpoint in endpoints):
            raise ArithmeticError("a blocking row did not raise the rank")

        steps.append(DecompositionStep(
            current, direction, positive, negative,
            positive_point, negative_point,
        ))
        positive_weights, positive_ray = visit(positive_point)
        if negative_point is None:
            ray = tuple(
                positive_ray[index] - positive * direction[index]
                for index in range(dimension)
            )
            return positive_weights, ray

        negative_weights, negative_ray = visit(negative_point)
        total = positive + negative
        positive_weight = negative / total
        negative_weight = positive / total
        weights = _combine(
            positive_weights, negative_weights,
            positive_weight, negative_weight,
        )
        ray = tuple(
            positive_weight * positive_ray[index]
            + negative_weight * negative_ray[index]
            for index in range(dimension)
        )
        return weights, ray

    weights, direction = visit(point)
    if sum(weights.values(), Fraction(0)) != 1 or \
            any(weight < 0 for weight in weights.values()):
        raise ArithmeticError("corner weights must form a convex combination")
    if not is_direction(matrix, direction):
        raise ArithmeticError("the remainder must be a recession direction")
    reconstructed = tuple(
        sum((weight * corner[index] for corner, weight in weights.items()),
            Fraction(0)) + direction[index]
        for index in range(dimension)
    )
    if reconstructed != point:
        raise ArithmeticError("corner and ray terms do not reconstruct x")
    return (weights, direction), tuple(steps)


def _primitive_ray(point):
    return _primitive(point)


def extreme_rays(A):
    """Return primitive integer generators of the cone's extreme rays."""
    matrix, dimension = _matrix(A)
    if rank(matrix) != dimension:
        raise ValueError("extreme rays require a pointed cone")
    normal = tuple(
        -sum((row[index] for row in matrix), Fraction(0))
        for index in range(dimension)
    )
    if not any(normal):
        return ()

    slice_A = matrix + (normal, tuple(-value for value in normal))
    slice_b = (Fraction(0),) * len(matrix) + (Fraction(1), Fraction(-1))
    points = basic_points(slice_A, slice_b)
    rays = {
        _primitive_ray(point)
        for point, feasible in points
        if feasible and any(point)
    }
    return tuple(sorted(rays))


def _normalized_rows(rows):
    normalized = {}
    for row in rows:
        if not any(row.coeffs):
            if row.rhs < 0:
                raise ArithmeticError("projection unexpectedly became empty")
            continue
        first = next(value for value in row.coeffs if value)
        factor = Fraction(1, 1) / abs(first)
        candidate = Row(
            tuple(factor * value for value in row.coeffs),
            factor * row.rhs,
            tuple(factor * value for value in row.mult),
        )
        previous = normalized.get(candidate.coeffs)
        if previous is None or candidate.rhs < previous.rhs:
            normalized[candidate.coeffs] = candidate
    return list(normalized.values())


def _redundant(rows, index):
    candidate = rows[index]
    others = rows[:index] + rows[index + 1:]
    if not others:
        return False
    matrix = tuple(row.coeffs for row in others)
    if rank(matrix) < len(candidate.coeffs):
        return False
    rhs = tuple(row.rhs for row in others)
    corners = tuple(
        point for point, feasible in basic_points(matrix, rhs) if feasible
    )
    if not corners:
        return False
    rays = extreme_rays(matrix)
    return (
        all(_dot(candidate.coeffs, point) <= candidate.rhs for point in corners)
        and all(_dot(candidate.coeffs, ray) <= 0 for ray in rays)
    )


def _irredundant(rows):
    rows = _normalized_rows(rows)
    while True:
        for index in range(len(rows)):
            if _redundant(rows, index):
                rows.pop(index)
                break
        else:
            return rows


def _facet_rows(vertices, rays, projected):
    dimension = len(vertices[0])
    spanning = tuple(
        tuple(point[index] - vertices[0][index] for index in range(dimension))
        for point in vertices[1:]
    ) + rays
    if rank(spanning) < dimension:
        return None

    facets = {}
    for anchor in vertices:
        tangents = [
            tuple(point[index] - anchor[index] for index in range(dimension))
            for point in vertices if point != anchor
        ] + list(rays)
        tangents = [vector for vector in tangents if any(vector)]
        for subset in combinations(tangents, dimension - 1):
            if rank(subset) != dimension - 1:
                continue
            basis = nullspace(subset, dimension)
            if len(basis) != 1:
                continue
            normal = _positive_orientation(basis[0])
            for signed_normal in (normal, tuple(-value for value in normal)):
                bound = _dot(signed_normal, anchor)
                if (all(_dot(signed_normal, point) <= bound
                        for point in vertices)
                        and all(_dot(signed_normal, ray) <= 0
                                for ray in rays)):
                    first = next(value for value in signed_normal if value)
                    factor = Fraction(1, 1) / abs(first)
                    coefficients = tuple(factor * value
                                         for value in signed_normal)
                    facets[coefficients] = (
                        coefficients, factor * bound,
                    )
                    break

    by_signature = {
        (row.coeffs, row.rhs): row for row in _normalized_rows(projected)
    }
    if any(signature not in by_signature for signature in facets.values()):
        return None
    return [by_signature[signature] for signature in facets.values()]


def weyl(V, R):
    """Project a convex hull plus a finitely generated cone to its row form."""
    vertices = tuple(tuple(F(value) for value in point) for point in V)
    rays = tuple(tuple(F(value) for value in ray) for ray in R)
    if not vertices:
        raise ValueError("V must contain at least one point")
    dimension = len(vertices[0])
    if dimension == 0 or any(len(point) != dimension for point in vertices) \
            or any(len(ray) != dimension for ray in rays):
        raise ValueError("all generators must have the same positive dimension")

    vertex_count, ray_count = len(vertices), len(rays)
    auxiliary_count = vertex_count + ray_count
    variable_count = auxiliary_count + dimension
    source_count = 2 * dimension + 2 + auxiliary_count
    rows = []

    def add(coefficients, rhs):
        index = len(rows)
        multipliers = tuple(
            Fraction(int(index == source)) for source in range(source_count)
        )
        rows.append(Row(coefficients, rhs, multipliers))

    for coordinate in range(dimension):
        equation = [Fraction(0)] * variable_count
        for index, point in enumerate(vertices):
            equation[index] = -point[coordinate]
        for index, ray in enumerate(rays):
            equation[vertex_count + index] = -ray[coordinate]
        equation[auxiliary_count + coordinate] = Fraction(1)
        add(tuple(equation), Fraction(0))
        add(tuple(-value for value in equation), Fraction(0))

    lambda_sum = tuple(
        Fraction(1) if index < vertex_count else Fraction(0)
        for index in range(variable_count)
    )
    add(lambda_sum, Fraction(1))
    add(tuple(-value for value in lambda_sum), Fraction(-1))
    for index in range(auxiliary_count):
        row = [Fraction(0)] * variable_count
        row[index] = Fraction(-1)
        add(tuple(row), Fraction(0))

    projected = project(rows, range(auxiliary_count, variable_count))
    facets = _facet_rows(vertices, rays, projected)
    return facets if facets is not None else _irredundant(projected)
