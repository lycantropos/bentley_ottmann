from reprlib import recursive_repr
from typing import (Optional,
                    Sequence)

from ground.base import Relation
from ground.hints import Point
from reprit.base import generate_repr


class Event:
    __slots__ = ('complement', 'is_left_endpoint', 'relation', 'segments_ids',
                 'start')

    def __init__(self,
                 start: Point,
                 complement: Optional['Event'],
                 is_left_endpoint: bool,
                 relation: Relation,
                 segments_ids: Sequence[int]) -> None:
        self.start, self.complement = start, complement
        self.is_left_endpoint = is_left_endpoint
        self.relation = relation
        self.segments_ids = segments_ids

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.complement.start

    def set_both_relations(self, relation: Relation) -> None:
        self.relation = self.complement.relation = relation
