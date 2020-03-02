from fractions import Fraction
from numbers import Real
from typing import (Tuple,
                    Type)

from bentley_ottmann.hints import (Point,
                                   Scalar)

RealPoint = Tuple[Real, Real]


def is_real_point(point: Point) -> bool:
    x, y = point
    return isinstance(x, Real)


def to_real_point(point: Point) -> RealPoint:
    x, y = point
    return float(x), float(y)


def to_scalar_point(point: Point, coordinate_type: Type[Scalar]) -> Point:
    x, y = point
    return (coordinate_type(x.numerator) / x.denominator
            if isinstance(x, Fraction)
            else coordinate_type(x),
            coordinate_type(y.numerator) / y.denominator
            if isinstance(y, Fraction)
            else coordinate_type(y))


def to_rational_point(point: Point) -> Point:
    x, y = point
    return Fraction(x), Fraction(y)
