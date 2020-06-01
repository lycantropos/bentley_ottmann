from typing import (Iterable,
                    List,
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
        sweep_line.move_to(start)
        for event in same_start_events:
            if event.is_left_endpoint:
                sweep_line.add(event)
                above_event, below_event = (sweep_line.above(event),
                                            sweep_line.below(event))
                if below_event is not None:
                    detect_intersection(below_event, event,
                                        events_queue=events_queue)
                if above_event is not None:
                    detect_intersection(event, above_event,
                                        events_queue=events_queue)
            else:
                event = event.complement
                if event in sweep_line:
                    above_event, below_event = (sweep_line.above(event),
                                                sweep_line.below(event))
                    sweep_line.remove(event)
                    if below_event is not None and above_event is not None:
                        detect_intersection(below_event, above_event,
                                            events_queue=events_queue)
                if len(event.segments_ids) > 1:
                    yield event, event
        prev_start, prev_same_start_events = start, same_start_events


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


def detect_intersection(below_event: Event, event: Event,
                        events_queue: EventsQueue) -> None:
    below_segment, segment = below_event.segment, event.segment
    relationship = segments_relationship(below_segment, segment)

    if relationship is SegmentsRelationship.OVERLAP:
        # segments overlap
        starts_equal = event.start == below_event.start
        if starts_equal:
            start_min = start_max = None
        elif EventsQueueKey(event) < EventsQueueKey(below_event):
            start_min, start_max = event, below_event
        else:
            start_min, start_max = below_event, event

        ends_equal = event.end == below_event.end
        if ends_equal:
            end_min = end_max = None
        elif (EventsQueueKey(event.complement)
              < EventsQueueKey(below_event.complement)):
            end_min, end_max = event.complement, below_event.complement
        else:
            end_min, end_max = below_event.complement, event.complement

        segments_ids = merge_ids(below_event.segments_ids,
                                 event.segments_ids)
        if starts_equal:
            if ends_equal:
                # segments are equal
                below_event.segments_ids = event.segments_ids = segments_ids
                event.set_both_relationships(relationship)
                below_event.set_both_relationships(relationship)
            else:
                # segments share the left endpoint
                end_min.set_both_relationships(relationship)
                end_max.complement.relationship = relationship
                divide_segment(end_max.complement, end_min.start, events_queue,
                               segments_ids)
        elif ends_equal:
            # segments share the right endpoint
            start_max.set_both_relationships(relationship)
            start_min.complement.relationship = relationship
            divide_segment(start_min, start_max.start, events_queue,
                           segments_ids)
        elif start_min is end_max.complement:
            # one line segment includes the other one
            start_max.set_both_relationships(relationship)
            start_min_original_relationship = start_min.relationship
            start_min.relationship = relationship
            divide_segment(start_min, end_min.start, events_queue,
                           segments_ids)
            start_min.relationship = start_min_original_relationship
            start_min.complement.relationship = relationship
            divide_segment(start_min, start_max.start, events_queue,
                           segments_ids)
        else:
            # no line segment includes the other one
            start_max.relationship = relationship
            divide_segment(start_max, end_min.start, events_queue,
                           segments_ids)
            start_min.complement.relationship = relationship
            divide_segment(start_min, start_max.start, events_queue,
                           segments_ids)
    elif relationship is not SegmentsRelationship.NONE:
        # segments touch or cross
        point = segments_intersection(below_segment, segment)
        if point != below_event.start and point != below_event.end:
            divide_segment(below_event, point, events_queue)
        if point != event.start and point != event.end:
            divide_segment(event, point, events_queue)

        event.set_both_relationships(max(event.relationship,
                                         relationship))
        below_event.set_both_relationships(max(below_event.relationship,
                                               relationship))


def divide_segment(event: Event,
                   break_point: Point,
                   events_queue: EventsQueue,
                   segments_ids: Optional[Sequence[int]] = None) -> None:
    if segments_ids is None:
        segments_ids = event.segments_ids
    else:
        event.segments_ids = segments_ids
    left_event = Event(is_left_endpoint=True,
                       relationship=event.complement.relationship,
                       start=break_point,
                       complement=event.complement,
                       segments_ids=segments_ids)
    right_event = Event(is_left_endpoint=False,
                        relationship=event.relationship,
                        start=break_point,
                        complement=event,
                        segments_ids=segments_ids)
    event.complement.complement, event.complement = left_event, right_event
    events_queue.push(left_event)
    events_queue.push(right_event)
