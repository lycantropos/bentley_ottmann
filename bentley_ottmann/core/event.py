from reprlib import recursive_repr
from typing import (Dict,
                    Optional,
                    Set)

from ground.base import Relation
from ground.hints import Point
from reprit.base import generate_repr


class Event:
    __slots__ = ('opposite', 'is_left_endpoint', 'relation', 'start',
                 'points_ids')

    def __init__(self,
                 start: Point,
                 opposite: Optional['Event'],
                 is_left_endpoint: bool,
                 relation: Relation,
                 points_ids: Dict[Point, Dict[Point, Set[int]]]) -> None:
        self.is_left_endpoint, self.opposite, self.points_ids, self.start = (
            is_left_endpoint, opposite, points_ids, start)
        self.relation = relation

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.opposite.start

    def set_both_relations(self, relation: Relation) -> None:
        self.relation = self.opposite.relation = relation

    def merge_with(self, other: 'Event') -> None:
        self._assimilate(other)
        other._assimilate(self)

    def _assimilate(self, other: 'Event') -> None:
        end, points_ids, start = self.end, self.points_ids, self.start
        for other_start, other_ends_ids in other.points_ids.items():
            if other_start < start:
                continue
            for other_end, other_ids in other_ends_ids.items():
                if end < other_end:
                    continue
                (points_ids.setdefault(other_start, {})
                 .setdefault(other_end, set())).update(other_ids)
