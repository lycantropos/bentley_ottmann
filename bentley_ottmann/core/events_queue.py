from typing import Sequence

from ground.base import (Context,
                         Relation)
from ground.hints import (Point,
                          Segment)
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .event import Event
from .sweep_line import SweepLine
from .utils import classify_overlap


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
    @classmethod
    def from_segments(cls,
                      segments: Sequence[Segment],
                      *,
                      context: Context) -> 'EventsQueue':
        result = cls(context)
        for index, segment in enumerate(segments):
            event = Event.from_segment(segment, index)
            result.push(event)
            result.push(event.opposite)
        return result

    __slots__ = 'context', '_queue'

    def __init__(self, context: Context) -> None:
        self.context = context
        self._queue = PriorityQueue(key=EventsQueueKey)

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    def detect_intersection(self,
                            below_event: Event,
                            event: Event,
                            sweep_line: SweepLine) -> None:
        relation = self.context.segments_relation(
                below_event.start, below_event.end, event.start, event.end)
        if relation is Relation.DISJOINT:
            return
        elif relation is Relation.TOUCH or relation is Relation.CROSS:
            # segments touch or cross
            point = self.context.segments_intersection(
                    below_event.start, below_event.end, event.start, event.end)
            assert event.ids.isdisjoint(below_event.ids)
            if point != below_event.start and point != below_event.end:
                below_below = sweep_line.below(below_event)
                assert (below_below is None
                        or below_below.start != below_event.start
                        or below_below.end != point)
                self._divide_segment(below_event, point)
            if point != event.start and point != event.end:
                above_event = sweep_line.above(event)
                if (above_event is not None
                        and above_event.start == event.start
                        and above_event.end == point):
                    sweep_line.remove(above_event)
                    event.merge_with(above_event)
                self._divide_segment(event, point)
            touching_event = (event
                              if point == event.start
                              else event.opposite)
            touching_below_event = (below_event
                                    if point == below_event.start
                                    else below_event.opposite)
            touching_event.register_tangent(touching_below_event)
            touching_below_event.register_tangent(touching_event)
            full_relation = (relation
                             if (relation is Relation.CROSS
                                 or point == below_event.original_start
                                 or point == below_event.original_end
                                 or point == event.original_start
                                 or point == event.original_end)
                             else Relation.CROSS)
        else:
            # segments overlap
            starts_equal = event.start == below_event.start
            start_min, start_max = (
                (event, below_event)
                if (starts_equal
                    or EventsQueueKey(event) < EventsQueueKey(below_event))
                else (below_event, event))
            ends_equal = event.end == below_event.end
            end_min, end_max = (
                (event.opposite, below_event.opposite)
                if ends_equal or (EventsQueueKey(event.opposite)
                                  < EventsQueueKey(below_event.opposite))
                else (below_event.opposite, event.opposite))
            if starts_equal:
                assert not ends_equal
                # segments share the left endpoint
                sweep_line.remove(end_max.opposite)
                self._divide_segment(end_max.opposite, end_min.start)
                event.merge_with(below_event)
            elif ends_equal:
                # segments share the right endpoint
                self._divide_segment(start_min, start_max.start)
            elif start_min is end_max.opposite:
                # one line segment includes the other one
                self._divide_segment(start_min, end_min.start)
                self._divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                self._divide_segment(start_max, end_min.start)
                self._divide_segment(start_min, start_max.start)
            full_relation = classify_overlap(below_event.original_start,
                                             below_event.original_end,
                                             event.original_start,
                                             event.original_end)
        event.add_relation(full_relation)
        below_event.add_relation(full_relation.complement)

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

    def _divide_segment(self, event: Event, break_point: Point) -> None:
        ids = event.ids
        left_event = event.opposite.opposite = Event(
                break_point, event.opposite, True, event.original_start,
                event.parts_ids)
        right_event = event.opposite = Event(break_point, event, False,
                                             event.original_end,
                                             event.opposite.parts_ids)
        (left_event.parts_ids.setdefault(break_point, {})
         .setdefault(left_event.end, set()).update(ids))
        (right_event.parts_ids[right_event.end].setdefault(break_point, set())
         .update(ids))
        self.push(left_event)
        self.push(right_event)
