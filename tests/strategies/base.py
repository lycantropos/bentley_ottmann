import sys
from decimal import Decimal
from fractions import Fraction
from operator import ne
from typing import Optional

from hypothesis import strategies

from bentley_ottmann.hints import (Coordinate,
                                   Point,
                                   Segment)
from tests.utils import (Strategy,
                         pack,
                         to_pairs)

MAX_FLOAT = 1.e15
MIN_FLOAT = -MAX_FLOAT


def to_floats(min_value: Optional[Coordinate] = MIN_FLOAT,
              max_value: Optional[Coordinate] = MAX_FLOAT,
              *,
              allow_nan: bool = False,
              allow_infinity: bool = False) -> Strategy:
    return (strategies.floats(min_value=min_value,
                              max_value=max_value,
                              allow_nan=allow_nan,
                              allow_infinity=allow_infinity)
            .map(to_digits_count))


def to_digits_count(number: float,
                    *,
                    max_digits_count: int = sys.float_info.dig) -> float:
    decimal = Decimal(number).normalize()
    _, significant_digits, exponent = decimal.as_tuple()
    significant_digits_count = len(significant_digits)
    if exponent < 0:
        fixed_digits_count = (1 - exponent
                              if exponent <= -significant_digits_count
                              else significant_digits_count)
    else:
        fixed_digits_count = exponent + significant_digits_count
    if fixed_digits_count <= max_digits_count:
        return number
    whole_digits_count = max(significant_digits_count + exponent, 0)
    if whole_digits_count:
        whole_digits_offset = max(whole_digits_count - max_digits_count, 0)
        decimal /= 10 ** whole_digits_offset
        whole_digits_count -= whole_digits_offset
    else:
        decimal *= 10 ** (-exponent - significant_digits_count)
        whole_digits_count = 1
    decimal = round(decimal, max(max_digits_count - whole_digits_count, 0))
    return float(str(decimal))


scalars_strategies_factories = {float: to_floats,
                                Fraction: strategies.fractions,
                                int: strategies.integers}
scalars_strategies = strategies.sampled_from(
        [factory() for factory in scalars_strategies_factories.values()])


def coordinates_to_segments(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Segment]:
    return (to_pairs(coordinates_to_points(coordinates))
            .filter(pack(ne)))


def coordinates_to_points(coordinates: Strategy[Coordinate]
                          ) -> Strategy[Point]:
    return to_pairs(coordinates)


points_strategies = scalars_strategies.map(coordinates_to_points)
segments_strategies = scalars_strategies.map(coordinates_to_segments)
