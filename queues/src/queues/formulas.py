"""Queueing formulas, in exact rational arithmetic.

Every quantity the guide quotes is a Fraction. That is not decoration: the
guide's central claim is that two differently-computed averages are *equal*,
and the whole point of chapter 2 is that this is an identity rather than an
approximation. A formula module that returned 8.999999999999998 would be
arguing against the text.

The names follow the standard ones. `L` is the time-average number in the
system, `W` the customer-average time in it, and the `_q` versions are the same
two quantities with the box drawn around the waiting line only.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F

Number = F | int | str | float


def frac(x: Number) -> F:
    """Coerce to an exact Fraction, routing floats through their decimal text."""
    return F(str(x)) if isinstance(x, float) else F(x)


# --- one server, exponential service ---------------------------------------

@dataclass(frozen=True)
class MM1:
    """A single server, Poisson arrivals, exponential service.

    `rate` is arrivals per unit time, `service_rate` is completions per unit
    time when the server is busy. Both are held exactly.
    """

    rate: F
    service_rate: F

    @staticmethod
    def build(rate: Number, service_rate: Number) -> "MM1":
        q = MM1(frac(rate), frac(service_rate))
        assert q.rate > 0 and q.service_rate > 0
        assert q.rate < q.service_rate, "an unstable queue has no long-run average"
        return q

    @property
    def load(self) -> F:
        """The fraction of time the server is busy.

        This is Little's law applied to a box drawn around the server alone:
        the server holds 0 or 1 customers, so its time-average occupancy *is*
        the busy fraction, and equals the arrival rate times the mean service
        time.
        """
        return self.rate / self.service_rate

    @property
    def mean_service(self) -> F:
        return 1 / self.service_rate

    @property
    def number_in_system(self) -> F:          # L
        return self.load / (1 - self.load)

    @property
    def number_waiting(self) -> F:            # L_q
        return self.load ** 2 / (1 - self.load)

    @property
    def time_in_system(self) -> F:            # W
        return 1 / (self.service_rate - self.rate)

    @property
    def time_waiting(self) -> F:              # W_q
        return self.load / (self.service_rate - self.rate)

    @property
    def congestion_multiplier(self) -> F:
        """1/(1 - load). The wait is the service time times this number."""
        return 1 / (1 - self.load)

    @property
    def relaxation_time(self) -> float:
        """Roughly how long the queue takes to forget its starting state.

        Used only to say how long a measurement window has to be before an
        average of it means anything; chapter 8 leans on this.
        """
        import math
        return 1.0 / (math.sqrt(float(self.service_rate))
                      - math.sqrt(float(self.rate))) ** 2

    def stationary(self, n: int) -> F:
        """The chance of finding exactly n customers there at a random moment."""
        return (1 - self.load) * self.load ** n


def number_in_system_by_summation(q: MM1, terms: int = 4000) -> float:
    """L, obtained by adding up n times its probability, term by term.

    Deliberately not the closed form. The closed form comes from summing a
    geometric series by hand; this sums it numerically instead, so the test
    that compares them is checking the algebra rather than restating it.
    """
    return sum(n * float(q.stationary(n)) for n in range(terms))


# --- one server, any service distribution ----------------------------------

def pollaczek_khinchine(rate: Number, mean_service: Number,
                        second_moment: Number) -> F:
    """Mean wait before service starts, for any service-time distribution.

    W_q = rate * E[S^2] / (2 (1 - load)).

    The second moment is the whole story. A random arrival lands inside a
    service in progress with probability proportional to that service's length,
    so long services are over-represented in what an arrival actually has to
    wait out. That is why E[S^2] appears here and E[S] does not.
    """
    rate, mean_service = frac(rate), frac(mean_service)
    second_moment = frac(second_moment)
    load = rate * mean_service
    assert load < 1, "an unstable queue has no long-run average"
    return rate * second_moment / (2 * (1 - load))


def wait_from_variability(rate: Number, mean_service: Number,
                          service_cv_squared: Number) -> F:
    """The same formula, split into the three knobs it really has.

    W_q = (load / (1 - load)) * ((1 + c^2) / 2) * E[S]

    Utilisation, variability, and scale, multiplied together. Each can be
    changed without touching the others, which is what makes it a design tool
    rather than a description.
    """
    rate, mean_service = frac(rate), frac(mean_service)
    cv2 = frac(service_cv_squared)
    load = rate * mean_service
    assert load < 1
    return (load / (1 - load)) * ((1 + cv2) / 2) * mean_service


def kingman(rate: Number, mean_service: Number,
            arrival_cv_squared: Number, service_cv_squared: Number) -> F:
    """The general single-server approximation.

    Exact when arrivals are Poisson (arrival_cv_squared = 1), where it reduces
    to Pollaczek-Khinchine. Elsewhere it is a heavy-traffic result and the
    guide says so: chapter 6 shows it overstating the wait by 96% at half
    utilisation with regular arrivals.
    """
    rate, mean_service = frac(rate), frac(mean_service)
    ca2, cs2 = frac(arrival_cv_squared), frac(service_cv_squared)
    load = rate * mean_service
    assert load < 1
    return (load / (1 - load)) * ((ca2 + cs2) / 2) * mean_service


# --- several servers -------------------------------------------------------

def erlang_c(servers: int, offered_load: Number) -> F:
    """The chance that an arrival finds every server busy, exactly.

    Written from the definition rather than from the numerically stable
    recursion, because at the sizes this guide draws, exactness is worth more
    than range. `queues.simulate` carries the recursion for the large cases,
    and a test checks the two against each other.
    """
    a = frac(offered_load)
    assert servers >= 1 and a / servers < 1, "an unstable queue has no average"
    terms = sum(a ** k / _factorial(k) for k in range(servers))
    tail = a ** servers / _factorial(servers) * (1 / (1 - a / servers))
    return tail / (terms + tail)


def erlang_c_stable(servers: int, offered_load: float) -> float:
    """Erlang C via the Erlang B recursion, for sizes the exact form cannot reach.

    The direct formula overflows above a few hundred servers because it forms
    a^c and c! separately. This recursion never forms either.
    """
    load = offered_load / servers
    b = 1.0
    for k in range(1, servers + 1):
        b = offered_load * b / (k + offered_load * b)
    return b / (1 - load * (1 - b))


def _factorial(n: int) -> int:
    out = 1
    for k in range(2, n + 1):
        out *= k
    return out


@dataclass(frozen=True)
class MMC:
    """`servers` identical servers sharing one queue."""

    rate: F
    service_rate: F
    servers: int

    @staticmethod
    def build(rate: Number, service_rate: Number, servers: int) -> "MMC":
        q = MMC(frac(rate), frac(service_rate), servers)
        assert q.load < 1, "an unstable queue has no long-run average"
        return q

    @property
    def offered_load(self) -> F:
        """Erlangs: the number of servers that would be busy if none ever idled."""
        return self.rate / self.service_rate

    @property
    def load(self) -> F:
        return self.offered_load / self.servers

    @property
    def wait_probability(self) -> F:
        return erlang_c(self.servers, self.offered_load)

    @property
    def time_waiting(self) -> F:              # W_q
        return self.wait_probability / (self.servers * self.service_rate - self.rate)

    @property
    def number_waiting(self) -> F:            # L_q
        return self.rate * self.time_waiting

    @property
    def time_in_system(self) -> F:
        return self.time_waiting + 1 / self.service_rate

    @property
    def number_in_system(self) -> F:
        return self.number_waiting + self.offered_load
