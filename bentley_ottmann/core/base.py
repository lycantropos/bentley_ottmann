from typing import Iterable, List, Optional, Sequence
from ground.base import Context, Relation
from ground.hints import Point, Segment
from .event import Event, LeftEvent
from .events_queue import EventsQueue
from .sweep_line import SweepLine
from .utils import classify_overlap

"""
Implementation of the Bentley-Ottmann algorithm for detecting intersections in a set of line segments.

The Bentley-Ottmann algorithm is an efficient, sweep line based method for finding all intersections 
in a set of line segments. This implementation consists of multiple functions that collectively process 
the segments, identify intersections, and handle the events resulting from these intersections.

Functions:
    sweep: Main function that initiates the sweep line algorithm over a sequence of segments.
    process_left_event: Processes 'left' events, which signify the beginning of a segment in the sweep line.
    process_right_event: Processes 'right' events, marking the end of a segment in the sweep line.
    check_for_intersections: Checks and processes potential intersections between segments.
    handle_segment_removal: Handles the removal of a segment from the sweep line, adjusting the sweep line state.
    complete_events_relations: Completes the relationships between events that have the same start point.

The algorithm uses several classes including EventsQueue for event management and SweepLine for maintaining 
the state of the sweep line. Each segment is represented by left and right events, which are processed to 
detect and manage intersections. The algorithm efficiently handles segment intersections, overlaps, and 
endpoint coincidences.

Yields:
    Iterable[LeftEvent]: An iterable of LeftEvent objects representing processed events on the sweep line, 
    particularly those at the left endpoints of the segments.

Example:
    Given a set of line segments, the algorithm can be invoked as follows:
    >>> segments = [Segment(Point(0, 0), Point(1, 1)), Segment(Point(1, 0), Point(0, 1))]
    >>> for event in sweep(segments, context=YourContextImplementation):
    ...     # Process or inspect the event
    ...     pass
"""

def sweep(segments: Sequence[Segment], *, context: Context) -> Iterable[LeftEvent]:
    """
    Processes a sequence of segments using a sweep line algorithm to identify geometric events.

    Args:
        segments (Sequence[Segment]): A sequence of segments to be processed.
        context (Context): Geometric context in which the operation is performed.

    Yields:
        Iterable[LeftEvent]: An iterable of LeftEvent objects representing events on the left endpoints of the segments.
    """
    # Initialize the events queue and the sweep line
    events_queue = EventsQueue.from_segments(segments, context=context)
    sweep_line = SweepLine(context)
    
    # Track the starting point and events with the same starting point
    start: Optional[Point] = events_queue.peek().start if events_queue else None
    same_start_events: List[Event] = []
    
    while events_queue:
        event = events_queue.pop()
        if event.start == start:
            same_start_events.append(event)
        else:
            yield from complete_events_relations(same_start_events)
            same_start_events, start = [event], event.start

        if event.is_left:
            # Handle left events (start of a segment)
            process_left_event(event, sweep_line, events_queue)
        else:
            # Handle right events (end of a segment)
            process_right_event(event, sweep_line, events_queue)

    yield from complete_events_relations(same_start_events)

def process_left_event(event: Event, sweep_line: SweepLine, events_queue: EventsQueue):
    """
    Process a left event in the sweep line algorithm.

    Args:
        event (Event): The current event being processed.
        sweep_line (SweepLine): The sweep line object.
        events_queue (EventsQueue): The queue of events.
    """
    assert isinstance(event, LeftEvent), event
    equal_segment_event = sweep_line.find_equal(event)
    if equal_segment_event is None:
        sweep_line.add(event)
        check_for_intersections(event, sweep_line, events_queue)
    else:
        equal_segment_event.merge_with(event)

def process_right_event(event: Event, sweep_line: SweepLine, events_queue: EventsQueue):
    """
    Process a right event in the sweep line algorithm.

    Args:
        event (Event): The current event being processed.
        sweep_line (SweepLine): The sweep line object.
        events_queue (EventsQueue): The queue of events.
    """
    event = event.left
    equal_segment_event = sweep_line.find_equal(event)
    if equal_segment_event is not None:
        handle_segment_removal(equal_segment_event, sweep_line, events_queue)
        if event is not equal_segment_event:
            equal_segment_event.merge_with(event)

def check_for_intersections(event: Event, sweep_line: SweepLine, events_queue: EventsQueue):
    """
    Check and handle intersections for a given event.

    Args:
        event (Event): The event to check intersections for.
        sweep_line (SweepLine): The sweep line object.
        events_queue (EventsQueue): The queue of events.
    """
    below_event = sweep_line.below(event)
    if below_event is not None:
        events_queue.detect_intersection(below_event, event, sweep_line)
    above_event = sweep_line.above(event)
    if above_event is not None:
        events_queue.detect_intersection(event, above_event, sweep_line)

def handle_segment_removal(event: Event, sweep_line: SweepLine, events_queue: EventsQueue):
    """
    Handle the removal of a segment from the sweep line.

    Args:
        event (Event): The event corresponding to the segment being removed.
        sweep_line (SweepLine): The sweep line object.
        events_queue (EventsQueue): The queue of events.
    """
    above_event, below_event = sweep_line.above(event), sweep_line.below(event)
    sweep_line.remove(event)
    if below_event is not None and above_event is not None:
        events_queue.detect_intersection(below_event, above_event, sweep_line)

def complete_events_relations(same_start_events: Sequence[Event]) -> Iterable[LeftEvent]:
    """
    Process and complete the relationships between events that have the same start point.

    Args:
        same_start_events (Sequence[Event]): Events starting at the same point.

    Yields:
        Iterable[LeftEvent]: Events with completed relationships.
    """
    for offset, first in enumerate(same_start_events, start=1):
        first_left = first if first.is_left else first.left
        assert isinstance
