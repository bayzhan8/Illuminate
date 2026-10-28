"""Exact checks for the chapter 3 formulations and quoted values."""

import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from linprog import mill as f
from linprog.lp import LP, best_by_enumeration, simplex

ROOT = Path(__file__).resolve().parents[1]
TEXT = (ROOT / "lesson.md").read_text()
FLAT = " ".join(TEXT.split())


@dataclass(frozen=True)
class Sqrt2:
    rational: Fraction
    radical: Fraction

    @staticmethod
    def coerce(value):
        if isinstance(value, Sqrt2):
            return value
        return Sqrt2(Fraction(value), Fraction(0))

    def __add__(self, other):
        other = self.coerce(other)
        return Sqrt2(self.rational + other.rational,
                     self.radical + other.radical)

    __radd__ = __add__

    def __neg__(self):
        return Sqrt2(-self.rational, -self.radical)

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        return Sqrt2(self.rational * other.rational + 2 * self.radical * other.radical,
                     self.rational * other.radical + self.radical * other.rational)

    __rmul__ = __mul__


SQRT2 = Sqrt2(Fraction(0), Fraction(1))


def test_complete_sets_lp_has_the_quoted_best_plan_and_certificate():
    lp = LP.build(
        c=(0, 0, 1),
        A=[[1, 2, 0], [1, 1, 0], [-1, 0, 1], [0, -1, 1]],
        b=(32, 20, 0, 0),
    )
    walk = simplex(lp)
    assert walk.x == (10, 10, 10)
    assert walk.value == 10
    assert best_by_enumeration(lp) == ((10, 10, 10), Fraction(10))

    certificate = tuple(sum((lp.A[row][column] / 2 for row in (2, 3, 1)),
                             Fraction(0))
                        for column in range(3))
    assert certificate == (0, 0, 1)
    assert Fraction(1, 2) * lp.b[1] == 10
    assert f.MILL.used(0, (10, 10)) == 30
    assert f.MILL.used(1, (10, 10)) == 20
    assert f.money(f.MILL.value((10, 10))) == "80,000 roubles"
    assert f.money(f.BEST_VALUE - f.MILL.value((10, 10))) == "4,000 roubles"


def test_disc_radical_certificate_and_display_values():
    radius = Sqrt2(Fraction(20), Fraction(-10))
    assert radius * (2 + SQRT2) == Sqrt2(Fraction(20), Fraction(0))

    press = (Sqrt2(1, 0), Sqrt2(1, 0), SQRT2)
    t_axis = (Sqrt2(-1, 0), Sqrt2(0, 0), Sqrt2(1, 0))
    f_axis = (Sqrt2(0, 0), Sqrt2(-1, 0), Sqrt2(1, 0))
    certificate = tuple(sum((row[column] for row in (press, t_axis, f_axis)),
                            Sqrt2(0, 0))
                        for column in range(3))
    assert certificate == (Sqrt2(0, 0), Sqrt2(0, 0), Sqrt2(2, 1))
    assert f.MILL.b[1] == 20

    center = (radius, radius)
    assert center[0] == radius and center[1] == radius
    radius_float = 20 - 10 * math.sqrt(2)
    lathe = (3 + math.sqrt(5)) * radius_float
    gap = (32 - lathe) / math.sqrt(5)
    assert f"{lathe:.2f}" == "30.67"
    assert f"{gap:.2f}" == "0.59"
    assert f"{radius_float:.2f}" == "5.86"


def test_disc_grid_search_agrees_with_the_radical_radius():
    radical_radius = 20 - 10 * math.sqrt(2)
    root_two = math.sqrt(2)
    root_five = math.sqrt(5)
    best_radius = -1.0
    for t_index in range(2001):
        t = t_index / 100
        max_f_index = min(2000, (3200 - t_index) // 2, 2000 - t_index)
        for f_index in range(max_f_index + 1):
            five = f_index / 100
            radius = min(t, five, (32 - t - 2 * five) / root_five,
                         (20 - t - five) / root_two)
            best_radius = max(best_radius, radius)
    assert abs(best_radius - radical_radius) < 0.01


def test_chapter_3_prose_matches_the_computed_values():
    assert "30 lathe hours with 2 to spare" in FLAT
    assert "80,000 roubles" in FLAT
    assert "4,000 roubles" in FLAT
    assert "= z ≤ ½ × 20 = 10" in FLAT
    assert "r = 20 − 10√2 ≈ 5.86" in FLAT
    assert "30.67" in FLAT
    assert "0.59" in FLAT
    assert "(1 + s, s)" in FLAT
    assert "1 + 2s" in FLAT
    assert "u = max(u, 0) − max(−u, 0)" in FLAT


def test_absolute_value_vee_and_split_have_the_quoted_properties():
    y = Fraction(1)
    minimum_z = max(y, -y)
    assert minimum_z == 1
    assert minimum_z >= y and minimum_z >= -y
    for integer in range(6):
        s = Fraction(integer)
        y_plus, y_minus = 1 + s, s
        assert y_plus - y_minus == 1
        assert y_plus >= 0 and y_minus >= 0
        assert y_plus + y_minus == 1 + 2 * s
