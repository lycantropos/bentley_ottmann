from reprlib import recursive_repr
from typing import (Dict,
                    List,
                    Optional)

from ground.base import Relation
from ground.hints import Point
from reprit.base import generate_repr

from .hints import Ids


class Event:
    __slots__ = ('complement', 'is_left_endpoint', 'original_start',
                 'relations', 'segments_ids', 'start')

    def __init__(self,
                 start: Point,
                 complement: Optional['Event'],
                 is_left_endpoint: bool,
                 original_start: Point,
                 segments_ids: Ids,
                 relations: Dict[Relation, List[Ids]]) -> None:
        self.complement, self.original_start, self.start = (
            complement, original_start, start)
        self.is_left_endpoint = is_left_endpoint
        self.relations, self.segments_ids = relations, segments_ids

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.complement.start

    @property
    def original_end(self) -> Point:
        return self.complement.original_start
