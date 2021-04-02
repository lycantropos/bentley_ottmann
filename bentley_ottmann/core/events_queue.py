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
        relation = self.context.segments_relation(
                below_event.start, below_event.end, event.start, event.end)
        if relation is Relation.DISJOINT:
            return
        elif relation is Relation.TOUCH or relation is Relation.CROSS:
            # segments touch or cross
            point = self.context.segments_intersection(
                    below_event.start, below_event.end, event.start, event.end)
            assert event.segments_ids.isdisjoint(below_event.segments_ids)
            if point != below_event.start and point != below_event.end:
                below_below = sweep_line.below(below_event)
                assert not (below_below is not None
                            and below_below.start == below_event.start
                            and below_below.end == point)
                self.push(below_event.divide(point))
                self.push(below_event.right)
            if point != event.start and point != event.end:
                above_event = sweep_line.above(event)
                if (above_event is not None
                        and above_event.start == event.start
                        and above_event.end == point):
                    sweep_line.remove(above_event)
                    self.push(event.divide(point))
                    self.push(event.right)
                    event.merge_with(above_event)
                else:
                    self.push(event.divide(point))
                    self.push(event.right)
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
                (event.right, below_event.right)
                if ends_equal or (EventsQueueKey(event.right)
                                  < EventsQueueKey(below_event.right))
                else (below_event.right, event.right))
            if starts_equal:
                assert not ends_equal
                # segments share the left endpoint
                sweep_line.remove(end_max.left)
                self.push(end_max.left.divide(end_min.start))
                event.merge_with(below_event)
            elif ends_equal:
                # segments share the right endpoint
                start_max.merge_with(start_min.divide(start_max.start))
                self.push(start_min.right)
            elif start_min is end_max.left:
                # one line segment includes the other one
                self.push(start_min.divide(end_min.start))
                self.push(start_min.right)
                start_max.merge_with(start_min.divide(start_max.start))
                self.push(start_min.right)
            else:
                # no line segment includes the other one
                self.push(start_max.divide(end_min.start))
                start_max.merge_with(start_min.divide(start_max.start))
                self.push(start_max.right)
                self.push(start_min.right)

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
