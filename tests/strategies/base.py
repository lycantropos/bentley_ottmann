from fractions import Fraction
from operator import ne

from ground.hints import Coordinate
from hypothesis import strategies

from tests.utils import (Point,
                         Segment,
                         Strategy,
                         pack,
                         to_pairs)

coordinates_strategies_factories = {Fraction: strategies.fractions,
                                    int: strategies.integers}
coordinates_strategies = strategies.sampled_from(
        [factory() for factory in coordinates_strategies_factories.values()])


def coordinates_to_segments(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Segment]:
    return (to_pairs(coordinates_to_points(coordinates))
            .filter(pack(ne))
            .map(pack(Segment)))


def coordinates_to_points(coordinates: Strategy[Coordinate]
                          ) -> Strategy[Point]:
    return strategies.builds(Point, coordinates, coordinates)


points_strategies = coordinates_strategies.map(coordinates_to_points)
segments_strategies = coordinates_strategies.map(coordinates_to_segments)
