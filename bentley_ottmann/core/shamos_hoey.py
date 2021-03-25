from typing import (Optional,
                    Sequence)

from ground.base import Context
from ground.hints import (Point,
                          Segment)

from .events_queue import EventsQueue
from .sweep_line import SweepLine


def sweep(segments: Sequence[Segment],
          *,
          context: Context) -> bool:
    events_queue = EventsQueue.from_segments(segments,
                                             context=context)
    sweep_line = SweepLine(context)
    prev_start = None  # type: Optional[Point]
    while events_queue:
        event = events_queue.pop()
        start = event.start
        if (len(event.segments_ids) > 1
                or start == prev_start
                or events_queue and events_queue.peek().start == start):
            return True
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
        prev_start = start
    return False
