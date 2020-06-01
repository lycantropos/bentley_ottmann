from typing import (Iterable,
                    Optional,
                    Sequence,
                    Tuple)

from bentley_ottmann.hints import (Point,
                                   Segment)
from .event import Event
from .events_queue import (EventsQueue,
                           EventsQueueKey)
from .linear import (SegmentsRelationship,
                     segments_intersection,
                     segments_relationship,
                     sort_endpoints,
                     to_rational_segment)
from .sweep_line import SweepLine
from .utils import (merge_ids,
                    to_pairs_combinations)


def sweep(segments: Sequence[Segment],
          accurate: bool,
          validate: bool) -> Iterable[Tuple[Event, Event]]:
    if validate:
        for segment in segments:
            start, end = segment
            if start == end:
                raise ValueError('Degenerate segment found: {segment}.'
                                 .format(segment=segment))
    if accurate:
        segments = [to_rational_segment(segment) for segment in segments]
    events_queue = to_events_queue(segments)
    sweep_line = SweepLine()
    while events_queue:
        event = events_queue.pop()
        point, same_start_events = event.start, [event]
        while events_queue and events_queue.peek().start == point:
            same_start_events.append(events_queue.pop())
        for event, other_event in to_pairs_combinations(same_start_events):
            yield event, other_event
        sweep_line.move_to(point)
        for event in same_start_events:
            if len(event.segments_ids) > 1:
                yield event, event

            if event.is_left_endpoint:
                sweep_line.add(event)
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                if below_event is not None:
                    yield from detect_intersection(below_event, event,
                                                   events_queue=events_queue)
                if above_event is not None:
                    yield from detect_intersection(event, above_event,
                                                   events_queue=events_queue)
            else:
                event = event.complement
                if event in sweep_line:
                    above_event, below_event = (sweep_line.above(event),
                                                sweep_line.below(event))
                    sweep_line.remove(event)
                    if below_event is not None and above_event is not None:
                        yield from detect_intersection(
                                below_event, above_event,
                                events_queue=events_queue)


def to_events_queue(segments: Sequence[Segment]) -> EventsQueue:
    segments_with_ids = sorted((sort_endpoints(segment), segment_id)
                               for segment_id, segment in enumerate(segments))
    events_queue = EventsQueue()
    index = 0
    while index < len(segments_with_ids):
        segment, segment_id = segments_with_ids[index]
        index += 1
        same_segments_ids = [segment_id]
        while (index < len(segments_with_ids)
               and segments_with_ids[index][0] == segment):
            same_segments_ids.append(segments_with_ids[index][1])
            index += 1
        start, end = segment
        relationship = (SegmentsRelationship.NONE
                        if len(same_segments_ids) == 1
                        else SegmentsRelationship.OVERLAP)
        start_event = Event(is_left_endpoint=True,
                            relationship=relationship,
                            start=start,
                            complement=None,
                            segments_ids=same_segments_ids)
        end_event = Event(is_left_endpoint=False,
                          relationship=relationship,
                          start=end,
                          complement=start_event,
                          segments_ids=same_segments_ids)
        start_event.complement = end_event
        events_queue.push(start_event)
        events_queue.push(end_event)
    return events_queue


def detect_intersection(first_event: Event, second_event: Event,
                        events_queue: EventsQueue
                        ) -> Iterable[Tuple[Event, Event]]:
    first_segment, second_segment = first_event.segment, second_event.segment
    relationship = segments_relationship(first_segment, second_segment)

    if relationship is SegmentsRelationship.NONE:
        return
    elif relationship is SegmentsRelationship.OVERLAP:
        # segments overlap
        yield first_event, second_event

        sorted_events = []
        starts_equal = first_event.start == second_event.start
        if starts_equal:
            sorted_events.append(None)
        elif EventsQueueKey(first_event) > EventsQueueKey(second_event):
            sorted_events.append(second_event)
            sorted_events.append(first_event)
        else:
            sorted_events.append(first_event)
            sorted_events.append(second_event)

        ends_equal = first_event.end == second_event.end
        if ends_equal:
            sorted_events.append(None)
        elif (EventsQueueKey(first_event.complement)
              > EventsQueueKey(second_event.complement)):
            sorted_events.append(second_event.complement)
            sorted_events.append(first_event.complement)
        else:
            sorted_events.append(first_event.complement)
            sorted_events.append(second_event.complement)

        segments_ids = merge_ids(first_event.segments_ids,
                                 second_event.segments_ids)
        if starts_equal and ends_equal:
            # both line segments are equal
            first_event.relationship = second_event.relationship = relationship
            first_event.segments_ids = second_event.segments_ids = segments_ids
        elif starts_equal or ends_equal:
            # line segments share endpoint
            divide_segment(sorted_events[2].complement
                           # line segments share the left endpoint
                           if starts_equal
                           # line segments share the right endpoint
                           else sorted_events[0], sorted_events[1].start,
                           relationship, events_queue, segments_ids)
        else:
            divide_segment(sorted_events[0], sorted_events[1].start,
                           relationship, events_queue, segments_ids)
            divide_segment(sorted_events[0]
                           # one line segment includes the other one
                           if sorted_events[0] is sorted_events[3].complement
                           # no line segment includes totally the other one
                           else sorted_events[1], sorted_events[2].start,
                           relationship, events_queue, segments_ids)
    else:
        # segments intersect
        yield first_event, second_event

        point = segments_intersection(first_segment, second_segment)
        if point != first_event.start and point != first_event.end:
            divide_segment(first_event, point, relationship, events_queue)
        if point != second_event.start and point != second_event.end:
            divide_segment(second_event, point, relationship, events_queue)


def divide_segment(event: Event,
                   break_point: Point,
                   relationship: SegmentsRelationship,
                   events_queue: EventsQueue,
                   segments_ids: Optional[Sequence[int]] = None) -> None:
    if segments_ids is None:
        segments_ids = event.segments_ids
    else:
        event.segments_ids = segments_ids
    left_event = Event(is_left_endpoint=True,
                       relationship=relationship,
                       start=break_point,
                       complement=event.complement,
                       segments_ids=segments_ids)
    right_event = Event(is_left_endpoint=False,
                        relationship=relationship,
                        start=break_point,
                        complement=event,
                        segments_ids=segments_ids)
    event.relationship = relationship
    event.complement.complement, event.complement = left_event, right_event
    events_queue.push(left_event)
    events_queue.push(right_event)
