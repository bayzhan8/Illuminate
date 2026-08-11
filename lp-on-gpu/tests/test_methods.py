"""The mathematics, checked against the exact rational simplex from lp-duality.

That solver shares no line of code with anything here and returns Fractions, so
it is a genuinely independent statement of what the answer is. Every claim this
guide makes about what a first-order method found is measured against it.
"""

import numpy as np
import pytest

from firstorder import story as s
from firstorder.methods import (Problem, arithmetic_intensity,
                                gradient_descent_ascent, pdhg, spiral_anatomy,
                                spiral_matrix, steps_for, usable_fraction)
from lpduality import workshop as w
from lpduality.lp import LP, solve


# --- the two methods differ by exactly one term ----------------------------

def test_the_workshop_here_is_the_workshop_from_the_duality_guide():
    """If these ever drift apart, every cross-check below is meaningless."""
    assert np.array_equal(s.WORKSHOP.A, np.array([[float(v) for v in row]
                                                  for row in w.PRIMAL.A]))
    assert np.array_equal(s.WORKSHOP.b, np.array([float(v) for v in w.PRIMAL.b]))
    assert np.array_equal(-s.WORKSHOP.c, np.array([float(v) for v in w.PRIMAL.c]))


def test_pdhg_finds_what_the_exact_simplex_finds():
    plan, prices = s.converging_run(4000).last
    assert plan == pytest.approx(s.TRUE_PLAN, abs=1e-9)
    assert prices == pytest.approx(s.TRUE_PRICES, abs=1e-9)


def test_pdhg_finds_the_prices_too_which_is_the_point():
    """The dual iterate converges to the duals of guide 1: 25/4, 5/2, 0."""
    _, prices = s.converging_run(4000).last
    assert prices[0] == pytest.approx(6.25, abs=1e-9)
    assert prices[1] == pytest.approx(2.5, abs=1e-9)
    assert prices[2] == pytest.approx(0.0, abs=1e-9)


def test_gradient_descent_ascent_never_settles():
    """It does not diverge here and it does not converge. It cycles."""
    trace = s.cycling_run(4000)
    both = np.hstack([trace.xs, trace.ys])
    tail = both[2000:]
    assert np.linalg.norm(tail[-1] - tail[-2]) > 1.0, "it is still moving"
    assert not np.allclose(trace.last[0], s.TRUE_PLAN, atol=1.0)


def test_the_cycle_is_exact_and_has_the_period_the_guide_quotes():
    trace = s.cycling_run(4000)
    both = np.hstack([trace.xs, trace.ys])[2000:]
    period = s.CYCLE_PERIOD
    assert period == 10
    repeat = np.linalg.norm(both[period:] - both[:-period], axis=1)
    assert repeat.max() < 1e-9, "the cycle repeats exactly, not approximately"


def test_the_cycle_straddles_the_answer_without_ever_reaching_it():
    assert s.CYCLE_LOW < s.TRUE_VALUE < s.CYCLE_HIGH
    trace = s.cycling_run(4000)
    values = -(s.WORKSHOP.c @ trace.xs[-1000:].T)
    assert np.min(np.abs(values - s.TRUE_VALUE)) > 1.0


def test_the_cycling_iterates_are_wildly_infeasible():
    assert s.CYCLE_WORST_VIOLATION > 40


def test_both_methods_use_the_same_step_sizes():
    """So the difference cannot be blamed on tuning."""
    tau, sigma = steps_for(s.WORKSHOP)
    settled = pdhg(s.WORKSHOP, 4000, tau=tau, sigma=sigma).last[0]
    assert settled == pytest.approx(s.TRUE_PLAN, abs=1e-9)
    cycling = gradient_descent_ascent(s.WORKSHOP, 4000, tau=tau, sigma=sigma)
    assert not np.allclose(cycling.last[0], s.TRUE_PLAN, atol=1.0)


# --- the spiral ------------------------------------------------------------

def test_the_spiral_closed_forms_match_the_eigenvalues():
    for step in (0.05, 0.1, 0.2, 0.4, 0.7):
        got = spiral_anatomy(a=1.0, tau=step, sigma=step)
        assert got["contraction"] == pytest.approx(got["contraction_closed_form"])
        assert got["rotation_degrees"] == pytest.approx(got["rotation_closed_form"])


def test_the_contraction_is_the_square_root_of_one_minus_the_step_product():
    for tau, sigma, a in ((0.2, 0.2, 1.0), (0.1, 0.3, 2.0), (0.05, 0.5, 1.5)):
        t = tau * sigma * a * a
        got = spiral_anatomy(a, tau, sigma)
        assert got["contraction"] == pytest.approx(np.sqrt(1 - t))


def test_a_smaller_step_rotates_less_and_contracts_less():
    """The bind: the setting that keeps it stable is the one that stalls it."""
    slow = spiral_anatomy(1.0, 0.05, 0.05)
    fast = spiral_anatomy(1.0, 0.4, 0.4)
    assert slow["rotation_degrees"] < fast["rotation_degrees"]
    assert slow["contraction"] > fast["contraction"]      # closer to 1 = slower


def test_the_guides_spiral_numbers():
    assert s.SPIRAL["contraction"] == pytest.approx(0.9798, abs=5e-5)
    assert s.SPIRAL["rotation_degrees"] == pytest.approx(11.537, abs=5e-4)
    assert s.SPIRAL["iterations_per_turn"] == pytest.approx(31.2, abs=0.05)


def test_the_step_rule_is_what_makes_the_eigenvalues_a_rotation():
    """Outside 0 < tau*sigma*a^2 < 1 there is no spiral to analyse."""
    with pytest.raises(ValueError):
        spiral_anatomy(a=1.0, tau=1.5, sigma=1.5)


# --- restarts --------------------------------------------------------------

def test_restarting_beats_not_restarting_by_orders_of_magnitude():
    plain = s.distance_curve(pdhg(s.WORKSHOP, 600))
    restarted = s.distance_curve(pdhg(s.WORKSHOP, 600, restart_every=40))
    assert restarted[-1] < plain[-1] / 100


def test_restarting_costs_nothing_per_iteration():
    """Same number of matrix products; the averaging is vector work."""
    import inspect
    source = inspect.getsource(pdhg)
    assert source.count("problem.A") == 2, "two matrix products per iteration"


# --- what it costs ---------------------------------------------------------

def test_the_iterate_is_illegal_until_it_has_converged():
    ladder = s.feasibility_ladder()
    violations = [v for _, _, v in ladder]
    assert violations[0] > 0.1
    assert violations[-1] < 1e-9
    assert violations == sorted(violations, reverse=True)


def test_an_early_iterate_can_beat_the_true_optimum_by_cheating():
    """Because it is not standing anywhere legal yet."""
    x, _ = pdhg(s.WORKSHOP, 10).last
    assert -float(s.WORKSHOP.c @ x) > s.TRUE_VALUE
    assert s.WORKSHOP.violation(x) > 0


def test_simplex_iterates_are_always_legal_by_contrast():
    assert w.PRIMAL.is_feasible(solve(w.PRIMAL).x)


def test_on_a_tie_it_lands_between_the_corners():
    interior, corner = s.tie_answers()
    assert interior == pytest.approx(np.array([0.5, 0.5]), abs=1e-6)
    assert corner.tolist() in ([1.0, 0.0], [0.0, 1.0])
    assert interior.sum() == pytest.approx(corner.sum())     # both optimal


# --- the kernel ------------------------------------------------------------

def test_arithmetic_intensity_is_two_flops_per_twelve_bytes():
    assert arithmetic_intensity() == pytest.approx(2 / 12)


def test_a_machine_with_more_arithmetic_can_use_less_of_it():
    """Same kernel, two machines: the one with the higher balance wastes more."""
    lean = usable_fraction(flops_per_second=256e9, bytes_per_second=137.5e9)
    rich = usable_fraction(flops_per_second=26e12, bytes_per_second=2e12)
    assert rich < lean
    assert lean < 0.15 and rich < 0.02


def test_the_reachable_speed_is_set_by_bandwidth_alone():
    slow = s.machine_usage(flops=256e9, bandwidth=137.5e9)
    fast = s.machine_usage(flops=26e12, bandwidth=2e12)
    assert fast["ceiling"] / slow["ceiling"] == pytest.approx(2e12 / 137.5e9)
