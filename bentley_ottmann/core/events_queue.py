from typing import Sequence

from ground.base import (Context,
                         Relation)
from ground.hints import (Point,
                          Segment)
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .event import Event
from .utils import to_sorted_pair


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
        result._populate(segments)
        return result

    __slots__ = 'context', '_queue'

    def __init__(self, context: Context) -> None:
        self.context = context
        self._queue = PriorityQueue(key=EventsQueueKey)

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    def detect_intersection(self, below_event: Event, event: Event) -> None:
        relation = self.context.segments_relation(
                below_event.start, below_event.end, event.start, event.end)
        if relation is Relation.TOUCH or relation is Relation.CROSS:
            # segments touch or cross
            point = self.context.segments_intersection(
                    below_event.start, below_event.end, event.start, event.end)
            if point != below_event.start and point != below_event.end:
                self._divide_segment(below_event, point)
            if point != event.start and point != event.end:
                self._divide_segment(event, point)
        elif (relation is not Relation.DISJOINT
              and relation is not Relation.EQUAL):
            # segments overlap
            starts_equal = event.start == below_event.start
            start_min, start_max = (
                (None, None)
                if starts_equal
                else ((event, below_event)
                      if EventsQueueKey(event) < EventsQueueKey(below_event)
                      else (below_event, event)))
            ends_equal = event.end == below_event.end
            end_min, end_max = (
                (None, None)
                if ends_equal
                else ((event.complement, below_event.complement)
                      if (EventsQueueKey(event.complement)
                          < EventsQueueKey(below_event.complement))
                      else (below_event.complement, event.complement)))
            if starts_equal:
                # segments share the left endpoint
                self._divide_segment(end_max.complement, end_min.start)
            elif ends_equal:
                # segments share the right endpoint
                self._divide_segment(start_min, start_max.start)
            elif start_min is end_max.complement:
                # one line segment includes the other one
                self._divide_segment(start_min, end_min.start)
                self._divide_segment(start_min, start_max.start)
            else:
                # no line segment includes the other one
                self._divide_segment(start_max, end_min.start)
                self._divide_segment(start_min, start_max.start)

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
        left_event = event.complement.complement = Event(
                break_point, event.complement, True, event.original_start,
                event.segments_ids, event.relations)
        right_event = event.complement = Event(
                break_point, event, False, event.original_end,
                event.complement.segments_ids, event.complement.relations)
        self.push(left_event)
        self.push(right_event)

    def _populate(self, segments: Sequence[Segment]) -> None:
        endpoints_with_ids = sorted(
                (to_sorted_pair(segment.start, segment.end),
                 segment_id)
                for segment_id, segment in enumerate(segments))
        index = 0
        while index < len(endpoints_with_ids):
            endpoints, segment_id = endpoints_with_ids[index]
            index += 1
            same_segments_ids = [segment_id]
            while (index < len(endpoints_with_ids)
                   and endpoints_with_ids[index][0] == endpoints):
                same_segments_ids.append(endpoints_with_ids[index][1])
                index += 1
            same_segments_ids = tuple(same_segments_ids)
            start, end = endpoints
            relations = {}
            start_event = Event(start, None, True, start, same_segments_ids,
                                relations)
            end_event = Event(end, start_event, False, end, same_segments_ids,
                              relations)
            start_event.complement = end_event
            self.push(start_event)
            self.push(end_event)
