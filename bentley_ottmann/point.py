from fractions import Fraction
from numbers import (Rational,
                     Real)
from typing import (NamedTuple,
                    Type)

from .hints import Scalar

Point = NamedTuple('Point', [('x', Scalar), ('y', Scalar)])


def _is_real_point(point: Point) -> bool:
    x, y = point
    return isinstance(x, Real)


def _to_real_point(point: Point) -> Point:
    x, y = point
    return Point(float(x), float(y))


def _to_scalar_point(point: Point, coordinate_type: Type[Scalar]) -> Point:
    x, y = point
    return Point(coordinate_type(x), coordinate_type(y))


def _to_rational_point(point: Point) -> Point:
    x, y = point
    if not isinstance(x, Rational):
        x = Fraction(x)
    if not isinstance(y, Rational):
        y = Fraction(y)
    return Point(x, y)
