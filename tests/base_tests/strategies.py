from hypothesis import strategies

from tests.strategies import segments_strategies

segments_lists = segments_strategies.flatmap(strategies.lists)
