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
    __slots__ = ('is_left_endpoint', 'relationship', 'start', 'complement',
                 'segments_ids')

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

    def set_both_relationships(self, relationship: SegmentsRelationship
                               ) -> None:
        self.relationship = self.complement.relationship = relationship

    def y_at(self, x: Coordinate) -> Coordinate:
        if self.is_vertical or self.is_horizontal:
            _, start_y = self.start
            return start_y
        else:
            _, start_y = self.start
            _, end_y = self.end
            _, result = segments_intersection(self.segment,
                                              ((x, start_y), (x, end_y)))
            return result
