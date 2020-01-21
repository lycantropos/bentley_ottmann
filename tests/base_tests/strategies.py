from functools import partial

from hypothesis import strategies

from tests.strategies import segments_strategies

segments_lists = segments_strategies.flatmap(strategies.lists)
empty_segments_lists = strategies.builds(list)
non_empty_segments_lists = (segments_strategies
                            .flatmap(partial(strategies.lists,
                                             min_size=1)))
