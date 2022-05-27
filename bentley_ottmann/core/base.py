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
from .utils import classify_overlap


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
            yield from complete_events_relations(same_start_events)
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
                    sweep_line.below(equal_segment_event)
                )
                sweep_line.remove(equal_segment_event)
                if below_event is not None and above_event is not None:
                    events_queue.detect_intersection(below_event, above_event,
                                                     sweep_line)
                if event is not equal_segment_event:
                    equal_segment_event.merge_with(event)
    yield from complete_events_relations(same_start_events)


def complete_events_relations(same_start_events: Sequence[Event]
                              ) -> Iterable[Event]:
    for offset, first in enumerate(same_start_events,
                                   start=1):
        first_left = first if first.is_left else first.left
        first_ids = first_left.segments_ids
        for second_index in range(offset, len(same_start_events)):
            second = same_start_events[second_index]
            second_left = second if second.is_left else second.left
            second_ids = second_left.segments_ids
            first_extra_ids_count, second_extra_ids_count = (
                len(first_ids - second_ids), len(second_ids - first_ids)
            )
            if first_extra_ids_count and second_extra_ids_count:
                relation = (Relation.TOUCH
                            if (first.start == first.original_start
                                or second.start == second.original_start)
                            else Relation.CROSS)
                first.register_tangent(second)
                second.register_tangent(first)
                first_left.register_relation(relation)
                second_left.register_relation(relation.complement)
            elif first_extra_ids_count or second_extra_ids_count:
                relation = classify_overlap(first_left.original_start,
                                            first_left.original_end,
                                            second_left.original_start,
                                            second_left.original_end)
                first_left.register_relation(relation)
                second_left.register_relation(relation.complement)
        if not first.is_left:
            yield first_left
