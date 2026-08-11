"""What one more unit is worth, and how long that stays true.

A price attached to a row answers "what would one more unit of this earn me?".
The answer is a straight line only for a while.  Push the capacity far enough
and the plan changes shape, a different row takes over as the binding one, and
the price steps down.  This module rebuilds that whole picture -- the value as
a function of one right-hand side, its straight pieces, and the exact points
where it bends.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .lp import LP, F, solve


def with_rhs(lp: LP, row: int, value) -> LP:
    """The same program with one right-hand side changed."""
    b = list(lp.b)
    b[row] = F(value)
    return LP.build(c=lp.c, A=lp.A, b=b, op=lp.op, sense=lp.sense,
                    var_names=lp.var_names, row_names=lp.row_names)


def value_at(lp: LP, row: int, value) -> Fraction | None:
    """The best achievable objective when row *row* has that much capacity."""
    found = solve(with_rhs(lp, row, value))
    return found.value if found.ok else None


@dataclass(frozen=True)
class Segment:
    start: Fraction
    end: Fraction
    slope: Fraction      # what one more unit is worth along this piece
    intercept: Fraction  # value = slope * capacity + intercept

    def value(self, t) -> Fraction:
        return self.slope * F(t) + self.intercept

    def contains(self, t) -> bool:
        return self.start <= F(t) <= self.end


def value_function(lp: LP, row: int, lo, hi, samples: int = 120) -> list[Segment]:
    """The value as a function of one capacity, as exact straight pieces.

    Sampled on a regular grid, then rebuilt into lines and intersected, so the
    bends come out as exact fractions rather than as wherever a sample happened
    to land.

    The subtle part is that a bend almost never lands on a sample.  The two
    samples either side of one are joined by a segment whose slope belongs to
    neither piece, and taken at face value that phantom slope becomes a
    phantom fourth piece a few hundredths wide.  This example really does
    produce one: the plank curve bends at 316/7, the grid steps over it from
    45 to 45.5, and the straddling pair reads as slope 25/14, which is a piece
    of nothing.  So a line is only believed when a run of at least two
    consecutive intervals agrees on it, single-interval runs are treated as
    straddles, and every bend is then re-solved directly to confirm the value
    there really is what both neighbouring lines predict.  A genuine piece
    narrower than two grid steps would trip that check rather than pass
    silently: it raises, and the caller passes more samples.
    """
    lo, hi = F(lo), F(hi)
    step = (hi - lo) / samples
    grid: list[tuple[Fraction, Fraction]] = []
    for k in range(samples + 1):
        t = lo + step * k
        v = value_at(lp, row, t)
        if v is not None:
            grid.append((t, v))
    if len(grid) < 2:
        return []

    # every consecutive pair, with the slope of the segment joining them
    spans = [(a[0], b[0], (b[1] - a[1]) / (b[0] - a[0]))
             for a, b in zip(grid, grid[1:])]

    # maximal runs of consecutive spans that agree on a slope
    runs = [[spans[0]]]
    for span in spans[1:]:
        if span[2] == runs[-1][-1][2]:
            runs[-1].append(span)
        else:
            runs.append([span])

    def line_of(run):
        slope = run[0][2]
        t0 = run[0][0]
        v0 = next(v for t, v in grid if t == t0)
        return slope, v0 - slope * t0

    believed = [line_of(r) for r in runs if len(r) >= 2]
    if not believed:
        # Nothing was corroborated. If every span agreed on one slope that is
        # simply a straight function and there is nothing to corroborate. If
        # they disagreed, the grid is too coarse to tell a real piece from a
        # straddled bend, and guessing would return a plausible wrong curve --
        # which is worse than refusing, because a wrong curve looks fine.
        if len({s for _, _, s in spans}) > 1:
            raise ValueError(
                f"a grid of {samples} cannot resolve this curve: no two "
                f"neighbouring spans agree on a slope")
        believed = [line_of(runs[0])]

    bounds = [lo]
    for (s1, i1), (s2, i2) in zip(believed, believed[1:]):
        if s1 == s2:
            raise ValueError("two believed lines share a slope; this is a bug")
        bounds.append((i2 - i1) / (s1 - s2))
    bounds.append(hi)

    segments = [Segment(start=bounds[k], end=bounds[k + 1], slope=s, intercept=i)
                for k, (s, i) in enumerate(believed)]

    # confirm each bend by solving there, not by trusting the reconstruction
    for seg, nxt in zip(segments, segments[1:]):
        bend = seg.end
        actual = value_at(lp, row, bend)
        if actual is None or actual != seg.value(bend) or actual != nxt.value(bend):
            raise ValueError(
                f"the bend near {float(bend):.4f} does not check out; "
                f"the grid of {samples} is too coarse for this program")
    return segments


def breakpoints(lp: LP, row: int, lo, hi, samples: int = 120) -> list[Fraction]:
    segs = value_function(lp, row, lo, hi, samples)
    return [s.end for s in segs[:-1]]


def price_range(lp: LP, row: int, lo, hi, samples: int = 120) -> tuple[Fraction, Fraction, Fraction]:
    """(from, to, price): how far the current capacity's price holds, and its value."""
    here = lp.b[row]
    for seg in value_function(lp, row, lo, hi, samples):
        if seg.contains(here):
            return seg.start, seg.end, seg.slope
    raise ValueError("the current capacity is outside the range examined")
