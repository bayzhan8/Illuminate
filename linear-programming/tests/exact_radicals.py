from dataclasses import dataclass
from fractions import Fraction


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
        return Sqrt2(self.rational * other.rational
                     + 2 * self.radical * other.radical,
                     self.rational * other.radical
                     + self.radical * other.rational)

    __rmul__ = __mul__


SQRT2 = Sqrt2(Fraction(0), Fraction(1))


@dataclass(frozen=True)
class Sqrt5:
    rational: Fraction
    radical: Fraction

    @staticmethod
    def coerce(value):
        if isinstance(value, Sqrt5):
            return value
        return Sqrt5(Fraction(value), Fraction(0))

    def __add__(self, other):
        other = self.coerce(other)
        return Sqrt5(self.rational + other.rational,
                     self.radical + other.radical)

    __radd__ = __add__

    def __neg__(self):
        return Sqrt5(-self.rational, -self.radical)

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        other = self.coerce(other)
        return Sqrt5(self.rational * other.rational
                     + 5 * self.radical * other.radical,
                     self.rational * other.radical
                     + self.radical * other.rational)

    __rmul__ = __mul__


SQRT5 = Sqrt5(Fraction(0), Fraction(1))
