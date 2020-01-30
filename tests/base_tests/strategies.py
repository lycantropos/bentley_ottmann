from functools import partial

from hypothesis import strategies

from bentley_ottmann.base import _vertices_to_edges
from tests.strategies import (points_strategies,
                              segments_strategies)

to_non_empty_lists = partial(strategies.lists,
                             min_size=1)
edges_lists = (points_strategies
               .flatmap(strategies.lists)
               .map(_vertices_to_edges))
non_empty_edges_lists = (points_strategies
                         .flatmap(to_non_empty_lists)
                         .map(_vertices_to_edges))
segments_lists = segments_strategies.flatmap(strategies.lists)
empty_edges_lists = empty_segments_lists = strategies.builds(list)
non_empty_segments_lists = segments_strategies.flatmap(to_non_empty_lists)
