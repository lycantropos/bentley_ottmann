from reprlib import recursive_repr
from typing import (Optional,
                    Sequence)

from ground.base import Relation
from ground.hints import Point
from reprit.base import generate_repr


class Event:
    __slots__ = ('is_left_endpoint', 'relation', 'start', 'complement',
                 'segments_ids')

    def __init__(self,
                 is_left_endpoint: bool,
                 relation: Relation,
                 start: Point,
                 complement: Optional['Event'],
                 segments_ids: Sequence[int]) -> None:
        self.is_left_endpoint = is_left_endpoint
        self.relation = relation
        self.start = start
        self.complement = complement
        self.segments_ids = segments_ids

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.complement.start

    def set_both_relations(self, relation: Relation) -> None:
        self.relation = self.complement.relation = relation
