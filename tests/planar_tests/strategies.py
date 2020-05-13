from functools import partial
from itertools import repeat
from typing import Tuple

from hypothesis import strategies

from bentley_ottmann.hints import Point
from tests.strategies import (points_strategies,
                              segments_strategies)
from tests.utils import Strategy

contours = points_strategies.flatmap(partial(strategies.lists,
                                             min_size=3))
non_triangular_contours = (points_strategies
                           .flatmap(partial(strategies.lists,
                                            min_size=4)))
triangular_contours = (points_strategies
                       .flatmap(partial(strategies.lists,
                                        min_size=3,
                                        max_size=3)))
degenerate_contours = (points_strategies
                       .flatmap(partial(strategies.lists,
                                        max_size=2)))
segments_lists = segments_strategies.flatmap(strategies.lists)
empty_segments_lists = strategies.builds(list)
non_empty_segments_lists = (segments_strategies
                            .flatmap(partial(strategies.lists,
                                             min_size=1)))


def points_to_degenerate_segments(points: Strategy[Point]
                                  ) -> Strategy[Tuple[Point, Point]]:
    return (points.map(partial(repeat,
                               times=2))
            .map(tuple))


degenerate_segments = points_strategies.flatmap(points_to_degenerate_segments)
degenerate_segments_lists = strategies.lists(degenerate_segments,
                                             min_size=1)
