from functools import partial
from itertools import combinations
from typing import Sequence


def merge_ids(left_ids: Sequence[int],
              right_ids: Sequence[int]) -> Sequence[int]:
    return sorted({*left_ids, *right_ids})


to_pairs_combinations = partial(combinations,
                                r=2)
