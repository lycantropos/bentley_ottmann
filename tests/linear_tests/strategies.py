from tests.strategies import segments_strategies
from tests.utils import to_pairs

segments_pairs = segments_strategies.flatmap(to_pairs)
