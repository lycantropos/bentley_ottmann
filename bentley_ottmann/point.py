from numbers import Real
from typing import NamedTuple

from .hints import Scalar

Point = NamedTuple('Point', [('x', Scalar), ('y', Scalar)])


def _is_real_point(point: Point) -> bool:
    x, y = point
    return isinstance(x, Real)


def _to_real_point(point: Point) -> Point:
    x, y = point
    return Point(float(x), float(y))
