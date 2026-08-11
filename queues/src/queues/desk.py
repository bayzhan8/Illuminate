"""The one desk the whole guide runs on, and every number quoted about it.

One clerk, six minutes a customer. Everything the guide says about waiting is
this desk at a different arrival rate, or this desk with the six minutes made
less variable, or two of these desks arranged differently.

The rates are per hour and chosen so that every quantity at every utilisation
the guide visits is a tidy fraction, and the waits come out in whole minutes.
"""

from __future__ import annotations

from fractions import Fraction as F

from .formulas import (MM1, MMC, erlang_c, kingman, pollaczek_khinchine,
                       wait_from_variability)

SERVICE_RATE = F(10)                 # ten customers an hour
MEAN_SERVICE = 1 / SERVICE_RATE      # six minutes

# the arrival rates the guide visits, and the desk at each of them
RATES = (F(5), F(6), F(8), F(9), F(19, 2), F(99, 10))
DESKS = {rate: MM1.build(rate, SERVICE_RATE) for rate in RATES}

BUSY = DESKS[F(9)]                   # the headline case: ninety percent busy
QUIET = DESKS[F(5)]                  # half busy


# --- constant service instead of exponential -------------------------------

def steady_desk(rate) -> F:
    """The wait when every customer takes exactly six minutes.

    Same server, same speed, same utilisation. The second moment of a constant
    is its square, so Pollaczek-Khinchine collapses to exactly half the
    exponential answer.
    """
    return pollaczek_khinchine(rate, MEAN_SERVICE, MEAN_SERVICE ** 2)


STEADY_BUSY = steady_desk(F(9))      # 27 minutes against 54


# --- the variability ladder ------------------------------------------------

# Same clerk, same six-minute average, same ninety percent busy. Only the
# spread of the service times changes.
SPREADS = (
    (F(0), "every customer takes exactly six minutes"),
    (F(1, 2), "mildly variable"),
    (F(1), "exponential: the textbook case"),
    (F(4), "some customers take much longer"),
    (F(25), "a few customers take enormously longer"),
)
LADDER = tuple((cv2, wait_from_variability(F(9), MEAN_SERVICE, cv2), label)
               for cv2, label in SPREADS)


# --- two clerks, arranged two ways -----------------------------------------

def pooled(rate) -> MMC:
    return MMC.build(rate, SERVICE_RATE, 2)


def separate(rate) -> MM1:
    """One of two independent desks, each taking half the arrivals."""
    return MM1.build(rate / 2, SERVICE_RATE)


POOLING = tuple(
    (rate, separate(rate).time_waiting, pooled(rate).time_waiting)
    for rate in (F(9), F(18))
)


# --- when pooling is the wrong answer --------------------------------------

# Two kinds of job with very different lengths. Dedicating a desk to each beats
# putting them in one line, at identical total capacity and utilisation,
# because a short job stuck behind a long one waits for the long one.
QUICK_RATE, QUICK_TIME = F(4, 5), F(1)        # per hour, hours
SLOW_RATE, SLOW_TIME = F(2, 25), F(10)


def dedicated_wait() -> F:
    """Customer-average wait when each kind of job has its own desk."""
    quick = pollaczek_khinchine(QUICK_RATE, QUICK_TIME, QUICK_TIME ** 2)
    slow = pollaczek_khinchine(SLOW_RATE, SLOW_TIME, SLOW_TIME ** 2)
    total = QUICK_RATE + SLOW_RATE
    return (QUICK_RATE * quick + SLOW_RATE * slow) / total


def combined_wait() -> F:
    """The same work through one desk of double speed: identical capacity."""
    total = QUICK_RATE + SLOW_RATE
    mean = (QUICK_RATE * QUICK_TIME + SLOW_RATE * SLOW_TIME) / total / 2
    second = (QUICK_RATE * QUICK_TIME ** 2
              + SLOW_RATE * SLOW_TIME ** 2) / total / 4
    return pollaczek_khinchine(total, mean, second)


DEDICATED, COMBINED = dedicated_wait(), combined_wait()


# --- averaging the arrival rate is not allowed -----------------------------

# Demand is five an hour half the time and nine an hour the other half.
# Averaging first and then applying the formula is not the same as applying
# the formula and then averaging, because the formula bends.
SLOW_PERIOD, FAST_PERIOD = F(5), F(9)
MEAN_RATE = (SLOW_PERIOD + FAST_PERIOD) / 2


def naive_wait() -> F:
    """What you get by putting the average arrival rate into the formula."""
    return MM1.build(MEAN_RATE, SERVICE_RATE).time_in_system


def honest_wait() -> F:
    """The customer-average wait when each period is long enough to settle.

    Customers are weighted by how many of them there are, which is why the
    busy period counts for more than half.
    """
    slow, fast = DESKS[SLOW_PERIOD], DESKS[FAST_PERIOD]
    total = SLOW_PERIOD + FAST_PERIOD
    return (SLOW_PERIOD * slow.time_in_system
            + FAST_PERIOD * fast.time_in_system) / total


def honest_number() -> F:
    """The time-average number present, which weights the periods equally."""
    return (DESKS[SLOW_PERIOD].number_in_system
            + DESKS[FAST_PERIOD].number_in_system) / 2


NAIVE, HONEST, HONEST_L = naive_wait(), honest_wait(), honest_number()


# --- rendering -------------------------------------------------------------

def minutes(hours) -> str:
    """An exact number of hours, said in minutes the way the prose says it."""
    q = F(hours) * 60
    if q.denominator == 1:
        return f"{q.numerator} min"
    return f"{float(q):.3g} min"


def number(x) -> str:
    q = F(x)
    if q.denominator == 1:
        return str(q.numerator)
    if (q * 1000).denominator == 1:
        return f"{float(q):g}"
    return f"{q.numerator}/{q.denominator}"
