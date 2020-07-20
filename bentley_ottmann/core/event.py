from reprlib import recursive_repr
from typing import (Optional,
                    Sequence)

from reprit.base import generate_repr

from bentley_ottmann.hints import (Point,
                                   Segment)
from .linear import SegmentsRelationship


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
    def end(self) -> Point:
        return self.complement.start

    @property
    def segment(self) -> Segment:
        return self.start, self.end

    def set_both_relationships(self, relationship: SegmentsRelationship
                               ) -> None:
        self.relationship = self.complement.relationship = relationship
