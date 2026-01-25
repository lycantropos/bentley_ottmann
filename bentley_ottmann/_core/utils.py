from collections.abc import Hashable, Iterable
from typing import Protocol, TypeVar

from typing_extensions import Self


class Ordered(Protocol):
    def __lt__(self, other: Self, /) -> bool: ...


_HashableT = TypeVar('_HashableT', bound=Hashable)


def all_unique(values: Iterable[_HashableT], /) -> bool:
    seen: set[_HashableT] = set()
    seen_add = seen.add
    for value in values:
        if value in seen:
            return False
        seen_add(value)
    return True


def is_even(value: int, /) -> bool:
    return not (value & 1)


_OrderedT = TypeVar('_OrderedT', bound=Ordered)


def to_sorted_pair(
    first: _OrderedT, second: _OrderedT, /
) -> tuple[_OrderedT, _OrderedT]:
    return (first, second) if first < second else (second, first)
