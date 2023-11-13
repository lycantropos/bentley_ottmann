from __future__ import annotations

from typing import (Any,
                    Sequence)

from ground.base import (Context,
                         Relation)
from ground.hints import Segment
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .event import (Event,
                    LeftEvent)
from .sweep_line import SweepLine

"""
This script is an integral part of the Bentley-Ottmann algorithm implementation,
focusing on the management and processing of events in a sweep-line algorithm
for detecting intersections in a set of line segments.

The primary components include the `EventsQueue` and `EventsQueueKey` classes,
which play crucial roles in organizing and processing the events efficiently.

1. `EventsQueue`:
   - Manages a priority queue of events (`LeftEvent` and their corresponding `RightEvent`),
     ensuring that events are processed in the correct order during the sweep-line algorithm.
   - The `from_segments` class method initializes the queue with events derived from the given segments.
   - The `detect_intersection` method handles the detection and processing of intersections,
     including dividing segments at intersection points and merging overlapping segments.
   - The `push`, `pop`, and `peek` methods manage the addition, removal,
     and previewing of events in the queue, respectively, with checks for degenerate segments.

2. `EventsQueueKey`:
   - A utility class used for comparing events in the priority queue.
   - Defines a custom less-than (`__lt__`) method to establish the processing order of events
     based on their geometric properties (e.g., x and y coordinates, and whether they are left or right events).

Overall, this script encapsulates the core logic for handling events in the Bentley-Ottmann algorithm,
enabling efficient processing and detection of intersections in geometric computations.
Its design and implementation are tailored to manage events systematically,
ensuring the correct sequencing and handling of geometric intersections and overlaps.
"""


class EventsQueue:
    """
    Represents a priority queue of events for the Bentley-Ottmann algorithm.

    This class manages a sequence of geometric events, specifically designed to handle
    intersections and overlaps in a set of line segments. It uses a priority queue
    to ensure that events are processed in the correct order.
    """

    @classmethod
    def from_segments(cls, segments: Sequence[Segment], *, context: Context) -> 'EventsQueue':
        """
        Creates an event queue from a sequence of segments.

        Args:
            segments: A sequence of segments to process.
            context: Geometric context providing necessary operations for segment comparison.

        Returns:
            An instance of EventsQueue filled with events derived from the given segments.
        """
        result = cls(context)
        for index, segment in enumerate(segments):
            # Create a LeftEvent from each segment and add it along with its corresponding RightEvent to the queue.
            event = LeftEvent.from_segment(segment, index)
            result.push(event)
            result.push(event.right)
        return result

    __slots__ = 'context', '_queue'

    def __init__(self, context: Context) -> None:
        """
        Initializes the EventsQueue.

        Args:
            context: Geometric context providing operations for segment comparison.
        """
        self.context = context
        self._queue: PriorityQueue[EventsQueueKey, Event] = PriorityQueue(key=EventsQueueKey)

    __repr__ = generate_repr(__init__)

    def __bool__(self) -> bool:
        """Checks if the queue is non-empty."""
        return bool(self._queue)

    def detect_intersection(self, below_event: LeftEvent, event: LeftEvent, sweep_line: SweepLine) -> None:
        """
        Detects and processes intersections between two events.

        This method determines the relationship between two events and handles their intersection
        or overlap appropriately, altering the events and the sweep line as necessary.

        Args:
            below_event: The event below the current event on the sweep line.
            event: The current event being processed.
            sweep_line: The sweep line data structure.
        """
        # Detects the relationship between two events (segments)
        relation = self.context.segments_relation(below_event, event)

        # If segments are disjoint (have no intersection), no further action needed
        if relation is Relation.DISJOINT:
            return
        elif relation is Relation.TOUCH or relation is Relation.CROSS:
            # If segments touch or cross each other at a point
            # Calculate the intersection point
            point = self.context.segments_intersection(below_event, event)

            # Ensure that the segment IDs of the events are disjoint to avoid processing the same segment twice
            assert event.segments_ids.isdisjoint(below_event.segments_ids)

            # If the intersection point is not at the start or end of the below_event
            if point != below_event.start and point != below_event.end:
                # Find the event directly below the below_event on the sweep line
                below_below_event = sweep_line.below(below_event)

                # Ensure there is no erroneous overlap with the below_below_event
                assert not (below_below_event is not None and 
                            below_below_event.start == below_event.start and 
                            below_below_event.end == point)

                # Divide the below_event at the intersection point, creating two new events
                # and push them into the queue
                (
                    point_to_below_event_start_event,
                    point_to_below_event_end_event
                ) = below_event.divide(point)
                self.push(point_to_below_event_start_event)
                self.push(point_to_below_event_end_event)

            # If the intersection point is not at the start or end of the event
            if point != event.start and point != event.end:
                # Find the event directly above the current event on the sweep line
                above_event = sweep_line.above(event)

                # Handle a special case where the above event needs to be removed from the sweep line
                if (above_event is not None and 
                    above_event.start == event.start and 
                    above_event.end == point):
                    sweep_line.remove(above_event)

                    # Divide the current event and merge it with the above event
                    # and push the new events into the queue
                    (
                        point_to_event_start_event, point_to_event_end_event
                    ) = event.divide(point)
                    self.push(point_to_event_start_event)
                    self.push(point_to_event_end_event)
                    event.merge_with(above_event)
                else:
                    # Divide the current event at the intersection point
                    # and push the new events into the queue
                    (
                        point_to_event_start_event, point_to_event_end_event
                    ) = event.divide(point)
                    self.push(point_to_event_start_event)
                    self.push(point_to_event_end_event)
        else:
            # Handle overlapping segments
            starts_equal = event.start == below_event.start

            # Determine the order of the events based on their start points
            min_start_event, max_start_event = (
                (event, below_event) if (starts_equal or EventsQueueKey(event) < EventsQueueKey(below_event))
                else (below_event, event)
            )
            ends_equal = event.end == below_event.end

            # Determine the order of the events based on their end points
            min_end_event, max_end_event = (
                (event.right, below_event.right) if (ends_equal or EventsQueueKey(event.right) < EventsQueueKey(below_event.right))
                else (below_event.right, event.right)
            )

            # Process different cases of overlapping, based on the relative positions of the start and end points
            if starts_equal:
                # If segments share the left endpoint
                assert not ends_equal
                sweep_line.remove(max_end_event.left)
                _, min_end_to_max_end_event = max_end_event.left.divide(min_end_event.start)
                self.push(min_end_to_max_end_event)
                event.merge_with(below_event)
            elif ends_equal:
                # If segments share the right endpoint
                (
                    max_start_to_min_start, max_start_to_end_event
                ) = min_start_event.divide(max_start_event.start)
                max_start_event.merge_with(max_start_to_end_event)
                self.push(max_start_to_min_start)
            elif min_start_event is max_end_event.left:
                # If one line segment includes the other one
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
                # If no line segment includes the other one
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
        """Returns the next event in the queue without removing it."""
        return self._queue.peek()

    def pop(self) -> Event:
        """Removes and returns the next event in the queue."""
        return self._queue.pop()

    def push(self, event: Event) -> None:
        """
        Adds an event to the queue.

        Args:
            event: The event to add to the queue.

        Raises:
            ValueError: If the event is a degenerate segment (start and end points are the same).
        """
        if event.start == event.end:
            raise ValueError('Degenerate segment found '
                             'with both endpoints being: {}.'
                             .format(event.start))
        self._queue.push(event)


class EventsQueueKey:
    """
    Key for comparing events in the EventsQueue.

    This class defines a custom ordering for events in the priority queue, ensuring that
    they are processed in the correct geometric order.
    """

    event: Event

    __slots__ = 'event',

    def __init__(self, event: Event) -> None:
        """
        Initializes an EventsQueueKey instance.

        Args:
            event: The event associated with this key.
        """
        self.event = event

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: EventsQueueKey) -> Any:
        """
        Determines the order of events for processing.

        This method compares two events based on their geometric properties to establish
        the correct processing order in the Bentley-Ottmann algorithm.

        Args:
            other: Another EventsQueueKey to compare with.

        Returns:
            True if this event should be processed before the other event, False otherwise.
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
