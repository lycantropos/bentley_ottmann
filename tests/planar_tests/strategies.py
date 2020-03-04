from functools import partial

from hypothesis import strategies

from tests.strategies import (points_strategies,
                              segments_strategies)

contours = points_strategies.flatmap(strategies.lists)
non_empty_contours = (points_strategies
                      .flatmap(partial(strategies.lists,
                                       min_size=3)))
segments_lists = segments_strategies.flatmap(strategies.lists)
empty_contours = empty_segments_lists = strategies.builds(list)
non_empty_segments_lists = (segments_strategies
                            .flatmap(partial(strategies.lists,
                                             min_size=1)))
