"""Exact checks for the chapter 6 duality examples and sign table."""

import random
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from exact_radicals import SQRT2, Sqrt2
from linprog import mill as f
from linprog.duality import GeneralLP, dual, to_canonical
from linprog.lp import (best_by_enumeration, dual_by_enumeration, solve_square,
                        vertices)

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "lesson.md").read_text()
FLAT = " ".join(TEXT.split())


def dot(a, x):
    return sum((left * right for left, right in zip(a, x)), Fraction(0))


def fair_offer_corners():
    boundaries = [
        (tuple(f.MILL.A[i][j] for i in range(f.MILL.m)), f.MILL.c[j])
        for j in range(f.MILL.n)
    ]
    boundaries.extend(
        (tuple(Fraction(int(i == j)) for i in range(f.MILL.m)), Fraction(0))
        for j in range(f.MILL.m)
    )
    found = {}
    for first, second in combinations(boundaries, f.MILL.m):
        offer = solve_square((first[0], second[0]), (first[1], second[1]))
        if offer is None or any(value < 0 for value in offer):
            continue
        if any(dot(tuple(offer[i] for i in range(f.MILL.m)),
                   tuple(f.MILL.A[i][j] for i in range(f.MILL.m))) < f.MILL.c[j]
               for j in range(f.MILL.n)):
            continue
        bill = dot(offer, f.MILL.b)
        found[offer] = bill
    return found


def priced_products(offer):
    return tuple(
        sum((offer[i] * f.MILL.A[i][j] for i in range(f.MILL.m)),
            Fraction(0))
        for j in range(f.MILL.n)
    )


def weak_duality_chain(plan, offer):
    products = priced_products(offer)
    used = tuple(f.MILL.used(i, plan) for i in range(f.MILL.m))
    return (
        f.MILL.value(plan),
        dot(products, plan),
        dot(offer, used),
        dot(offer, f.MILL.b),
    )


def test_independent_price_plane_enumeration_finds_the_three_fair_corners():
    corners = fair_offer_corners()
    assert corners == {
        (Fraction(0), Fraction(5)): Fraction(100),
        (Fraction(2), Fraction(1)): Fraction(84),
        (Fraction(3), Fraction(0)): Fraction(96),
    }
    assert dual_by_enumeration(f.MILL) == ((Fraction(2), Fraction(1)), 84)
    assert dual_by_enumeration(f.MILL)[0] == f.WALK.prices


def test_weak_duality_chains_show_the_two_distinct_gaps():
    assert weak_duality_chain((8, 12), (3, 0)) == (84, 96, 96, 96)
    assert weak_duality_chain((0, 16), (2, 1)) == (80, 80, 80, 84)


def test_offer_fairness_and_bills_match_the_examples():
    unfair = (Fraction(1), Fraction(1))
    assert priced_products(unfair) == (2, 3)
    assert dot(unfair, f.MILL.b) == 52
    assert any(value < cost for value, cost in zip(priced_products(unfair), f.MILL.c))

    fair = (Fraction(2), Fraction(2))
    assert priced_products(fair) == (4, 6)
    assert all(value >= cost for value, cost in zip(priced_products(fair), f.MILL.c))
    assert dot(fair, f.MILL.b) == 104

    weak = (Fraction(1), Fraction(2))
    plan = (Fraction(0), Fraction(16))
    assert priced_products(weak) == (3, 4)
    assert dot(weak, f.MILL.b) == 72
    assert dot(weak, f.MILL.b) < f.MILL.value(plan) == 80


def test_every_mill_corner_value_is_below_every_fair_corner_bill():
    bills = fair_offer_corners().values()
    assert all(f.MILL.value(plan) <= bill
               for plan in f.CORNERS for bill in bills)


def test_unbounded_primal_has_an_infeasible_dual():
    primal = GeneralLP("max", (3, 5), ((1, -1),), ("<=",), (4,),
                       (">=0", ">=0"))
    buyer = dual(primal)
    assert buyer.sense == "min"
    assert buyer.rows == (">=", ">=")
    assert buyer.b == (3, 5)
    assert not vertices(to_canonical(buyer))

    values = []
    for amount in range(11):
        plan = (Fraction(amount), Fraction(amount))
        assert dot(primal.A[0], plan) <= primal.b[0]
        values.append(dot(primal.c, plan))
    assert values == [Fraction(8 * amount) for amount in range(11)]


def test_complete_sets_certificate_is_a_fair_offer_with_bill_ten():
    primal = GeneralLP(
        "max",
        (0, 0, 1),
        ((1, 2, 0), (1, 1, 0), (-1, 0, 1), (0, -1, 1)),
        ("<=", "<=", "<=", "<="),
        (32, 20, 0, 0),
        (">=0", ">=0", ">=0"),
    )
    buyer = dual(primal)
    multipliers = (Fraction(0), Fraction(1, 2),
                   Fraction(1, 2), Fraction(1, 2))
    covered = tuple(
        sum((multipliers[i] * primal.A[i][j] for i in range(len(primal.rows))),
            Fraction(0))
        for j in range(len(primal.c))
    )
    bill = dot(multipliers, primal.b)

    assert buyer.sense == "min"
    assert covered == (0, 0, 1)
    assert all(value >= cost for value, cost in zip(covered, primal.c))
    assert bill == 10
    assert dot(multipliers, buyer.c) == bill


def test_disc_certificate_uses_the_exact_sqrt_two_multiplier():
    multiplier = Sqrt2(Fraction(1), Fraction(-1, 2))
    assert multiplier * Sqrt2(Fraction(2), Fraction(1)) == Sqrt2(1, 0)

    rows = (
        (Sqrt2(1, 0), Sqrt2(1, 0), SQRT2),
        (Sqrt2(-1, 0), Sqrt2(0, 0), Sqrt2(1, 0)),
        (Sqrt2(0, 0), Sqrt2(-1, 0), Sqrt2(1, 0)),
    )
    combined = tuple(
        sum((multiplier * row[column] for row in rows), Sqrt2(0, 0))
        for column in range(3)
    )
    assert combined == (Sqrt2(0, 0), Sqrt2(0, 0), Sqrt2(1, 0))
    assert 20 * multiplier == Sqrt2(Fraction(20), Fraction(-10))


def _random_program(index, rng):
    n = 3 if index % 4 == 0 else 2
    row_count = 2 + index % 3
    if n == 2:
        sign_patterns = ((">=0", "<=0"), ("free", ">=0"), ("<=0", "free"))
        signs = sign_patterns[index % len(sign_patterns)]
    else:
        cycle = (">=0", "<=0", "free")
        signs = tuple(cycle[(index + j) % len(cycle)] for j in range(n))
    x0 = tuple(
        rng.randint(0, 5) if sign == ">=0"
        else rng.randint(-5, 0) if sign == "<=0"
        else rng.randint(-5, 5)
        for sign in signs
    )
    row_cycle = ("<=", ">=", "=")
    row_senses = tuple(row_cycle[(index + i) % len(row_cycle)]
                       for i in range(row_count))
    coefficients = tuple(
        tuple(Fraction(rng.randint(-3, 3)) for _ in range(n))
        for _ in range(row_count)
    )
    bounds = []
    for row, sense in zip(coefficients, row_senses):
        value = dot(row, x0)
        slack = Fraction(rng.randint(0, 4))
        bounds.append(value + slack if sense == "<="
                      else value - slack if sense == ">="
                      else value)

    box_rows = []
    box_bounds = []
    for j in range(n):
        positive = tuple(Fraction(int(k == j)) for k in range(n))
        box_rows.extend((positive, tuple(-value for value in positive)))
        box_bounds.extend((Fraction(5), Fraction(5)))
    return GeneralLP(
        "max" if index % 2 else "min",
        tuple(Fraction(rng.randint(-5, 5)) for _ in range(n)),
        coefficients + tuple(box_rows),
        row_senses + ("<=",) * (2 * n),
        tuple(bounds) + tuple(box_bounds),
        signs,
    )


def restore_variables(signs, canonical):
    original = []
    index = 0
    for sign in signs:
        if sign == ">=0":
            original.append(canonical[index])
            index += 1
        elif sign == "<=0":
            original.append(-canonical[index])
            index += 1
        else:
            original.append(canonical[index] - canonical[index + 1])
            index += 2
    return tuple(original)


def general_feasible(program, point):
    for value, sign in zip(point, program.signs):
        if sign == ">=0" and value < 0:
            return False
        if sign == "<=0" and value > 0:
            return False
    for row, sense, bound in zip(program.A, program.rows, program.b):
        value = dot(row, point)
        if sense == "<=" and value > bound:
            return False
        if sense == ">=" and value < bound:
            return False
        if sense == "=" and value != bound:
            return False
    return True


def test_seeded_mixed_general_programs_preserve_duality_and_weak_duality():
    rng = random.Random(407)
    for index in range(200):
        primal = _random_program(index, rng)
        buyer = dual(primal)
        assert dual(buyer) == primal

        primal_vertex, primal_value = best_by_enumeration(to_canonical(primal))
        buyer_vertex, buyer_value = best_by_enumeration(to_canonical(buyer))
        assert primal_value + buyer_value == 0

        x = restore_variables(primal.signs, primal_vertex)
        y = restore_variables(buyer.signs, buyer_vertex)
        assert general_feasible(primal, x)
        assert general_feasible(buyer, y)
        primal_value = dot(primal.c, x)
        buyer_value = dot(buyer.c, y)
        if primal.sense == "max":
            assert primal_value <= buyer_value
        else:
            assert primal_value >= buyer_value


def test_chapter_six_numbers_and_figure_paths_match_the_computation():
    for phrase in (
        "84,000", "96,000", "100,000", "3·8 + 6·12 = 96",
        "32 + 40 = 72", "½ × 20 = 10", "20 − 10√2",
        "1 − √2 ÷ 2 ≈ 0.29",
    ):
        assert phrase in FLAT

    for image in ("offer.gif", "sandwich.png", "signs.png"):
        relative = f"chapters/06-buying-the-hours/{image}"
        assert relative in TEXT
        assert (ROOT / relative).is_file()
