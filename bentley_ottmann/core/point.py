from fractions import Fraction

from bentley_ottmann.hints import Point


def to_rational_point(point: Point) -> Point:
    x, y = point
    return Fraction(x), Fraction(y)
