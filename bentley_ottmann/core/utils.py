from functools import partial
from itertools import combinations
from typing import (Hashable,
                    Iterable,
                    Tuple,
                    TypeVar)

_T = TypeVar('_T')


def all_unique(values: Iterable[Hashable]) -> bool:
    seen = set()
    seen_add = seen.add
    for value in values:
        if value in seen:
            return False
        else:
            seen_add(value)
    return True


def pairwise(ids: Iterable[_T]) -> Iterable[Tuple[_T, _T]]:
    iterator = iter(ids)
    value = next(iterator)
    for next_value in iterator:
        yield value, next_value
        value = next_value


to_pairs_combinations = partial(combinations,
                                r=2)


def to_sorted_pair(first: _T, second: _T) -> Tuple[_T, _T]:
    return (first, second) if first < second else (second, first)
