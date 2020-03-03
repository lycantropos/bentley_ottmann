from fractions import Fraction
from numbers import (Rational,
                     Real)

from robust.hints import Point as RealPoint

from bentley_ottmann.hints import (Base,
                                   Point)


def is_real_point(point: Point) -> bool:
    x, y = point
    return isinstance(x, Real)


def to_real_point(point: Point) -> RealPoint:
    x, y = point
    return float(x), float(y)


def to_scalar_point(point: Point, base: Base) -> Point:
    x, y = point
    return (base(x.numerator) / x.denominator
            if isinstance(x, Rational)
            else base(x),
            base(y.numerator) / y.denominator
            if isinstance(y, Rational)
            else base(y))


def to_rational_point(point: Point) -> Point:
    x, y = point
    return Fraction(x), Fraction(y)
