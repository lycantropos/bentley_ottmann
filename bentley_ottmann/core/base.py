from typing import (Iterable,
                    List,
                    Optional,
                    Sequence)

from ground.base import (Context,
                         Relation)
from ground.hints import (Point,
                          Segment)

from .event import (Event,
                    LeftEvent)
from .events_queue import EventsQueue
from .sweep_line import SweepLine
from .utils import to_pairs_combinations


def sweep(segments: Sequence[Segment],
          *,
          context: Context) -> Iterable[LeftEvent]:
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
        if event.is_left:
            equal_segment_event = sweep_line.find_equal(event)
            if equal_segment_event is None:
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
            event = event.left
            equal_segment_event = sweep_line.find_equal(event)
            if equal_segment_event is not None:
                above_event, below_event = (
                    sweep_line.above(equal_segment_event),
                    sweep_line.below(equal_segment_event))
                sweep_line.remove(equal_segment_event)
                if below_event is not None and above_event is not None:
                    events_queue.detect_intersection(below_event, above_event,
                                                     sweep_line)
                if event is not equal_segment_event:
                    event.merge_with(equal_segment_event)
    complete_touching_same_start_events(same_start_events)
    yield from to_processed_events(same_start_events)


def complete_touching_same_start_events(events: Sequence[Event]) -> None:
    for first, second in to_pairs_combinations(events):
        first_left, second_left = (first if first.is_left else first.left,
                                   second if second.is_left else second.left)
        non_overlapping_parts = (first_left.segments_ids
                                 .isdisjoint(second_left.segments_ids))
        if non_overlapping_parts:
            endpoint = first.start
            full_relation = (Relation.TOUCH
                             if (endpoint == first.original_start
                                 or endpoint == first.original_end
                                 or endpoint == second.original_start
                                 or endpoint == second.original_end)
                             else Relation.CROSS)
            first_left.add_relation(full_relation)
            second_left.add_relation(full_relation.complement)
            first.register_tangent(second)
            second.register_tangent(first)


def to_processed_events(events: Iterable[Event]) -> List[LeftEvent]:
    return [candidate.left for candidate in events if not candidate.is_left]
