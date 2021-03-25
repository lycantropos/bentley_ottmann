from itertools import combinations
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


def sweep(segments: Sequence[Segment],
          *,
          context: Context) -> Iterable[Event]:
    events_queue = EventsQueue.from_segments(segments,
                                             context=context)
    segments_relater = context.segments_relation
    sweep_line = SweepLine(context)
    prev_start = None  # type: Optional[Point]
    prev_same_start_events = []  # type: List[Event]
    while events_queue:
        event = events_queue.pop()
        start = event.start
        same_start_events = (prev_same_start_events + [event]
                             if start == prev_start
                             else [event])
        while events_queue and events_queue.peek().start == start:
            same_start_events.append(events_queue.pop())
        for event, other_event in combinations(same_start_events,
                                               r=2):
            if event.segments_ids is not other_event.segments_ids:
                relation = segments_relater(
                        event.original_start, event.original_end,
                        other_event.original_start, other_event.original_end)
                (event.relations.setdefault(relation, [])
                 .append(other_event.segments_ids))
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
                yield event
        prev_start, prev_same_start_events = start, same_start_events
