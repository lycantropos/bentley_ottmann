from fractions import Fraction
from functools import partial
from operator import ne

from ground.hints import Scalar
from hypothesis import strategies

from tests.utils import (MAX_SCALAR,
                         MIN_SCALAR,
                         Point,
                         Segment,
                         Strategy,
                         pack,
                         to_pairs)

scalars_strategies_factories = {Fraction: strategies.fractions,
                                int: strategies.integers,
                                float: partial(strategies.floats,
                                               allow_infinity=False,
                                               allow_nan=False)}
scalars_strategies = strategies.sampled_from(
        [factory(MIN_SCALAR, MAX_SCALAR)
         for factory in scalars_strategies_factories.values()])


def scalars_to_segments(scalars: Strategy[Scalar]) -> Strategy[Segment]:
    return (to_pairs(scalars_to_points(scalars))
            .filter(pack(ne))
            .map(pack(Segment)))


def scalars_to_points(scalars: Strategy[Scalar]) -> Strategy[Point]:
    return strategies.builds(Point, scalars, scalars)


points_strategies = scalars_strategies.map(scalars_to_points)
segments_strategies = scalars_strategies.map(scalars_to_segments)
