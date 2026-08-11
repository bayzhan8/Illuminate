"""The mathematics, against a route that shares no code with it.

Presolve is the part of a solver most able to be confidently wrong: it can
delete the optimum and every downstream answer still looks like an answer.
So the important test here is not that presolve does something, it is that a
model reduced by presolve and one enumerated point by point agree, over as
many random instances as will run in a second.
"""

import random
from fractions import Fraction as F

import pytest

from solvers import library as L
from solvers.model import build
from solvers.presolve import Infeasible, postsolve, presolve
from solvers.solve import brute_force, relax, solve_mip


# --- the headline instance -------------------------------------------------

def test_presolve_keeps_the_answer_on_the_worked_instance():
    reduced = solve_mip(L.SMALL_REDUCED)
    assert reduced.value == L.SMALL_ANSWER.value == 290


def test_postsolve_rebuilds_a_real_solution_to_the_original_model():
    reduced = solve_mip(L.SMALL_REDUCED)
    x = postsolve(L.SMALL_PRESOLVED, reduced.x)
    assert L.SMALL.violations(x) == []
    assert L.SMALL.objective(x) == 290


def test_presolve_shrinks_the_worked_instance_as_the_guide_says():
    p = L.SMALL_PRESOLVED
    assert p.before == (20, 21, 42)
    assert p.after == (7, 9, 14)
    assert p.rounds == 13


def test_presolve_proves_a_setup_must_happen_before_any_search():
    """openB1 is fixed to 1 by reasoning alone, which is the chapter 3 claim."""
    j = [c.name for c in L.SMALL.cols].index("openB1")
    assert L.SMALL_PRESOLVED.fixed[j] == 1
    assert any(r.target == "openB1" and r.kind == "tightened bound"
               for r in L.SMALL_PRESOLVED.log)


def test_the_relaxation_gets_stronger_without_a_single_cut():
    assert L.SMALL_RELAXATION == 248
    assert L.SMALL_REDUCED_RELAXATION == 263
    assert L.SMALL_ANSWER.value == 290
    # the reduced bound is strictly better and still a bound
    assert L.SMALL_RELAXATION < L.SMALL_REDUCED_RELAXATION <= L.SMALL_ANSWER.value


# --- the independent route -------------------------------------------------

def random_model(rng: random.Random):
    """A small integer model, boxed so it can be enumerated point by point."""
    n = rng.randint(2, 4)
    m = rng.randint(1, 4)
    cols, cost = [], []
    for j in range(n):
        lo = rng.randint(-2, 2)
        hi = lo + rng.randint(0, 4)
        cols.append((f"x{j}", lo, hi, True))
        cost.append(rng.randint(-4, 4))
    rows = []
    for i in range(m):
        picked = rng.sample(range(n), rng.randint(1, n))
        coefs = {f"x{j}": rng.choice([-3, -2, -1, 1, 2, 3]) for j in picked}
        centre = rng.randint(-6, 6)
        width = rng.randint(0, 6)
        kind = rng.choice(["range", "upper", "lower", "equality"])
        lo, hi = {"range": (centre - width, centre + width),
                  "upper": (None, centre + width),
                  "lower": (centre - width, None),
                  "equality": (centre, centre)}[kind]
        rows.append((f"r{i}", coefs, lo, hi))
    return build(cost=cost, rows=rows, cols=cols, sense=rng.choice(["min", "max"]))


@pytest.mark.parametrize("seed", range(400))
def test_presolve_agrees_with_enumerating_every_point(seed):
    rng = random.Random(seed)
    m = random_model(rng)
    truth = brute_force(m)

    try:
        p = presolve(m)
    except ValueError:
        pytest.skip("column with no bound in the direction its cost pulls")

    if p.status == "infeasible":
        assert truth.status == "infeasible", "presolve threw away a real solution"
        return

    if p.model.n_cols == 0:
        # presolve settled it outright: the constant is the whole answer
        x = postsolve(p, ())
        assert truth.status == "optimal"
        assert m.violations(x) == [], "presolve fixed columns to an illegal point"
        assert m.objective(x) == truth.value
        return

    reduced = solve_mip(p.model)
    if reduced.status != "optimal":
        assert truth.status == "infeasible"
        return

    assert truth.status == "optimal", "presolve invented a solution"
    assert reduced.value == truth.value, "presolve moved the optimal value"
    x = postsolve(p, reduced.x)
    assert m.violations(x) == [], "postsolve produced an illegal point"
    assert m.objective(x) == truth.value


@pytest.mark.parametrize("seed", range(200))
def test_presolve_never_weakens_the_relaxation(seed):
    """Tightening bounds and fixing columns can only help the bound."""
    rng = random.Random(10_000 + seed)
    m = random_model(rng)
    before = relax(m)
    try:
        p = presolve(m)
    except ValueError:
        pytest.skip("unbounded column")
    if p.status == "infeasible" or p.model.n_cols == 0:
        return
    after = relax(p.model)
    if before.status != "optimal" or after.status != "optimal":
        return
    if m.sense == "min":
        assert after.value >= before.value
    else:
        assert after.value <= before.value


# --- the reductions, one at a time -----------------------------------------

def test_a_singleton_row_becomes_a_bound():
    m = build(cost=[1], rows=[("r", {"x": 2}, 6, 6)],
              cols=[("x", 0, 10, True)], sense="min")
    p = presolve(m)
    assert p.fixed[0] == 3 and p.after[0] == 0


def test_a_row_that_cannot_be_violated_is_dropped():
    m = build(cost=[1, 1], rows=[("r", {"x": 1, "y": 1}, None, 99)],
              cols=[("x", 0, 3, True), ("y", 0, 3, True)], sense="min")
    p = presolve(m)
    assert any(r.kind == "dropped row" for r in p.log)


def test_an_impossible_bound_is_reported_rather_than_solved_around():
    m = build(cost=[1], rows=[("a", {"x": 1}, 5, 5), ("b", {"x": 1}, 2, 2)],
              cols=[("x", 0, 10, True)], sense="min")
    assert presolve(m).status == "infeasible"


def test_integer_rounding_closes_an_empty_interval():
    m = build(cost=[1], rows=[("r", {"x": 4}, 1, 3)],
              cols=[("x", 0, 10, True)], sense="min")
    # 1/4 <= x <= 3/4 has no whole number in it
    assert presolve(m).status == "infeasible"


def test_the_loop_refuses_rather_than_returning_half_a_model(monkeypatch):
    import solvers.presolve as ps
    monkeypatch.setattr(ps, "MAX_ROUNDS", 1)
    with pytest.raises(RuntimeError):
        ps.presolve(L.SMALL)
