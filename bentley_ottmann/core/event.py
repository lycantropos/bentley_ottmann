from reprlib import recursive_repr
from typing import (Dict,
                    List,
                    Optional,
                    Set)

from ground.hints import (Point,
                          Segment)
from reprit.base import generate_repr

from .utils import to_sorted_pair


class Event:
    @classmethod
    def from_segment(cls, segment: Segment, segment_id: int) -> 'Event':
        start, end = to_sorted_pair(segment.start, segment.end)
        points_ids = {start: {end: {segment_id}}}
        result = Event(start, None, True, points_ids)
        opposite = Event(end, result, False, points_ids)
        result.opposite = opposite
        return result

    __slots__ = ('is_left_endpoint', 'opposite', 'parts_ids', 'start',
                 'tangents', '_relations')

    def __init__(self,
                 start: Point,
                 opposite: Optional['Event'],
                 is_left_endpoint: bool,
                 parts_ids: Dict[Point, Dict[Point, Set[int]]]) -> None:
        self.is_left_endpoint, self.opposite, self.parts_ids, self.start = (
            is_left_endpoint, opposite, parts_ids, start)
        self.tangents = []  # type: List[Event]

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.opposite.start

    @property
    def ids(self) -> Set[int]:
        return (self.parts_ids[self.start][self.end]
                if self.is_left_endpoint
                else self.parts_ids[self.end][self.start])

    def merge_with(self, other: 'Event') -> None:
        assert self.is_left_endpoint
        assert other.is_left_endpoint
        self._assimilate(other)
        other._assimilate(self)

    def _assimilate(self, other: 'Event') -> None:
        end, parts_ids, start = self.end, self.parts_ids, self.start
        for other_start, other_ends_ids in other.parts_ids.items():
            if other_start < start:
                continue
            for other_end, other_ids in other_ends_ids.items():
                if end < other_end:
                    continue
                if other_end in parts_ids.setdefault(other_start, {}):
                    parts_ids[other_start][other_end].update(other_ids)
                else:
                    parts_ids[other_start][other_end] = other_ids
