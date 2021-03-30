from typing import (Iterable,
                    Sequence,
                    Tuple)

from ground.base import (Context,
                         Relation)
from ground.hints import (Point,
                          Segment)

from .event import Event
from .events_queue import EventsQueue
from .sweep_line import SweepLine


def sweep(segments: Sequence[Segment],
          *,
          context: Context) -> Iterable[Event]:
    events_queue = to_events_queue(segments,
                                   context=context)
    sweep_line = SweepLine(context)
    while events_queue:
        event = events_queue.pop()
        if event.is_left_endpoint:
            equal_segment_event = sweep_line.find_equivalent(event)
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
            event = event.opposite
            equal_segment_event = sweep_line.find_equivalent(event)
            if equal_segment_event is not None:
                above_event, below_event = (
                    sweep_line.above(equal_segment_event),
                    sweep_line.below(equal_segment_event))
                sweep_line.remove(equal_segment_event)
                if below_event is not None and above_event is not None:
                    assert not events_queue.detect_intersection(below_event,
                                                                above_event,
                                                                sweep_line)
                if event is not equal_segment_event:
                    event.merge_with(equal_segment_event)
            yield event
        for e in sweep_line._set:
            above = sweep_line.above(e)
            assert above is None or e.start != above.start or e.end != above.end
            below = sweep_line.below(e)
            assert below is None or e.start != below.start or e.end != below.end


def to_events_queue(segments: Sequence[Segment],
                    *,
                    context: Context) -> EventsQueue:
    result = EventsQueue(context)
    for index, segment in enumerate(segments):
        start, end = sort_endpoints(segment)
        relation = Relation.DISJOINT
        points_ids = {start: {end: {index}}}
        start_event = Event(start, None, True, relation, points_ids)
        end_event = Event(end, start_event, False, relation, points_ids)
        start_event.opposite = end_event
        result.push(start_event)
        result.push(end_event)
    return result


def sort_endpoints(segment: Segment) -> Tuple[Point, Point]:
    start, end = segment.start, segment.end
    return (start, end) if start < end else (end, start)
