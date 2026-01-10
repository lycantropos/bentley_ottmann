from operator import ne

from ground.hints import Point, Segment
from hypothesis import strategies

from tests.hints import ScalarT
from tests.utils import (
    MAX_SCALAR,
    MIN_SCALAR,
    Strategy,
    context,
    pack,
    to_pairs,
)

scalars_strategies = strategies.just(
    strategies.fractions(MIN_SCALAR, MAX_SCALAR)
)


def scalars_to_segments(
    scalars: Strategy[ScalarT],
) -> Strategy[Segment[ScalarT]]:
    return (
        to_pairs(scalars_to_points(scalars))
        .filter(pack(ne))
        .map(pack(context.segment_cls))
    )


def scalars_to_points(scalars: Strategy[ScalarT]) -> Strategy[Point[ScalarT]]:
    return strategies.builds(context.point_cls, scalars, scalars)


points_strategies = scalars_strategies.map(scalars_to_points)
segments_strategies = scalars_strategies.map(scalars_to_segments)
