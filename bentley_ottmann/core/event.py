from abc import (ABC,
                 abstractmethod)
from reprlib import recursive_repr
from typing import (Dict,
                    List,
                    Optional,
                    Sequence,
                    Set)

from ground.base import Relation
from ground.hints import (Point,
                          Segment)
from reprit.base import generate_repr

from .utils import (classify_overlap,
                    to_sorted_pair)


class Event(ABC):
    __slots__ = ()

    is_left = False
    left = None  # type: Optional['LeftEvent']
    right = None  # type: Optional['RightEvent']

    @property
    @abstractmethod
    def end(self) -> Point:
        """Returns end of the event."""

    @property
    @abstractmethod
    def original_end(self) -> Point:
        """Returns original end of the event."""

    @property
    @abstractmethod
    def original_start(self) -> Point:
        """Returns original start of the segment."""

    @abstractmethod
    def register_tangent(self, tangent: 'Event') -> None:
        """Registers new tangent to the event"""

    @property
    @abstractmethod
    def segments_ids(self) -> Set[int]:
        """Returns segments ids of the event."""

    @property
    @abstractmethod
    def start(self) -> Point:
        """Returns start of the event."""

    @property
    @abstractmethod
    def tangents(self) -> Sequence['Event']:
        """Returns tangents of the event."""


class LeftEvent(Event):
    @classmethod
    def from_segment(cls, segment: Segment, segment_id: int) -> 'LeftEvent':
        start, end = to_sorted_pair(segment.start, segment.end)
        result = LeftEvent(start, None, start, {start: {end: {segment_id}}})
        result.right = RightEvent(end, result, end)
        return result

    is_left = True

    @property
    def end(self) -> Point:
        return self.right.start

    @property
    def original_start(self) -> Point:
        return self._original_start

    @property
    def original_end(self) -> Point:
        return self.right.original_start

    @property
    def segments_ids(self) -> Set[int]:
        return self.parts_ids[self.start][self.end]

    @property
    def start(self) -> Point:
        return self._start

    @property
    def tangents(self) -> Sequence[Event]:
        return self._tangents

    __slots__ = ('right', 'parts_ids', '_original_start',
                 '_start', '_tangents', '_relations_mask')

    def __init__(self,
                 start: Point,
                 right: Optional['RightEvent'],
                 original_start: Point,
                 parts_ids: Dict[Point, Dict[Point, Set[int]]]) -> None:
        self.right, self.parts_ids, self._original_start, self._start = (
            right, parts_ids, original_start, start)
        self._relations_mask = 0
        self._tangents = []  # type: List[Event]

    __repr__ = recursive_repr()(generate_repr(__init__))

    def divide(self, break_point: Point) -> 'LeftEvent':
        """Divides the event at given break point and returns tail."""
        segments_ids = self.segments_ids
        (self.parts_ids.setdefault(self.start, {})
         .setdefault(break_point, set()).update(segments_ids))
        (self.parts_ids.setdefault(break_point, {})
         .setdefault(self.end, set()).update(segments_ids))
        result = self.right.left = LeftEvent(
                break_point, self.right, self.original_start,
                self.parts_ids)
        self.right = RightEvent(break_point, self, self.original_end)
        return result

    def has_only_relations(self, *relations: Relation) -> bool:
        mask = self._relations_mask
        for relation in relations:
            mask &= ~(1 << relation)
        return not mask

    def merge_with(self, other: 'LeftEvent') -> None:
        assert self.start == other.start and self.end == other.end
        full_relation = classify_overlap(
                other.original_start, other.original_end, self.original_start,
                self.original_end)
        self.register_relation(full_relation)
        other.register_relation(full_relation.complement)
        start, end = self.start, self.end
        self.parts_ids[start][end] = other.parts_ids[start][end] = (
                self.parts_ids[start][end] | other.parts_ids[start][end])

    def register_tangent(self, tangent: Event) -> None:
        assert self.start == tangent.start
        assert tangent not in self._tangents
        self._tangents.append(tangent)

    def register_relation(self, relation: Relation) -> None:
        self._relations_mask |= 1 << relation


class RightEvent(Event):
    @property
    def end(self) -> Point:
        return self.left.start

    @property
    def original_end(self) -> Point:
        return self.left.original_start

    @property
    def original_start(self) -> Point:
        return self._original_start

    @property
    def segments_ids(self) -> Set[int]:
        return self.left.segments_ids

    @property
    def start(self) -> Point:
        return self._start

    @property
    def tangents(self) -> Sequence[Event]:
        return self._tangents

    __slots__ = 'left', '_original_start', '_start', '_tangents'

    def __init__(self,
                 start: Point,
                 left: Optional[LeftEvent],
                 original_start: Point) -> None:
        self.left, self._original_start, self._start = (left, original_start,
                                                        start)
        self._tangents = []  # type: List[Event]

    __repr__ = recursive_repr()(generate_repr(__init__))

    def register_tangent(self, tangent: 'Event') -> None:
        assert self.start == tangent.start
        assert tangent not in self._tangents
        self._tangents.append(tangent)
