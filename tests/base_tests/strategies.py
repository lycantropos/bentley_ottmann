from functools import partial
from typing import Sequence

from hypothesis import strategies

from bentley_ottmann.linear import Segment
from bentley_ottmann.point import Point
from tests.strategies import (points_strategies,
                              segments_strategies)


def vertices_to_edges(vertices: Sequence[Point]) -> Sequence[Segment]:
    return [Segment(vertices[index], vertices[(index + 1) % len(vertices)])
            for index in range(len(vertices))]


to_non_empty_lists = partial(strategies.lists,
                             min_size=1)
edges_lists = (points_strategies
               .flatmap(strategies.lists)
               .map(vertices_to_edges))
non_empty_edges_lists = (points_strategies
                         .flatmap(to_non_empty_lists)
                         .map(vertices_to_edges))
segments_lists = segments_strategies.flatmap(strategies.lists)
empty_edges_lists = empty_segments_lists = strategies.builds(list)
non_empty_segments_lists = segments_strategies.flatmap(to_non_empty_lists)
