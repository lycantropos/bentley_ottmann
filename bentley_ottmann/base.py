from collections import OrderedDict
from itertools import combinations
from reprlib import recursive_repr
from typing import (Dict,
                    Iterable,
                    Optional,
                    Sequence,
                    Set,
                    Tuple)

from dendroid import red_black
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .angular import (Orientation,
                      to_orientation)
from .linear import (Segment,
                     find_intersections)
from .point import Point


class Event:
    __slots__ = ('is_left', 'start', 'complement', 'segment_id')

    def __init__(self, is_left: bool, start: Point,
                 complement: Optional['Event'],
                 segment_id: int) -> None:
        self.is_left = is_left
        self.start = start
        self.complement = complement
        self.segment_id = segment_id

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def end(self) -> Point:
        return self.complement.start

    @property
    def segment(self) -> Segment:
        return Segment(self.start, self.end)

    def is_above(self, point: Point) -> bool:
        return ((to_orientation(self.start, point, self.end)
                 is Orientation.CLOCKWISE)
                if self.is_left
                else (to_orientation(self.end, point, self.start)
                      is Orientation.CLOCKWISE))

    def is_below(self, point: Point) -> bool:
        return ((to_orientation(self.start, point, self.end)
                 is Orientation.COUNTERCLOCKWISE)
                if self.is_left
                else (to_orientation(self.end, point, self.start)
                      is Orientation.COUNTERCLOCKWISE))


SweepLine = red_black.Tree[Event]
EventsQueue = PriorityQueue[Event]


class EventsQueueKey:
    __slots__ = ('event',)

    def __init__(self, event: Event) -> None:
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
        event_start, other_event_start = event.start, other_event.start
        event_start_x, event_start_y = event_start
        other_event_start_x, other_event_start_y = other_event_start
        if event_start_x != other_event_start_x:
            # different x-coordinate,
            # the event with lower x-coordinate is processed first
            return event_start_x < other_event_start_x
        elif event_start_y != other_event_start_y:
            # different points, but same x-coordinate,
            # the event with lower y-coordinate is processed first
            return event_start_y < other_event_start_y
        elif event.is_left is not other_event.is_left:
            # same point, but one is a left endpoint
            # and the other a right endpoint,
            # the right endpoint is processed first
            return event.is_left
        # same point, both events are left endpoints
        # or both are right endpoints
        return event.is_below(other_event.end)


class SweepLineKey:
    __slots__ = ('event',)

    def __init__(self, event: Event) -> None:
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
        event_start, other_event_start = event.start, other_event.start
        if not ((to_orientation(event_start, other_event_start, event.end)
                 is not Orientation.COLLINEAR)
                or (to_orientation(event_start, other_event.end, event.end)
                    is not Orientation.COLLINEAR)):
            # segments are collinear
            return (event.segment_id != other_event.segment_id
                    and EventsQueueKey(event) < EventsQueueKey(other_event))
        # segments are not collinear
        elif event_start == other_event_start:
            # same left endpoint, use the right endpoint to sort
            return event.is_below(other_event.end)
        # different left endpoint, use the left endpoint to sort
        event_start_x, event_start_y = event_start
        other_event_start_x, other_event_start_y = other_event_start
        if event_start_x == other_event_start_x:
            return event_start_y < other_event_start_y
        elif EventsQueueKey(event) < EventsQueueKey(other_event):
            # the line segment associated to `other_event` has been inserted
            # into sweep line after the line segment associated to `self`
            return event.is_below(other_event_start)
        else:
            # has the line segment associated to `self` been inserted
            # into sweep line after the line segment associated to `other`?
            return other_event.is_above(event_start)


def _to_events_queue(segments: Sequence[Segment]) -> PriorityQueue[Event]:
    events_queue = PriorityQueue(key=EventsQueueKey)
    for segment_id, segment in enumerate(segments):
        start, end = segment
        start_event = Event(True, start, None, segment_id)
        end_event = Event(True, end, start_event, segment_id)
        start_event.complement = end_event
        if min(segment) == start:
            end_event.is_left = False
        else:
            start_event.is_left = False
        events_queue.push(start_event)
        events_queue.push(end_event)
    return events_queue


def segments_intersect(segments: Sequence[Segment]) -> bool:
    return any(_sweep(segments))


def edges_intersect(edges: Sequence[Segment]) -> bool:
    last_edge_index = len(edges) - 1
    return any(next_segment_id - segment_id > 1
               and (segment_id != 0 or next_segment_id != last_edge_index)
               for segment_id, next_segment_id in _sweep(edges))


def segments_intersections(segments: Sequence[Segment]
                           ) -> Dict[Point, Set[Tuple[int, int]]]:
    result = OrderedDict()
    for segment_id, next_segment_id in _sweep(segments):
        for point in find_intersections(segments[segment_id],
                                        segments[next_segment_id]):
            result.setdefault(point, set()).add((segment_id, next_segment_id))
    return result


def _sweep(segments: Sequence[Segment]) -> Iterable[Tuple[int, int]]:
    events_queue = _to_events_queue(segments)
    sweep_line = red_black.tree(key=SweepLineKey)
    while events_queue:
        event = events_queue.pop()
        point, same_point_events = event.start, [event]
        while events_queue and events_queue.peek().start == point:
            same_point_events.append(events_queue.pop())
        for event, other_event in combinations(same_point_events, 2):
            segment_id, other_segment_id = (event.segment_id,
                                            other_event.segment_id)
            if (segment_id != other_segment_id
                    and point in segments[segment_id]
                    and point in segments[other_segment_id]):
                yield _to_sorted_pair(segment_id, other_segment_id)
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


def _detect_intersection(first_event: Event, second_event: Event,
                         events_queue: PriorityQueue
                         ) -> Iterable[Tuple[Point, Tuple[int, int]]]:
    def divide_segment(event: Event, point: Point) -> None:
        # "left event" of the "right line segment"
        # resulting from dividing event.segment
        left_event = Event(True, point, event.complement,
                           event.segment_id)
        # "right event" of the "left line segment"
        # resulting from dividing event.segment
        right_event = Event(False, point, event, event.segment_id)
        if EventsQueueKey(left_event) > EventsQueueKey(event.complement):
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
        not_first_event_endpoint = (first_event.start != point
                                    and first_event.end != point)
        not_second_event_endpoint = (
                second_event.start != point
                and second_event.end != point)
        if not_first_event_endpoint:
            # if the intersection start is not an endpoint of le1.segment
            divide_segment(first_event, point)
        if not_second_event_endpoint:
            # if the intersection start is not an endpoint of le2.segment
            divide_segment(second_event, point)
        if not_first_event_endpoint or not_first_event_endpoint:
            yield _to_sorted_pair(first_event.segment_id,
                                  second_event.segment_id)
        return

    # The line segments associated to le1 and le2 overlap
    sorted_events = []
    if first_event.start == second_event.start:
        sorted_events.append(None)
    elif EventsQueueKey(first_event) < EventsQueueKey(second_event):
        sorted_events.append(second_event)
        sorted_events.append(first_event)
    else:
        sorted_events.append(first_event)
        sorted_events.append(second_event)

    if first_event.end == second_event.end:
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
    yield _to_sorted_pair(first_event.segment_id, second_event.segment_id)
    if len(sorted_events) == 3:
        # line segments share endpoint
        if sorted_events[2]:
            # line segments share the left endpoint
            divide_segment(sorted_events[2].complement, sorted_events[1].start)
        else:
            # line segments share the right endpoint
            divide_segment(sorted_events[0], sorted_events[1].start)
        return
    elif sorted_events[0] is not sorted_events[3].complement:
        # no line segment includes totally the other one
        divide_segment(sorted_events[0], sorted_events[1].start)
        divide_segment(sorted_events[1], sorted_events[2].start)
    else:
        # one line segment includes the other one
        divide_segment(sorted_events[0], sorted_events[1].start)
        divide_segment(sorted_events[3].complement, sorted_events[2].start)


def _to_sorted_pair(left_coordinate: int,
                    right_coordinate: int) -> Tuple[int, int]:
    return ((left_coordinate, right_coordinate)
            if left_coordinate < right_coordinate
            else (right_coordinate, left_coordinate))
