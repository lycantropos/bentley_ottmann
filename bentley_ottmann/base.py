from itertools import combinations
from reprlib import recursive_repr
from typing import (Iterable,
                    Optional,
                    Sequence,
                    Tuple)

from dendroid import red_black
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .angular import (Orientation,
                      to_orientation)
from .linear import (Segment,
                     find_intersections)
from .point import Point


class SweepEvent:
    __slots__ = ('is_left', 'point', 'complement', 'segment_id')

    def __init__(self, is_left: bool, point: Point,
                 complement: Optional['SweepEvent'],
                 segment_id: int) -> None:
        self.is_left = is_left
        self.point = point
        self.complement = complement
        self.segment_id = segment_id

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def segment(self) -> Segment:
        return Segment(self.point, self.complement.point)

    def is_above(self, point: Point) -> bool:
        return ((to_orientation(self.point, point, self.complement.point)
                 is Orientation.CLOCKWISE)
                if self.is_left
                else (to_orientation(self.complement.point, point, self.point)
                      is Orientation.CLOCKWISE))

    def is_below(self, point: Point) -> bool:
        return ((to_orientation(self.point, point, self.complement.point)
                 is Orientation.COUNTERCLOCKWISE)
                if self.is_left
                else (to_orientation(self.complement.point, point, self.point)
                      is Orientation.COUNTERCLOCKWISE))


SweepLine = red_black.Tree[SweepEvent]
EventsQueue = PriorityQueue[SweepEvent]


class EventsQueueKey:
    __slots__ = ('event',)

    def __init__(self, event: SweepEvent) -> None:
        self.event = event

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'EventsQueueKey') -> bool:
        return (self.event == other.event
                if isinstance(other, EventsQueueKey)
                else NotImplemented)

    def __lt__(self, other: 'EventsQueueKey') -> bool:
        if not isinstance(other, EventsQueueKey):
            return NotImplemented
        event, other_event = self.event, other.event
        event_point, other_event_point = event.point, other_event.point
        event_point_x, event_point_y = event_point
        other_event_point_x, other_event_point_y = other_event_point
        if event_point_x != other_event_point_x:
            # different x-coordinate,
            # the event with lower x-coordinate is processed first
            return event_point_x > other_event_point_x
        elif event_point_y != other_event_point_y:
            # different points, but same x-coordinate,
            # the event with lower y-coordinate is processed first
            return event_point_y > other_event_point_y
        elif event.is_left is not other_event.is_left:
            # same point, but one is a left endpoint
            # and the other a right endpoint,
            # the right endpoint is processed first
            return event.is_left
        # same point, both events are left endpoints
        # or both are right endpoints
        elif (to_orientation(event.point, other_event.complement.point,
                             event.complement.point)
              is not Orientation.COLLINEAR):  # not collinear
            # the event associate to the bottom segment is processed first
            return event.is_above(other_event.complement.point)
        else:
            return event.segment_id == other_event.segment_id


class SweepLineKey:
    __slots__ = ('event',)

    def __init__(self, event: SweepEvent) -> None:
        self.event = event

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'SweepLineKey') -> bool:
        return (self.event == other.event
                if isinstance(other, SweepLineKey)
                else NotImplemented)

    def __lt__(self, other: 'SweepLineKey') -> bool:
        if not isinstance(other, SweepLineKey):
            return NotImplemented
        if self is other:
            return False
        event, other_event = self.event, other.event
        event_point, other_event_point = event.point, other_event.point
        if not ((to_orientation(event_point, other_event_point,
                                event.complement.point)
                 is not Orientation.COLLINEAR)
                or (to_orientation(event_point, other_event.complement.point,
                                   event.complement.point)
                    is not Orientation.COLLINEAR)):
            # segments are collinear
            return EventsQueueKey(event) < EventsQueueKey(other_event)
        # segments are not collinear
        elif event_point == other_event_point:
            # same left endpoint, use the right endpoint to sort
            return event.is_below(other_event.complement.point)
        # different left endpoint, use the left endpoint to sort
        event_point_x, event_point_y = event_point
        other_event_point_x, other_event_point_y = other_event_point
        if event_point_x == other_event_point_x:
            return event_point_y < other_event_point_y
        elif EventsQueueKey(event) < EventsQueueKey(other_event):
            # has the line segment associated to `self` been inserted
            # into sweep line after the line segment associated to `other`?
            return other_event.is_above(event_point)
        else:
            # the line segment associated to `other_event` has been inserted
            # into sweep line after the line segment associated to `self`
            return event.is_below(other_event_point)


def _to_events_queue(segments: Sequence[Segment]) -> PriorityQueue[SweepEvent]:
    events_queue = PriorityQueue(key=EventsQueueKey,
                                 reverse=True)
    for segment_id, segment in enumerate(segments):
        segment_start, segment_end = segment
        source_event = SweepEvent(True, segment_start, None, segment_id)
        end_event = SweepEvent(True, segment_end, source_event, segment_id)
        source_event.complement = end_event
        if min(segment) == segment_start:
            end_event.is_left = False
        else:
            source_event.is_left = False
        events_queue.push(source_event)
        events_queue.push(end_event)
    return events_queue


def sweep(segments: Sequence[Segment]
          ) -> Iterable[Tuple[Point, Tuple[int, int]]]:
    events_queue = _to_events_queue(segments)
    sweep_line = red_black.tree(key=SweepLineKey)
    while events_queue:
        event = events_queue.pop()
        point, same_point_events = event.point, [event]
        while events_queue and events_queue.peek().point == point:
            same_point_events.append(events_queue.pop())
        for event, other_event in combinations(same_point_events, 2):
            segment_id, other_segment_id = (event.segment_id,
                                            other_event.segment_id)
            if (segment_id != other_segment_id
                    and point in segments[segment_id]
                    and point in segments[other_segment_id]):
                yield point, _to_sorted_pair(segment_id,
                                             other_segment_id)
        for event in same_point_events:
            if event.is_left:
                sweep_line.add(event)
                try:
                    next_event = sweep_line.next(event)
                except ValueError:
                    next_event = None
                try:
                    previous_event = sweep_line.prev(event)
                except ValueError:
                    previous_event = None
                if next_event is not None:
                    yield from _detect_intersection(event, next_event,
                                                    events_queue=events_queue)
                if previous_event is not None:
                    yield from _detect_intersection(previous_event, event,
                                                    events_queue=events_queue)
            else:
                event = event.complement
                if event not in sweep_line:
                    continue
                try:
                    next_event = sweep_line.next(event)
                except ValueError:
                    next_event = None
                try:
                    previous_event = sweep_line.prev(event)
                except ValueError:
                    previous_event = None
                sweep_line.remove(event)
                if next_event is not None and previous_event is not None:
                    yield from _detect_intersection(previous_event, next_event,
                                                    events_queue=events_queue)


def _detect_intersection(first_event: SweepEvent, second_event: SweepEvent,
                         events_queue: PriorityQueue
                         ) -> Iterable[Tuple[Point, Tuple[int, int]]]:
    def divide_segment(event: SweepEvent, point: Point) -> None:
        # "left event" of the "right line segment"
        # resulting from dividing event.segment
        left_event = SweepEvent(True, point, event.complement,
                                event.segment_id)
        # "right event" of the "left line segment"
        # resulting from dividing event.segment
        right_event = SweepEvent(False, point, event, event.segment_id)
        if EventsQueueKey(left_event) < EventsQueueKey(event.complement):
            # avoid a rounding error,
            # the left event would be processed after the right event
            event.complement.is_left = True
            left_event.is_left = False
        event.complement.complement, event.complement = left_event, right_event
        events_queue.push(left_event)
        events_queue.push(right_event)

    intersections_points = find_intersections(first_event.segment,
                                              second_event.segment)

    if not intersections_points:
        return

    # The line segments associated to le1 and le2 intersect
    if len(intersections_points) == 1:
        point, = intersections_points
        if (first_event.point != point
                and first_event.complement.point != point):
            # if the intersection point is not an endpoint of le1.segment
            divide_segment(first_event, point)
            yield point, _to_sorted_pair(first_event.segment_id,
                                         second_event.segment_id)
        if (second_event.point != point
                and second_event.complement.point != point):
            # if the intersection point is not an endpoint of le2.segment
            divide_segment(second_event, point)
            yield point, _to_sorted_pair(first_event.segment_id,
                                         second_event.segment_id)
        return

    # The line segments associated to le1 and le2 overlap
    sorted_events = []
    if first_event.point == second_event.point:
        sorted_events.append(None)
    elif EventsQueueKey(first_event) < EventsQueueKey(second_event):
        sorted_events.append(second_event)
        sorted_events.append(first_event)
    else:
        sorted_events.append(first_event)
        sorted_events.append(second_event)

    if first_event.complement.point == second_event.complement.point:
        sorted_events.append(None)
    elif (EventsQueueKey(first_event.complement)
          < EventsQueueKey(second_event.complement)):
        sorted_events.append(second_event.complement)
        sorted_events.append(first_event.complement)
    else:
        sorted_events.append(first_event.complement)
        sorted_events.append(second_event.complement)

    if len(sorted_events) == 2:
        # both line segments are equal
        return
    for point in intersections_points:
        yield point, _to_sorted_pair(first_event.segment_id,
                                     second_event.segment_id)
    if len(sorted_events) == 3:
        # line segments share endpoint
        if sorted_events[2]:
            # line segments share the left endpoint
            divide_segment(sorted_events[2].complement, sorted_events[1].point)
        else:
            # line segments share the right endpoint
            divide_segment(sorted_events[0], sorted_events[1].point)
        return
    elif sorted_events[0] is not sorted_events[3].complement:
        # no line segment includes totally the other one
        divide_segment(sorted_events[0], sorted_events[1].point)
        divide_segment(sorted_events[1], sorted_events[2].point)
    else:
        # one line segment includes the other one
        divide_segment(sorted_events[0], sorted_events[1].point)
        divide_segment(sorted_events[3].complement, sorted_events[2].point)


def _to_sorted_pair(left_coordinate: int,
                    right_coordinate: int) -> Tuple[int, int]:
    return ((left_coordinate, right_coordinate)
            if left_coordinate < right_coordinate
            else (right_coordinate, left_coordinate))
