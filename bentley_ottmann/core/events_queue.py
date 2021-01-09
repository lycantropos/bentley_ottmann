from typing import (Optional,
                    Sequence)

from ground.base import (Relation,
                         get_context)
from ground.hints import Point
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .event import Event
from .utils import merge_ids


class EventsQueueKey:
    __slots__ = 'event',

    def __init__(self, event: Event) -> None:
        self.event = event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'EventsQueueKey') -> bool:
        """
        Checks if the event should be processed before the other.
        """
        event, other_event = self.event, other.event
        start_x, start_y = event.start.x, event.start.y
        other_start_x, other_start_y = other_event.start.x, other_event.start.y
        if start_x != other_start_x:
            # different x-coordinate,
            # the event with lower x-coordinate is processed first
            return start_x < other_start_x
        elif start_y != other_start_y:
            # different starts, but same x-coordinate,
            # the event with lower y-coordinate is processed first
            return start_y < other_start_y
        elif event.is_left_endpoint is not other_event.is_left_endpoint:
            # same start, but one is a left endpoint
            # and the other is a right endpoint,
            # the right endpoint is processed first
            return not event.is_left_endpoint
        else:
            # same start,
            # both events are left endpoints or both are right endpoints
            return event.end < other_event.end


class EventsQueue:
    __slots__ = '_queue', '_segments_relater', '_segments_intersector'

    def __init__(self) -> None:
        self._queue = PriorityQueue(key=EventsQueueKey)
        context = get_context()
        self._segments_relater = context.segments_relation
        self._segments_intersector = context.segments_intersection

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    def detect_intersection(self, below_event: Event, event: Event) -> None:
        relation = self._segments_relater(below_event.start, below_event.end,
                                          event.start, event.end)
        if relation is Relation.TOUCH or relation is Relation.CROSS:
            # segments touch or cross
            point = self._segments_intersector(
                    below_event.start, below_event.end, event.start, event.end)
            if point != below_event.start and point != below_event.end:
                self._divide_segment(below_event, point)
            if point != event.start and point != event.end:
                self._divide_segment(event, point)
            event.set_both_relations(max(event.relation,
                                         relation))
            below_event.set_both_relations(max(below_event.relation,
                                               relation))
        elif relation is not Relation.DISJOINT:
            # segments overlap
            starts_equal = event.start == below_event.start
            if starts_equal:
                start_min = start_max = None
            elif EventsQueueKey(event) < EventsQueueKey(below_event):
                start_min, start_max = event, below_event
            else:
                start_min, start_max = below_event, event
            ends_equal = event.end == below_event.end
            if ends_equal:
                end_min = end_max = None
            elif (EventsQueueKey(event.complement)
                  < EventsQueueKey(below_event.complement)):
                end_min, end_max = event.complement, below_event.complement
            else:
                end_min, end_max = below_event.complement, event.complement
            segments_ids = merge_ids(below_event.segments_ids,
                                     event.segments_ids)
            if starts_equal:
                if ends_equal:
                    # segments are equal
                    below_event.segments_ids = event.segments_ids = (
                        segments_ids)
                    event.set_both_relations(relation)
                    below_event.set_both_relations(relation)
                else:
                    # segments share the left endpoint
                    end_min.set_both_relations(relation)
                    end_max.complement.relation = relation
                    self._divide_segment(end_max.complement, end_min.start,
                                         segments_ids)
            elif ends_equal:
                # segments share the right endpoint
                start_max.set_both_relations(relation)
                start_min.complement.relation = relation
                self._divide_segment(start_min, start_max.start, segments_ids)
            elif start_min is end_max.complement:
                # one line segment includes the other one
                start_max.set_both_relations(relation)
                start_min_original_relationship = start_min.relation
                start_min.relation = relation
                self._divide_segment(start_min, end_min.start, segments_ids)
                start_min.relation = start_min_original_relationship
                start_min.complement.relation = relation
                self._divide_segment(start_min, start_max.start, segments_ids)
            else:
                # no line segment includes the other one
                start_max.relation = relation
                self._divide_segment(start_max, end_min.start, segments_ids)
                start_min.complement.relation = relation
                self._divide_segment(start_min, start_max.start, segments_ids)

    def peek(self) -> Event:
        return self._queue.peek()

    def pop(self) -> Event:
        return self._queue.pop()

    def push(self, event: Event) -> None:
        if event.start == event.end:
            raise ValueError('Degenerate segment found '
                             'with both endpoints being: {}.'
                             .format(event.start))
        self._queue.push(event)

    def _divide_segment(self,
                        event: Event,
                        break_point: Point,
                        segments_ids: Optional[Sequence[int]] = None) -> None:
        if segments_ids is None:
            segments_ids = event.segments_ids
        else:
            event.segments_ids = segments_ids
        left_event = Event(is_left_endpoint=True,
                           relation=event.complement.relation,
                           start=break_point,
                           complement=event.complement,
                           segments_ids=segments_ids)
        right_event = Event(is_left_endpoint=False,
                            relation=event.relation,
                            start=break_point,
                            complement=event,
                            segments_ids=segments_ids)
        event.complement.complement, event.complement = left_event, right_event
        self.push(left_event)
        self.push(right_event)
