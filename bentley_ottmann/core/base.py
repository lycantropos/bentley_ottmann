from typing import (Iterable,
                    List,
                    Sequence,
                    Tuple)

from ground.base import (Context,
                         Relation)
from ground.hints import (Point,
                          Segment)

from .event import Event
from .events_queue import EventsQueue
from .sweep_line import SweepLine
from .utils import to_pairs_combinations


def sweep(segments: Sequence[Segment],
          *,
          context: Context) -> Iterable[Tuple[Event, Event]]:
    events_queue = to_events_queue(segments, context=context)
    sweep_line = SweepLine(context)
    prev_start = None
    prev_same_start_events = []  # type: List[Event]
    while events_queue:
        event = events_queue.pop()
        start = event.start
        same_start_events = (prev_same_start_events + [event]
                             if start == prev_start
                             else [event])
        while events_queue and events_queue.peek().start == start:
            same_start_events.append(events_queue.pop())
        for event, other_event in to_pairs_combinations(same_start_events):
            yield event, other_event
        for event in same_start_events:
            if event.is_left_endpoint:
                sweep_line.add(event)
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                if below_event is not None:
                    events_queue.detect_intersection(below_event, event)
                if above_event is not None:
                    events_queue.detect_intersection(event, above_event)
            else:
                event = event.complement
                if event in sweep_line:
                    above_event, below_event = (sweep_line.above(event),
                                                sweep_line.below(event))
                    sweep_line.remove(event)
                    if below_event is not None and above_event is not None:
                        events_queue.detect_intersection(below_event,
                                                         above_event)
                if len(event.segments_ids) > 1:
                    yield event, event
        prev_start, prev_same_start_events = start, same_start_events


def to_events_queue(segments: Sequence[Segment],
                    *,
                    context: Context) -> EventsQueue:
    endpoints_with_ids = sorted((sort_endpoints(segment), segment_id)
                                for segment_id, segment in enumerate(segments))
    result = EventsQueue(context)
    index = 0
    while index < len(endpoints_with_ids):
        endpoints, segment_id = endpoints_with_ids[index]
        index += 1
        same_segments_ids = [segment_id]
        while (index < len(endpoints_with_ids)
               and endpoints_with_ids[index][0] == endpoints):
            same_segments_ids.append(endpoints_with_ids[index][1])
            index += 1
        start, end = endpoints
        relationship = (Relation.DISJOINT
                        if len(same_segments_ids) == 1
                        else Relation.EQUAL)
        start_event = Event(is_left_endpoint=True,
                            relation=relationship,
                            start=start,
                            complement=None,
                            segments_ids=same_segments_ids)
        end_event = Event(is_left_endpoint=False,
                          relation=relationship,
                          start=end,
                          complement=start_event,
                          segments_ids=same_segments_ids)
        start_event.complement = end_event
        result.push(start_event)
        result.push(end_event)
    return result


def sort_endpoints(segment: Segment) -> Tuple[Point, Point]:
    start, end = segment.start, segment.end
    return (start, end) if start < end else (end, start)
