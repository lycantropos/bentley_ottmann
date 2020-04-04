from reprlib import recursive_repr
from typing import (Optional,
                    Sequence)

from reprit.base import generate_repr

from bentley_ottmann.hints import (Coordinate,
                                   Point,
                                   Segment)
from .linear import (SegmentsRelationship,
                     segments_intersection)


class Event:
    __slots__ = ('is_left_endpoint', 'relationship',
                 'start', 'complement', 'segments_ids')

    def __init__(self,
                 is_left_endpoint: bool,
                 relationship: SegmentsRelationship,
                 start: Point,
                 complement: Optional['Event'],
                 segments_ids: Sequence[int]) -> None:
        self.is_left_endpoint = is_left_endpoint
        self.relationship = relationship
        self.start = start
        self.complement = complement
        self.segments_ids = segments_ids

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def is_intersection(self) -> bool:
        return self.relationship is not SegmentsRelationship.NONE

    @property
    def is_vertical(self) -> bool:
        start_x, _ = self.start
        end_x, _ = self.end
        return start_x == end_x

    @property
    def is_horizontal(self) -> bool:
        _, start_y = self.start
        _, end_y = self.end
        return start_y == end_y

    @property
    def end(self) -> Point:
        return self.complement.start

    @property
    def segment(self) -> Segment:
        return self.start, self.end

    def below_than_at_x(self, other: 'Event', x: Coordinate) -> bool:
        y_at_x, other_y_at_x = self.y_at(x), other.y_at(x)
        if other_y_at_x != y_at_x:
            return y_at_x < other_y_at_x
        else:
            _, start_y = self.start
            _, other_start_y = other.start
            end_x, end_y = self.end
            other_end_x, other_end_y = other.end
            return ((start_y, end_y, other_end_x)
                    < (other_start_y, other_end_y, end_x))

    def y_at(self, x: Coordinate) -> Coordinate:
        if self.is_vertical or self.is_horizontal:
            _, start_y = self.start
            return start_y
        else:
            start_x, start_y = self.start
            if x == start_x:
                return start_y
            end_x, end_y = self.end
            if x == end_x:
                return end_y
            _, result = segments_intersection(self.segment,
                                              ((x, start_y), (x, end_y)))
            return result
