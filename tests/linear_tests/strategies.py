from tests.strategies import (real_segments_strategies,
                              segments_strategies)
from tests.utils import (identity,
                         to_pairs)

segments = segments_strategies.flatmap(identity)
real_segments = real_segments_strategies.flatmap(identity)
segments_pairs = segments_strategies.flatmap(to_pairs)
real_segments_pairs = real_segments_strategies.flatmap(to_pairs)
