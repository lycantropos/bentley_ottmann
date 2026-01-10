from __future__ import annotations

from typing import Generic, TYPE_CHECKING

from ground.hints import Point
from typing_extensions import Self

from .event import Event, is_event_left
from .hints import ScalarT

if TYPE_CHECKING:
    from .hints import Map


class EventsQueueKey(Generic[ScalarT]):
    endpoints: Map[Event, Point[ScalarT]]
    opposites: Map[Event, Event]
    event: Event

    __slots__ = 'endpoints', 'event', 'opposites'

    def __new__(
        cls,
        endpoints: Map[Event, Point[ScalarT]],
        opposites: Map[Event, Event],
        event: Event,
        /,
    ) -> Self:
        self = super().__new__(cls)
        self.endpoints, self.event, self.opposites = (
            endpoints,
            event,
            opposites,
        )
        return self

    def __lt__(self, other: Self) -> bool:
        """
        Checks if the event should be processed before the other.
        """
        event, other_event = self.event, other.event
        event_start, other_event_start = (
            self.endpoints[event],
            self.endpoints[other_event],
        )
        start_x, start_y = event_start.x, event_start.y
        other_start_x, other_start_y = other_event_start.x, other_event_start.y
        if start_x != other_start_x:
            # different x-coordinate,
            # the event with lower x-coordinate is processed first
            return start_x < other_start_x
        if start_y != other_start_y:
            # different starts, but same x-coordinate,
            # the event with lower y-coordinate is processed first
            return start_y < other_start_y
        if is_event_left(event) is not is_event_left(other_event):
            # same start, but one is a left endpoint
            # and the other is a right endpoint,
            # the right endpoint is processed first
            return not is_event_left(event)
        # same start,
        # both events are left endpoints or both are right endpoints
        return (
            self.endpoints[self.opposites[event]]
            < self.endpoints[self.opposites[other_event]]
        )
