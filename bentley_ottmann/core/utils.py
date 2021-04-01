from itertools import combinations
from typing import (Iterable,
                    Tuple,
                    TypeVar)

from ground.hints import Point

_T = TypeVar('_T')


def to_pairs_combinations(iterable: Iterable[_T]) -> Iterable[Tuple[_T, _T]]:
    return combinations(iterable,
                        r=2)


def to_sorted_pair(start: Point, end: Point) -> Tuple[Point, Point]:
    return (start, end) if start < end else (end, start)
