from tests.strategies import segments_strategies
from tests.utils import (identity,
                         to_pairs)

segments = segments_strategies.flatmap(identity)
segments_pairs = segments_strategies.flatmap(to_pairs)
