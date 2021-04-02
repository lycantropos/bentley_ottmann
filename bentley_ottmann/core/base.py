from typing import (Iterable,
                    List,
                    Optional,
                    Sequence)

from ground.base import (Context,
                         Orientation,
                         Relation)
from ground.hints import (Point,
                          Segment)

from .event import (Event,
                    LeftEvent)
from .events_queue import EventsQueue
from .sweep_line import SweepLine
from .utils import (classify_overlap,
                    to_pairs_combinations)


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
            complete_events_relations(same_start_events)
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
    complete_events_relations(same_start_events)
    yield from to_processed_events(same_start_events)


def complete_events_relations(same_start_events: Sequence[Event]) -> None:
    for first, second in to_pairs_combinations(same_start_events):
        first_left, second_left = (first if first.is_left else first.left,
                                   second if second.is_left else second.left)
        first_ids, second_ids = (first_left.segments_ids,
                                 second_left.segments_ids)
        segments_touch = (len(first_ids - second_ids)
                          * len(second_ids - first_ids)) >= 1
        if segments_touch:
            intersection_point = first.start
            relation = (Relation.TOUCH
                        if (intersection_point == first.original_start
                            or intersection_point == second.original_start)
                        else Relation.CROSS)
            first.register_tangent(second)
            second.register_tangent(first)
        else:
            relation = classify_overlap(first_left.original_start,
                                        first_left.original_end,
                                        second_left.original_start,
                                        second_left.original_end)
        first_left.register_relation(relation)
        second_left.register_relation(relation.complement)


def to_processed_events(events: Iterable[Event]) -> List[LeftEvent]:
    return [candidate.left for candidate in events if not candidate.is_left]
