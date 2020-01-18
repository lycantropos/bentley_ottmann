from numbers import Real
from typing import NamedTuple

from .hints import Scalar

Point = NamedTuple('Point', [('x', Scalar), ('y', Scalar)])


def _to_real_point(point: Point) -> Point:
    x, y = point
    return Point(_scalar_to_real(x), _scalar_to_real(y))


def _scalar_to_real(scalar: Scalar) -> Real:
    return scalar if isinstance(scalar, Real) else float(scalar)
