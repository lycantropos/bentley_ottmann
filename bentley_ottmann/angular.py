from enum import (IntEnum,
                  unique)

from robust import (parallelogram,
                    projection)

from .hints import Scalar
from .point import RealPoint


@unique
class AngleKind(IntEnum):
    OBTUSE = -1
    RIGHT = 0
    ACUTE = 1


@unique
class Orientation(IntEnum):
    CLOCKWISE = -1
    COLLINEAR = 0
    COUNTERCLOCKWISE = 1


def to_angle_kind(first_ray_point: RealPoint,
                  vertex: RealPoint,
                  second_ray_point: RealPoint) -> AngleKind:
    return AngleKind(to_sign(projection.signed_length(
            vertex, first_ray_point, vertex, second_ray_point)))


def to_orientation(first_ray_point: RealPoint,
                   vertex: RealPoint,
                   second_ray_point: RealPoint) -> Orientation:
    return Orientation(to_sign(parallelogram.signed_area(
            vertex, first_ray_point, vertex, second_ray_point)))


def to_sign(value: Scalar) -> int:
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0
