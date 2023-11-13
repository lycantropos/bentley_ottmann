import typing as t
import typing_extensions as te
from ground.base import Relation
from ground.hints import Point

_HashableT = t.TypeVar('_HashableT', bound=t.Hashable)

"""
This utility module provides essential functions and type declarations used in geometric computations, 
particularly for the Bentley-Ottmann algorithm. It includes methods for determining uniqueness in a 
collection, classifying the type of overlap between two line segments, and sorting pairs of comparable objects.

Functions:
    - all_unique: Determines if all elements in an iterable are unique.
    - classify_overlap: Classifies the type of overlap between two line segments.
    - to_sorted_pair: Sorts a pair of comparable objects into order.

TypeVar:
    - _HashableT: A type variable bound to hashable types.
    - _ComparableT: A type variable bound to objects implementing the comparison protocol.
"""

def all_unique(values: t.Iterable[_HashableT]) -> bool:
    """
    Checks if all elements in an iterable are unique.

    Args:
        values (t.Iterable[_HashableT]): An iterable of hashable objects.

    Returns:
        bool: True if all elements are unique, False otherwise.
    """
    seen: t.Set[_HashableT] = set()
    seen_add = seen.add
    for value in values:
        # If the value has already been seen, return False
        if value in seen:
            return False
        # Otherwise, add the value to the seen set
        else:
            seen_add(value)
    # All elements are unique if this point is reached
    return True

def classify_overlap(test_start: Point, test_end: Point, goal_start: Point, goal_end: Point) -> Relation:
    """
    Classifies the type of overlap between two line segments.

    Args:
        test_start, test_end (Point): Start and end points of the first segment.
        goal_start, goal_end (Point): Start and end points of the second segment.

    Returns:
        Relation: The type of overlap (COMPONENT, COMPOSITE, EQUAL, or OVERLAP) between the two segments.
    """
    assert test_start < test_end
    assert goal_start < goal_end
    # Determine the type of overlap based on the relative positions of the segment endpoints
    if test_start == goal_start:
        return (Relation.COMPONENT if test_end < goal_end else (Relation.COMPOSITE if goal_end < test_end else Relation.EQUAL))
    elif test_end == goal_end:
        return (Relation.COMPOSITE if test_start < goal_start else Relation.COMPONENT)
    elif goal_start < test_start < goal_end:
        return (Relation.COMPONENT if test_end < goal_end else Relation.OVERLAP)
    else:
        assert test_start < goal_start < test_end
        return (Relation.COMPOSITE if goal_end < test_end else Relation.OVERLAP)

class _Comparable(te.Protocol):
    """
    A protocol for types that support comparison.

    This protocol ensures that the implementing type supports the less-than comparison operator.
    """
    def __lt__(self, other: te.Self) -> bool:
        ...

_ComparableT = t.TypeVar('_ComparableT', bound=_Comparable)

def to_sorted_pair(start: _ComparableT, end: _ComparableT) -> t.Tuple[_ComparableT, _ComparableT]:
    """
    Sorts a pair of comparable objects into order.

    Args:
        start, end (_ComparableT): A pair of comparable objects.

    Returns:
        t.Tuple[_ComparableT, _ComparableT]: A tuple of the two objects, sorted in order.
    """
    # Returns the pair in sorted order based on the comparison protocol
    return (start, end) if start < end else (end, start)
