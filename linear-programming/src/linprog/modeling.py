"""Exact LP models for the extra-row and yes-or-no examples."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .lp import F, LP, best_by_enumeration
from .mill import MILL

OVERTIME_TIER_WIDTH = Fraction(4)
OVERTIME_LIMIT = 2 * OVERTIME_TIER_WIDTH
CHEAP_OVERTIME_PRICE = Fraction(1)
DEAR_OVERTIME_PRICE = Fraction(3)
OVERTIME_GAIN_PER_HOUR = MILL.value((-1, 1))
SHORTFALL_ORDER = Fraction(14)
SHORTFALL_MAX_PENALTY = Fraction(3)
SCENARIO_LOW_ORDER = Fraction(12)
SCENARIO_HIGH_ORDER = Fraction(16)
CONTRACT_MIN = Fraction(14)
CONTRACT_MAX = Fraction(16)
SETUP_EXAMPLE_COST = Fraction(30)
SETUP_U_START = Fraction(16)
SETUP_U_END = Fraction(100)
EITHER_OR_LIMIT = Fraction(6)
SETUP_MOVE_STEPS = 48


@dataclass(frozen=True)
class BinaryBranch:
    value: int
    lp: LP
    offset: Fraction = Fraction(0)
    shift: tuple[Fraction, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "offset", F(self.offset))
        object.__setattr__(self, "shift", tuple(map(F, self.shift)))
        if self.value not in (0, 1):
            raise ValueError("a binary branch value must be 0 or 1")
        if self.shift and len(self.shift) != self.lp.n:
            raise ValueError("a variable shift must match the branch dimension")

    def restore(self, point):
        if not self.shift:
            return tuple(point)
        return tuple(value + shift for value, shift in zip(point, self.shift))


def solve_binary(branches):
    """Solve a one-binary model by enumerating its LP branches."""
    candidates = []
    for branch in branches:
        point, value = best_by_enumeration(branch.lp)
        candidates.append((branch, branch.restore(point), value + branch.offset))
    return max(candidates, key=lambda result: result[2])


def overtime_tiers(first_price=CHEAP_OVERTIME_PRICE,
                   second_price=DEAR_OVERTIME_PRICE) -> LP:
    first_price, second_price = F(first_price), F(second_price)
    width = OVERTIME_TIER_WIDTH
    return LP.build(
        c=(3, 5, -first_price, -second_price),
        A=((1, 2, -1, -1), (1, 1, 0, 0),
           (0, 0, 1, 0), (0, 0, 0, 1)),
        b=(32, 20, width, width),
        var_names=("t", "f", "u1", "u2"),
        row_names=("lathe", "press", "tier 1", "tier 2"),
    )


def overtime_epigraph() -> LP:
    intercept = (DEAR_OVERTIME_PRICE - CHEAP_OVERTIME_PRICE) * OVERTIME_TIER_WIDTH
    return LP.build(
        c=(3, 5, 0, -1),
        A=((1, 2, -1, 0), (1, 1, 0, 0), (0, 0, 1, 0),
           (0, 0, CHEAP_OVERTIME_PRICE, -1),
           (0, 0, DEAR_OVERTIME_PRICE, -1)),
        b=(32, 20, OVERTIME_LIMIT, 0, intercept),
        var_names=("t", "f", "u", "z"),
        row_names=("lathe", "press", "overtime limit", "first cost piece",
                   "second cost piece"),
    )


def overtime_cost(u) -> Fraction:
    u = F(u)
    if not 0 <= u <= OVERTIME_LIMIT:
        raise ValueError("overtime must lie between zero and its limit")
    first = CHEAP_OVERTIME_PRICE * u
    second = (CHEAP_OVERTIME_PRICE * OVERTIME_TIER_WIDTH
              + DEAR_OVERTIME_PRICE * (u - OVERTIME_TIER_WIDTH))
    return max(first, second)


def concave_overtime(w: int) -> BinaryBranch:
    if w == 0:
        lp = LP.build(
            c=(3, 5, -DEAR_OVERTIME_PRICE, -CHEAP_OVERTIME_PRICE),
            A=((1, 2, -1, -1), (1, 1, 0, 0),
               (0, 0, 1, 0), (0, 0, 0, 1)),
            b=(32, 20, OVERTIME_TIER_WIDTH, 0),
            var_names=("t", "f", "u1", "u2"),
            row_names=("lathe", "press", "first crew", "second crew off"),
        )
        return BinaryBranch(0, lp)
    if w == 1:
        lp = LP.build(
            c=(3, 5, -CHEAP_OVERTIME_PRICE),
            A=((1, 2, -1), (1, 1, 0), (0, 0, 1)),
            b=(32 + OVERTIME_TIER_WIDTH, 20, OVERTIME_TIER_WIDTH),
            var_names=("t", "f", "u2"),
            row_names=("lathe with first crew used", "press", "second crew"),
        )
        return BinaryBranch(1, lp, -DEAR_OVERTIME_PRICE * OVERTIME_TIER_WIDTH)
    raise ValueError("w must be 0 or 1")


def shortfall(q) -> LP:
    q = F(q)
    return LP.build(
        c=(3, 5, -q),
        A=((1, 2, 0), (1, 1, 0), (0, -1, -1)),
        b=(32, 20, -SHORTFALL_ORDER),
        var_names=("t", "f", "u"),
        row_names=("lathe", "press", "shortfall"),
    )


def ratio() -> LP:
    return LP.build(
        c=MILL.c,
        A=MILL.A + ((-2, 3),),
        b=MILL.b + (0,),
        var_names=("t", "f"),
        row_names=("lathe", "press", "proportion"),
    )


def two_week_inventory() -> LP:
    return LP.build(
        c=(3, 0, 5, -1, 3, 0, 5),
        A=(
            (1, 2, 0, 0, 0, 0, 0),
            (1, 1, 0, 0, 0, 0, 0),
            (0, 0, 1, 0, 0, 0, 0),
            (0, 0, 0, 0, 1, 2, 0),
            (0, 0, 0, 0, 1, 1, 0),
            (0, 0, 0, 0, 0, 0, 1),
            (0, -1, 1, 1, 0, 0, 0),
            (0, 1, -1, -1, 0, 0, 0),
            (0, 0, 0, -1, 0, -1, 1),
            (0, 0, 0, 1, 0, 1, -1),
        ),
        b=(32, 20, 8, 32, 10, 16, 0, 0, 0, 0),
        var_names=("t1", "f1", "sold1", "stored", "t2", "f2", "sold2"),
        row_names=("lathe 1", "press 1", "cap 1", "lathe 2", "press 2",
                   "cap 2", "balance 1 <=", "balance 1 >=", "balance 2 <=",
                   "balance 2 >="),
    )


def scenarios(p16) -> LP:
    p16 = F(p16)
    p12 = 1 - p16
    return LP.build(
        c=(3, 5, -3 * p12, -3 * p16),
        A=(
            (1, 2, 0, 0),
            (1, 1, 0, 0),
            (0, -1, -1, 0),
            (0, -1, 0, -1),
        ),
        b=(32, 20, -SCENARIO_LOW_ORDER, -SCENARIO_HIGH_ORDER),
        var_names=("t", "f", "u12", "u16"),
        row_names=("lathe", "press", "shortfall 12", "shortfall 16"),
    )


def setup(F_setup, U) -> tuple[BinaryBranch, BinaryBranch]:
    F_setup, U = F(F_setup), F(U)
    off = LP.build(
        c=MILL.c,
        A=MILL.A + ((0, 1),),
        b=MILL.b + (0,),
        var_names=("t", "f"),
        row_names=("lathe", "press", "setup off"),
    )
    on = LP.build(
        c=MILL.c,
        A=MILL.A + ((0, 1),),
        b=MILL.b + (U,),
        var_names=("t", "f"),
        row_names=("lathe", "press", "setup bound"),
    )
    return BinaryBranch(0, off), BinaryBranch(1, on, -F_setup)


def setup_relaxation(F_setup, U) -> LP:
    F_setup, U = F(F_setup), F(U)
    return LP.build(
        c=(3, 5, -F_setup),
        A=((1, 2, 0), (1, 1, 0), (0, 1, -U), (0, 0, 1)),
        b=(32, 20, 0, 1),
        var_names=("t", "f", "z"),
        row_names=("lathe", "press", "setup bound", "z at most 1"),
    )


def semicontinuous() -> tuple[BinaryBranch, BinaryBranch]:
    off = LP.build(
        c=MILL.c,
        A=MILL.A + ((0, 1),),
        b=MILL.b + (0,),
        var_names=("t", "f"),
        row_names=("lathe", "press", "no contract"),
    )
    on = LP.build(
        c=MILL.c,
        A=((1, 2), (1, 1), (0, 1)),
        b=(MILL.b[0] - 2 * CONTRACT_MIN,
           MILL.b[1] - CONTRACT_MIN, CONTRACT_MAX - CONTRACT_MIN),
        var_names=("t", "f above 14"),
        row_names=("lathe after 14 batches", "press after 14 batches",
                   "contract cap"),
    )
    return BinaryBranch(0, off), BinaryBranch(
        1, on, offset=70, shift=(0, 14)
    )


def semicontinuous_relaxation() -> LP:
    return LP.build(
        c=(3, 5, 0),
        A=((1, 2, 0), (1, 1, 0), (0, -1, CONTRACT_MIN),
           (0, 1, -CONTRACT_MAX), (0, 0, 1)),
        b=(32, 20, 0, 0, 1),
        var_names=("t", "f", "z"),
        row_names=("lathe", "press", "contract lower", "contract upper",
                   "z at most 1"),
    )


def either_or(M1, M2) -> tuple[BinaryBranch, BinaryBranch]:
    M1, M2 = F(M1), F(M2)
    z0 = LP.build(
        c=MILL.c,
        A=MILL.A + ((1, 0), (0, 1)),
        b=MILL.b + (EITHER_OR_LIMIT, EITHER_OR_LIMIT + M2),
        var_names=("t", "f"),
        row_names=("lathe", "press", "t at most 6", "f off bound"),
    )
    z1 = LP.build(
        c=MILL.c,
        A=MILL.A + ((1, 0), (0, 1)),
        b=MILL.b + (EITHER_OR_LIMIT + M1, EITHER_OR_LIMIT),
        var_names=("t", "f"),
        row_names=("lathe", "press", "t off bound", "f at most 6"),
    )
    return BinaryBranch(0, z0), BinaryBranch(1, z1)


def setup_bound_at(step: int, steps: int = SETUP_MOVE_STEPS) -> Fraction:
    """The exact smoothstep sample of U from 16 to 100."""
    if steps <= 0 or not 0 <= step <= steps:
        raise ValueError("step must lie between zero and a positive step count")
    progress = Fraction(step, steps)
    eased = progress * progress * (3 - 2 * progress)
    return SETUP_U_START + (SETUP_U_END - SETUP_U_START) * eased
