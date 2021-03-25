from typing import (Iterable,
                    Tuple,
                    TypeVar)

_T = TypeVar('_T')


def pairwise(ids: Iterable[_T]) -> Iterable[Tuple[_T, _T]]:
    iterator = iter(ids)
    value = next(iterator)
    for next_value in iterator:
        yield value, next_value
        value = next_value


def to_sorted_pair(first: _T, second: _T) -> Tuple[_T, _T]:
    return (first, second) if first < second else (second, first)
