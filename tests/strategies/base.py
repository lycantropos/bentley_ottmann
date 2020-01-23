from decimal import Decimal
from fractions import Fraction
from functools import partial
from operator import ne

from hypothesis import strategies

from bentley_ottmann.hints import Scalar
from bentley_ottmann.linear import Segment
from bentley_ottmann.point import Point
from tests.utils import (Strategy,
                         pack,
                         to_pairs)

MAX_FLOAT = 1.e10
MIN_FLOAT = -MAX_FLOAT
scalars_strategies_factories = {Decimal: partial(strategies.decimals,
                                                 min_value=MIN_FLOAT,
                                                 max_value=MAX_FLOAT,
                                                 allow_nan=False,
                                                 allow_infinity=False),
                                float: partial(strategies.floats,
                                               min_value=MIN_FLOAT,
                                               max_value=MAX_FLOAT,
                                               allow_nan=False,
                                               allow_infinity=False),
                                Fraction: strategies.fractions,
                                int: strategies.integers}
scalars_strategies = strategies.sampled_from(
        [factory() for factory in scalars_strategies_factories.values()])


def coordinates_to_segments(coordinates: Strategy[Scalar]
                            ) -> Strategy[Segment]:
    return (to_pairs(coordinates_to_points(coordinates))
            .filter(pack(ne))
            .map(pack(Segment)))


def coordinates_to_points(coordinates: Strategy[Scalar]) -> Strategy[Point]:
    return to_pairs(coordinates).map(pack(Point))


segments_strategies = scalars_strategies.map(coordinates_to_segments)
