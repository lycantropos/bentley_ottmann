from typing import (Iterable,
                    Sequence,
                    Tuple,
                    TypeVar)

from .hints import Ids

_T = TypeVar('_T')


def pairwise(ids: Iterable[_T]) -> Iterable[Tuple[_T, _T]]:
    iterator = iter(ids)
    value = next(iterator)
    for next_value in iterator:
        yield value, next_value
        value = next_value


def to_ids_pairs(id_: int, other_ids: Ids) -> Sequence[Tuple[int, int]]:
    return [to_sorted_pair(id_, other_id) for other_id in other_ids]


def to_sorted_pair(first: _T, second: _T) -> Tuple[_T, _T]:
    return (first, second) if first < second else (second, first)
