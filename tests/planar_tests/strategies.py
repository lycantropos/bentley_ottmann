from functools import partial

from hypothesis import strategies

from tests.strategies import (points_strategies,
                              segments_strategies)

vertices_lists = (points_strategies
                  .flatmap(strategies.lists))
non_empty_vertices_lists = (points_strategies
                            .flatmap(partial(strategies.lists,
                                             min_size=3)))
segments_lists = segments_strategies.flatmap(strategies.lists)
empty_vertices_lists = empty_segments_lists = strategies.builds(list)
non_empty_segments_lists = (segments_strategies
                            .flatmap(partial(strategies.lists,
                                             min_size=1)))
