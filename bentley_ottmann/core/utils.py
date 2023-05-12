import typing as t

import typing_extensions as te
from ground.base import Relation
from ground.hints import Point

_HashableT = t.TypeVar('_HashableT',
                       bound=t.Hashable)


def all_unique(values: t.Iterable[_HashableT]) -> bool:
    seen: t.Set[_HashableT] = set()
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


class _Comparable(te.Protocol):
    def __lt__(self, other: te.Self) -> bool:
        ...


_ComparableT = t.TypeVar('_ComparableT',
                         bound=_Comparable)


def to_sorted_pair(
        start: _ComparableT, end: _ComparableT
) -> t.Tuple[_ComparableT, _ComparableT]:
    return (start, end) if start < end else (end, start)
