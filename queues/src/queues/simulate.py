"""A discrete-event queue, and the two averages it produces.

The whole of chapter 2 turns on these being two genuinely different kinds of
average, computed in two genuinely different ways:

  `number_in_system` is a **time** average -- the area under the queue-length
  path, divided by elapsed time. Nobody is asked how long they waited.

  `time_in_system` is a **customer** average -- the mean of one number per
  person. The clock is never consulted.

Little's law says they are related by the arrival rate, and the simulation is
here so the guide can show that happening rather than assert it.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np


@dataclass
class Run:
    """What one simulated stretch of a queue produced."""

    elapsed: float
    arrivals: int
    area: float                    # integral of the queue length over time
    waits: np.ndarray              # one sojourn time per departed customer
    queue_waits: np.ndarray        # the same, excluding service
    busy: float                    # time the server spent occupied
    empty_marks: list = field(default_factory=list)   # (time, area, departures)
    trace: list = field(default_factory=list)         # (time, area, departures)

    @property
    def arrival_rate(self) -> float:
        return self.arrivals / self.elapsed

    @property
    def number_in_system(self) -> float:
        """Time average: area under the path, over elapsed time."""
        return self.area / self.elapsed

    @property
    def time_in_system(self) -> float:
        """Customer average: the mean of one number per person."""
        return float(self.waits.mean())

    @property
    def time_waiting(self) -> float:
        return float(self.queue_waits.mean())

    @property
    def utilisation(self) -> float:
        return self.busy / self.elapsed

    @property
    def littles_law_residual(self) -> float:
        """How far apart the two averages are, relative to their size.

        Over a window that starts and ends empty this is zero to machine
        precision, because there it is an identity. Over an arbitrary window
        it is the work still sitting in the box, divided by elapsed time.
        """
        left = self.number_in_system
        right = self.arrival_rate * self.time_in_system
        return abs(left - right) / left


def run_queue(rate: float, service_rate: float, customers: int,
              seed: int = 0, service: str = "exponential",
              record_every: int = 0) -> Run:
    """Serve `customers` people, one event at a time.

    A deliberately plain event loop, because chapter 7 walks through it. The
    one line that matters is the area accumulation, and it has to happen
    *before* the queue length changes -- that is the vertical slicing of
    chapter 2, and doing it after is the classic way to get a plausible wrong
    answer.
    """
    rng = np.random.default_rng(seed)

    def draw_service() -> float:
        if service == "exponential":
            return float(rng.exponential(1 / service_rate))
        if service == "deterministic":
            return 1 / service_rate
        raise ValueError(f"unknown service distribution {service!r}")

    now = 0.0
    present = 0
    area = 0.0
    busy = 0.0
    waiting: list[float] = []
    waits = np.empty(customers)
    queue_waits = np.empty(customers)
    empty_marks = [(0.0, 0.0, 0)]

    next_arrival = float(rng.exponential(1 / rate))
    next_departure = math.inf
    started = 0.0
    arrivals = 0
    departures = 0
    trace: list[tuple[float, float, int]] = []

    while departures < customers:
        moment = min(next_arrival, next_departure)
        area += present * (moment - now)      # the vertical slice, before the change
        now = moment

        if next_arrival <= next_departure:
            present += 1
            arrivals += 1
            waiting.append(now)
            if present == 1:
                started = now
                next_departure = now + draw_service()
            next_arrival = now + float(rng.exponential(1 / rate))
        else:
            entered = waiting.pop(0)
            waits[departures] = now - entered
            queue_waits[departures] = started - entered
            busy += now - started
            present -= 1
            departures += 1
            if present:
                started = now
                next_departure = now + draw_service()
            else:
                next_departure = math.inf
                empty_marks.append((now, area, departures))
            if record_every and departures % record_every == 0:
                trace.append((now, area, departures))

    return Run(elapsed=now, arrivals=arrivals, area=area, waits=waits,
               queue_waits=queue_waits, busy=busy, empty_marks=empty_marks,
               trace=trace)


def empty_to_empty(run: Run) -> tuple[float, float, int]:
    """The identity, measured over the longest window that starts and ends empty.

    Returns (area under the queue-length path, total of the sojourn times,
    number of customers). Over such a window the two are equal exactly, with
    no limit taken and no assumption made, because every customer who entered
    has left and no partial stays are being counted.
    """
    if len(run.empty_marks) < 2:
        raise ValueError("the queue never emptied; widen the run")
    (t0, a0, n0), (t1, a1, n1) = run.empty_marks[0], run.empty_marks[-1]
    return a1 - a0, float(run.waits[n0:n1].sum()), n1 - n0


# --- how slowly these estimates settle -------------------------------------

def lindley(rate: float, service_rate: float, customers: int,
            rng: np.random.Generator) -> np.ndarray:
    """Waiting times by the Lindley recursion: wait[n+1] = max(0, wait[n] + S - A).

    Equivalent in law to the event loop for a single server serving in order,
    and about a thousand times faster, which is what makes the convergence
    study in chapter 7 affordable. Used only where the *distribution* of the
    answer matters rather than the mechanics.
    """
    gaps = rng.exponential(1 / rate, customers)
    services = rng.exponential(1 / service_rate, customers)
    step = np.empty(customers)
    step[0] = 0.0
    step[1:] = services[:-1] - gaps[1:]
    walk = np.concatenate(([0.0], np.cumsum(step[1:])))
    waits = walk - np.minimum.accumulate(np.minimum(walk, 0.0))
    waits[0] = 0.0
    return waits


def naive_interval(waits: np.ndarray, confidence: float = 1.96) -> float:
    """The half-width you get by pretending the observations are independent."""
    return confidence * float(waits.std(ddof=1)) / math.sqrt(len(waits))


def batch_interval(waits: np.ndarray, batches: int = 10) -> tuple[float, float]:
    """(mean, half-width) from batch means, which does not pretend that.

    Consecutive waits in a queue are heavily correlated -- one long wait makes
    the next one long. Cutting the run into a few big blocks and treating the
    block means as the observations restores something close to independence,
    because a block is many correlation lengths long.
    """
    usable = len(waits) // batches * batches
    blocks = waits[:usable].reshape(batches, -1).mean(axis=1)
    spread = float(blocks.std(ddof=1)) / math.sqrt(batches)
    return float(blocks.mean()), _t_quantile(batches - 1) * spread


def _t_quantile(degrees: int) -> float:
    """Two-sided 95% Student-t quantile, table lookup with a normal fallback."""
    table = {4: 2.776, 9: 2.262, 19: 2.093, 29: 2.045, 49: 2.010, 99: 1.984}
    return table.get(degrees, 1.96)


def correlation_length(waits: np.ndarray, window: int = 20000) -> float:
    """Roughly how many consecutive customers count as one observation.

    The integrated autocorrelation time: 1 + twice the sum of the
    autocorrelations. At high utilisation this runs into the thousands, which
    is the reason the naive confidence interval in chapter 7 is so wrong.
    """
    centred = waits - waits.mean()
    variance = float(centred @ centred) / len(centred)
    if variance == 0:
        return 1.0
    total = 0.0
    for lag in range(1, min(window, len(centred) // 2)):
        rho = float(centred[:-lag] @ centred[lag:]) / (len(centred) - lag) / variance
        if rho <= 0:
            break
        total += rho
    return 1 + 2 * total
