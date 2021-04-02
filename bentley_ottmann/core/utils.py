from itertools import combinations
from typing import (Hashable,
                    Iterable,
                    Tuple,
                    TypeVar)

from ground.base import Relation
from ground.hints import Point

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


def classify_overlap(test_start: Point,
                     test_end: Point,
                     goal_start: Point,
                     goal_end: Point) -> Relation:
    assert test_start < test_end
    assert goal_start < goal_end
    if test_start == goal_start:
        return (Relation.COMPONENT
                if test_end < goal_end
                else (Relation.COMPOSITE
                      if goal_end < test_end
                      else Relation.EQUAL))
    elif test_end == goal_end:
        return (Relation.COMPOSITE
                if test_start < goal_start
                else Relation.COMPONENT)
    elif goal_start < test_start < goal_end:
        return (Relation.COMPONENT
                if test_end < goal_end
                else Relation.OVERLAP)
    else:
        assert test_start < goal_start < test_end
        return (Relation.COMPOSITE
                if goal_end < test_end
                else Relation.OVERLAP)


def to_pairs_combinations(iterable: Iterable[_T]) -> Iterable[Tuple[_T, _T]]:
    return combinations(iterable,
                        r=2)


def to_sorted_pair(start: _T, end: _T) -> Tuple[_T, _T]:
    return (start, end) if start < end else (end, start)
