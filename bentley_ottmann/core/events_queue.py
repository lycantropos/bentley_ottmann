from functools import partial
from typing import (Callable,
                    cast)

from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .event import Event


class EventsQueueKey:
    __slots__ = ('event',)

    def __init__(self, event: Event) -> None:
        self.event = event

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'EventsQueueKey') -> bool:
        return (self.event == other.event
                if isinstance(other, EventsQueueKey)
                else NotImplemented)

    def __lt__(self, other: 'EventsQueueKey') -> bool:
        """
        Checks if the event should be processed before the other.
        """
        if not isinstance(other, EventsQueueKey):
            return NotImplemented
        event, other_event = self.event, other.event
        start_x, start_y = event.start
        other_start_x, other_start_y = other_event.start
        if start_x != other_start_x:
            # different x-coordinate,
            # the event with lower x-coordinate is processed first
            return start_x < other_start_x
        elif start_y != other_start_y:
            # different starts, but same x-coordinate,
            # the event with lower y-coordinate is processed first
            return start_y < other_start_y
        elif event.end == other_event.end:
            # same segments
            return (event.segments_ids < other_event.segments_ids
                    if event.is_intersection is other_event.is_intersection
                    else event.is_intersection)
        elif event.is_left_endpoint is not other_event.is_left_endpoint:
            # same start, but one is a left endpoint
            # and the other is a right endpoint,
            # the right endpoint is processed first
            return not event.is_left_endpoint
        else:
            # same start, different end,
            # both events are left endpoints
            # or both are right endpoints
            return event.end < other_event.end


EventsQueue = cast(Callable[..., PriorityQueue[Event]],
                   partial(PriorityQueue[Event],
                           key=EventsQueueKey))
