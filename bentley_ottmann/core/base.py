from typing import (Iterable,
                    List,
                    Optional,
                    Sequence)

from ground.base import Context
from ground.hints import (Point,
                          Segment)

from .event import Event
from .events_queue import EventsQueue
from .sweep_line import SweepLine
from .utils import to_pairs_combinations


def sweep(segments: Sequence[Segment],
          *,
          context: Context) -> Iterable[Event]:
    events_queue = EventsQueue.from_segments(segments,
                                             context=context)
    sweep_line = SweepLine(context)
    start = (events_queue.peek().start
             if events_queue
             else None)  # type: Optional[Point]
    same_start_events = []  # type: List[Event]
    while events_queue:
        event = events_queue.pop()
        if event.start == start:
            same_start_events.append(event)
        else:
            complete_touching_same_start_events(same_start_events)
            yield from to_processed_events(same_start_events)
            same_start_events, start = [event], event.start
        if event.is_left_endpoint:
            equal_segment_event = sweep_line.find_equal(event)
            if equal_segment_event is None:
                assert event not in sweep_line
                sweep_line.add(event)
                below_event = sweep_line.below(event)
                if below_event is not None:
                    events_queue.detect_intersection(below_event, event,
                                                     sweep_line)
                above_event = sweep_line.above(event)
                if above_event is not None:
                    events_queue.detect_intersection(event, above_event,
                                                     sweep_line)
            else:
                # found equal segments' fragments
                equal_segment_event.merge_with(event)
        else:
            left_event = event.opposite
            equal_segment_event = sweep_line.find_equal(left_event)
            if equal_segment_event is not None:
                above_event, below_event = (
                    sweep_line.above(equal_segment_event),
                    sweep_line.below(equal_segment_event))
                sweep_line.remove(equal_segment_event)
                if below_event is not None and above_event is not None:
                    events_queue.detect_intersection(below_event, above_event,
                                                     sweep_line)
                if left_event is not equal_segment_event:
                    left_event.merge_with(equal_segment_event)
    complete_touching_same_start_events(same_start_events)
    yield from to_processed_events(same_start_events)


def complete_touching_same_start_events(events: Sequence[Event]) -> None:
    for first, second in to_pairs_combinations(events):
        non_overlapping_parts = first.ids.isdisjoint(second.ids)
        if non_overlapping_parts:
            first.register_tangent(second)
            second.register_tangent(first)


def to_processed_events(events: Iterable[Event]) -> Iterable[Event]:
    return [candidate.opposite
            for candidate in events
            if not candidate.is_left_endpoint]
