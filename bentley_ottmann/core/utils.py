from functools import partial
from heapq import merge
from itertools import (combinations,
                       groupby)
from typing import Sequence


def merge_ids(left_ids: Sequence[int],
              right_ids: Sequence[int]) -> Sequence[int]:
    return [key for key, _ in groupby(merge(left_ids, right_ids))]


to_pairs_combinations = partial(combinations,
                                r=2)
