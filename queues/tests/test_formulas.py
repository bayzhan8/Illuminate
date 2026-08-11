"""Mathematics, verified by a route that shares no code with the thing tested.

The closed forms are checked against summing the stationary distribution term
by term; the exact Erlang C against the numerically stable recursion; and the
whole lot against a discrete-event simulation that knows none of the formulas.
"""

import math
from fractions import Fraction as F

import numpy as np
import pytest

from queues import desk as d
from queues.formulas import (MM1, MMC, erlang_c, erlang_c_stable, frac,
                             kingman, number_in_system_by_summation,
                             pollaczek_khinchine, wait_from_variability)
from queues.simulate import (batch_interval, correlation_length, empty_to_empty,
                             lindley, naive_interval, run_queue)


# --- the closed forms, against summation -----------------------------------

@pytest.mark.parametrize("rate", [F(1), F(5), F(8), F(9), F(19, 2)])
def test_number_in_system_matches_summing_the_distribution(rate):
    """The closed form sums a geometric series by hand. This adds it up."""
    q = MM1.build(rate, 10)
    assert number_in_system_by_summation(q) == pytest.approx(
        float(q.number_in_system), rel=1e-9)


def test_the_stationary_distribution_is_a_distribution():
    q = d.BUSY
    assert sum(float(q.stationary(n)) for n in range(6000)) == pytest.approx(1.0)


# --- Little's law, as an algebraic identity --------------------------------

@pytest.mark.parametrize("rate", d.RATES)
def test_little_holds_for_the_whole_system(rate):
    q = d.DESKS[rate]
    assert q.number_in_system == q.rate * q.time_in_system


@pytest.mark.parametrize("rate", d.RATES)
def test_little_holds_for_the_waiting_line_alone(rate):
    q = d.DESKS[rate]
    assert q.number_waiting == q.rate * q.time_waiting


@pytest.mark.parametrize("rate", d.RATES)
def test_utilisation_is_little_applied_to_the_server(rate):
    """A box drawn round the server holds 0 or 1, so its average occupancy is
    the busy fraction, and Little makes that the arrival rate times E[S]."""
    q = d.DESKS[rate]
    assert q.load == q.rate * q.mean_service
    assert q.number_in_system == q.number_waiting + q.load


@pytest.mark.parametrize("rate", d.RATES)
def test_the_two_times_differ_by_exactly_one_service(rate):
    q = d.DESKS[rate]
    assert q.time_in_system - q.time_waiting == q.mean_service


# --- variability -----------------------------------------------------------

@pytest.mark.parametrize("rate", d.RATES)
def test_constant_service_halves_the_wait_exactly(rate):
    """Not approximately half. Half, at every utilisation."""
    exponential = d.DESKS[rate].time_waiting
    constant = d.steady_desk(rate)
    assert constant * 2 == exponential


def test_the_two_forms_of_pollaczek_khinchine_agree():
    """E[S^2] = (1 + c^2) E[S]^2, so the two spellings must coincide."""
    for cv2 in (F(0), F(1, 2), F(1), F(4), F(25)):
        second = (1 + cv2) * d.MEAN_SERVICE ** 2
        assert (pollaczek_khinchine(9, d.MEAN_SERVICE, second)
                == wait_from_variability(9, d.MEAN_SERVICE, cv2))


def test_kingman_is_exact_when_arrivals_are_poisson():
    """With c_a^2 = 1 the approximation reduces to Pollaczek-Khinchine."""
    for cv2 in (F(0), F(1), F(4)):
        assert (kingman(9, d.MEAN_SERVICE, 1, cv2)
                == wait_from_variability(9, d.MEAN_SERVICE, cv2))


def test_exponential_service_is_the_c_squared_equals_one_case():
    assert wait_from_variability(9, d.MEAN_SERVICE, 1) == d.BUSY.time_waiting


def test_the_ladder_is_increasing_and_starts_at_half():
    waits = [wait for _, wait, _ in d.LADDER]
    assert waits == sorted(waits)
    assert waits[0] * 2 == d.BUSY.time_waiting          # deterministic
    assert waits[2] == d.BUSY.time_waiting              # exponential


# --- several servers -------------------------------------------------------

def test_erlang_c_with_one_server_is_the_utilisation():
    for rate in (F(1), F(5), F(9)):
        assert erlang_c(1, rate / 10) == rate / 10


def test_erlang_c_two_servers_matches_its_closed_form():
    """C(2, a) = 2 rho^2 / (1 + rho), derived independently."""
    for rate in (F(1), F(9), F(18), F(19)):
        load = rate / 20
        assert erlang_c(2, rate / 10) == 2 * load ** 2 / (1 + load)


@pytest.mark.parametrize("servers,offered", [(1, 0.5), (2, 1.8), (5, 4.0),
                                             (10, 8.0), (50, 45.0), (200, 190.0)])
def test_the_stable_recursion_agrees_with_the_exact_formula(servers, offered):
    assert erlang_c_stable(servers, offered) == pytest.approx(
        float(erlang_c(servers, frac(offered))), rel=1e-12)


def test_the_recursion_survives_sizes_the_exact_form_cannot_reach():
    """The direct formula forms a^c and c! separately and overflows."""
    value = erlang_c_stable(10_000, 9900.0)
    assert 0.0 < value < 1.0


def test_one_server_of_the_many_server_model_is_the_one_server_model():
    single = MM1.build(9, 10)
    same = MMC.build(9, 10, 1)
    assert same.time_waiting == single.time_waiting
    assert same.number_in_system == single.number_in_system


def test_pooling_beats_splitting_at_equal_utilisation():
    for rate, apart, together in d.POOLING:
        assert together < apart


def test_pooling_helps_more_when_the_desk_is_quieter():
    """The surprise: the gain shrinks as the queue gets busier."""
    (_, apart_quiet, pooled_quiet), (_, apart_busy, pooled_busy) = d.POOLING
    assert apart_quiet / pooled_quiet > apart_busy / pooled_busy


def test_pooling_can_lose_when_the_jobs_are_different_sizes():
    """Same total capacity, same utilisation, and one line is worse."""
    assert d.COMBINED > d.DEDICATED
    assert d.COMBINED / d.DEDICATED > F(3, 2)


def test_the_two_pooling_arrangements_really_have_the_same_capacity():
    quick_load = d.QUICK_RATE * d.QUICK_TIME
    slow_load = d.SLOW_RATE * d.SLOW_TIME
    assert quick_load == slow_load == F(4, 5)             # each desk 80% busy
    total = d.QUICK_RATE + d.SLOW_RATE
    mean = (d.QUICK_RATE * d.QUICK_TIME + d.SLOW_RATE * d.SLOW_TIME) / total / 2
    assert total * mean == F(4, 5)                        # pooled desk too


# --- averaging the arrival rate --------------------------------------------

def test_plugging_in_the_average_rate_understates_the_wait():
    assert d.HONEST > d.NAIVE
    assert d.HONEST / d.NAIVE > F(2)


def test_little_survives_the_averaging_even_though_the_formula_does_not():
    """The point of the chapter: the law is linear in the right things."""
    assert d.MEAN_RATE * d.HONEST == d.HONEST_L


# --- the simulation, which knows none of the above -------------------------

def test_the_identity_is_exact_over_an_empty_to_empty_window():
    """No limit is taken and no assumption made, so this is machine precision."""
    run = run_queue(rate=0.9, service_rate=1.0, customers=60_000, seed=3)
    area, total_wait, served = empty_to_empty(run)
    assert served > 50_000
    assert area == pytest.approx(total_wait, rel=1e-11)


def test_the_simulation_finds_the_formulas():
    run = run_queue(rate=9.0, service_rate=10.0, customers=400_000, seed=5)
    assert run.number_in_system == pytest.approx(float(d.BUSY.number_in_system), rel=0.06)
    assert run.time_in_system == pytest.approx(float(d.BUSY.time_in_system), rel=0.06)
    assert run.utilisation == pytest.approx(float(d.BUSY.load), rel=0.03)


def test_little_holds_on_the_sample_path_far_tighter_than_the_estimates():
    """The heart of chapter 7.

    Over an arbitrary window the two averages do not agree exactly: the gap is
    the work sitting in the queue at the two ends, which no amount of running
    removes. But that gap is thousands of times smaller than the distance
    either average still has to travel to reach its true value. The relation
    is essentially satisfied long before either side is right.
    """
    run = run_queue(rate=9.0, service_rate=10.0, customers=400_000, seed=5)
    error = abs(run.number_in_system - float(d.BUSY.number_in_system)) \
        / float(d.BUSY.number_in_system)
    assert run.littles_law_residual < 1e-4        # boundary work, not zero
    assert error > run.littles_law_residual * 1000


def test_constant_service_really_does_halve_the_wait_in_simulation():
    fast = run_queue(9.0, 10.0, 200_000, seed=8, service="deterministic")
    slow = run_queue(9.0, 10.0, 200_000, seed=8, service="exponential")
    assert fast.time_waiting == pytest.approx(slow.time_waiting / 2, rel=0.12)


def test_consecutive_waits_are_badly_correlated_and_worse_when_busy():
    rng = np.random.default_rng(1)
    lengths = [correlation_length(lindley(rho, 1.0, 400_000, rng))
               for rho in (0.5, 0.8, 0.9)]
    assert lengths == sorted(lengths)
    assert lengths[0] > 5 and lengths[-1] > 200


def test_pretending_the_waits_are_independent_gives_a_far_too_narrow_interval():
    rng = np.random.default_rng(2)
    waits = lindley(0.9, 1.0, 1_000_000, rng)
    naive = naive_interval(waits)
    _, batched = batch_interval(waits, batches=10)
    assert batched > 10 * naive


def test_the_naive_interval_usually_misses_the_true_answer():
    """Nominally 95% confident. Run it repeatedly and watch."""
    truth = float(d.BUSY.time_waiting * 60)      # in minutes, mu = 10/hr
    rng = np.random.default_rng(4)
    hits = 0
    trials = 40
    for _ in range(trials):
        waits = lindley(9.0, 10.0, 200_000, rng) * 60
        mean = float(waits.mean())
        if abs(mean - truth) <= naive_interval(waits):
            hits += 1
    assert hits < trials / 2, f"{hits}/{trials} covered; expected far under half"
