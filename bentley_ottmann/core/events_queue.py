from typing import Sequence

from ground.base import (Context,
                         Relation)
from ground.hints import Segment
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .event import (Event,
                    LeftEvent)
from .sweep_line import SweepLine


class EventsQueue:
    @classmethod
    def from_segments(cls,
                      segments: Sequence[Segment],
                      *,
                      context: Context) -> 'EventsQueue':
        result = cls(context)
        for index, segment in enumerate(segments):
            event = LeftEvent.from_segment(segment, index)
            result.push(event)
            result.push(event.right)
        return result

    __slots__ = 'context', '_queue'

    def __init__(self, context: Context) -> None:
        self.context = context
        self._queue = PriorityQueue(key=EventsQueueKey)

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        return bool(self._queue)

    def detect_intersection(self,
                            below_event: LeftEvent,
                            event: LeftEvent,
                            sweep_line: SweepLine) -> None:
        relation = self.context.segments_relation(below_event, event)
        if relation is Relation.DISJOINT:
            return
        elif relation is Relation.TOUCH or relation is Relation.CROSS:
            # segments touch or cross
            point = self.context.segments_intersection(below_event, event)
            assert event.segments_ids.isdisjoint(below_event.segments_ids)
            if point != below_event.start and point != below_event.end:
                below_below_event = sweep_line.below(below_event)
                assert not (below_below_event is not None
                            and below_below_event.start == below_event.start
                            and below_below_event.end == point)
                (
                    point_to_below_event_start_event,
                    point_to_below_event_end_event
                ) = below_event.divide(point)
                self.push(point_to_below_event_start_event)
                self.push(point_to_below_event_end_event)
            if point != event.start and point != event.end:
                above_event = sweep_line.above(event)
                if (above_event is not None
                        and above_event.start == event.start
                        and above_event.end == point):
                    sweep_line.remove(above_event)
                    (
                        point_to_event_start_event, point_to_event_end_event
                    ) = event.divide(point)
                    self.push(point_to_event_start_event)
                    self.push(point_to_event_end_event)
                    event.merge_with(above_event)
                else:
                    (
                        point_to_event_start_event, point_to_event_end_event
                    ) = event.divide(point)
                    self.push(point_to_event_start_event)
                    self.push(point_to_event_end_event)
        else:
            # segments overlap
            starts_equal = event.start == below_event.start
            min_start_event, max_start_event = (
                (event, below_event)
                if (starts_equal
                    or EventsQueueKey(event) < EventsQueueKey(below_event))
                else (below_event, event)
            )
            ends_equal = event.end == below_event.end
            min_end_event, max_end_event = (
                (event.right, below_event.right)
                if ends_equal or (EventsQueueKey(event.right)
                                  < EventsQueueKey(below_event.right))
                else (below_event.right, event.right)
            )
            if starts_equal:
                assert not ends_equal
                # segments share the left endpoint
                sweep_line.remove(max_end_event.left)
                _, min_end_to_max_end_event = max_end_event.left.divide(
                        min_end_event.start
                )
                self.push(min_end_to_max_end_event)
                event.merge_with(below_event)
            elif ends_equal:
                # segments share the right endpoint
                (
                    max_start_to_min_start, max_start_to_end_event
                ) = min_start_event.divide(max_start_event.start)
                max_start_event.merge_with(max_start_to_end_event)
                self.push(max_start_to_min_start)
            elif min_start_event is max_end_event.left:
                # one line segment includes the other one
                (
                    min_end_to_min_start_event, min_end_to_max_end_event
                ) = min_start_event.divide(min_end_event.start)
                self.push(min_end_to_min_start_event)
                self.push(min_end_to_max_end_event)
                (
                    max_start_to_min_start_event, max_start_to_min_end_event
                ) = min_start_event.divide(max_start_event.start)
                max_start_event.merge_with(max_start_to_min_end_event)
                self.push(max_start_to_min_start_event)
            else:
                # no line segment includes the other one
                (
                    min_end_to_max_start_event, min_end_to_max_end_event
                ) = max_start_event.divide(min_end_event.start)
                self.push(min_end_to_max_start_event)
                self.push(min_end_to_max_end_event)
                (
                    max_start_to_min_start_event, max_start_to_min_end_event
                ) = min_start_event.divide(max_start_event.start)
                max_start_event.merge_with(max_start_to_min_end_event)
                self.push(max_start_to_min_start_event)

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
        elif event.is_left is not other_event.is_left:
            # same start, but one is a left endpoint
            # and the other is a right endpoint,
            # the right endpoint is processed first
            return not event.is_left
        else:
            # same start,
            # both events are left endpoints or both are right endpoints
            return event.end < other_event.end
