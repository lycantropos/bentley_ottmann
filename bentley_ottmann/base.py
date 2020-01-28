from collections import defaultdict
from functools import partial
from itertools import (combinations,
                       product)
from reprlib import recursive_repr
from typing import (Callable,
                    Dict,
                    Iterable,
                    Optional,
                    Sequence,
                    Set,
                    Tuple,
                    cast)

from dendroid import red_black
from prioq.base import PriorityQueue
from reprit.base import generate_repr

from .angular import Orientation
from .hints import Scalar
from .linear import (Segment,
                     SegmentsRelationship,
                     _find_intersection,
                     find_intersections,
                     point_orientation_with_segment,
                     to_segments_relationship)
from .point import Point


class Event:
    __slots__ = ('is_left_endpoint', 'is_intersection', 'start', 'complement',
                 '_segments_ids')

    def __init__(self,
                 *,
                 is_left_endpoint: bool,
                 is_intersection: bool,
                 start: Point,
                 complement: Optional['Event'],
                 segments_ids: Sequence[int]) -> None:
        self.is_left_endpoint = is_left_endpoint
        self.is_intersection = is_intersection
        self.start = start
        self.complement = complement
        self._segments_ids = segments_ids

    @property
    def segments_ids(self) -> Sequence[int]:
        return self._segments_ids

    @segments_ids.setter
    def segments_ids(self, segments_ids: Sequence[int]) -> None:
        self._segments_ids = self.complement._segments_ids = segments_ids

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def is_vertical(self) -> bool:
        start_x, _ = self.start
        end_x, _ = self.end
        return start_x == end_x

    @property
    def is_horizontal(self) -> bool:
        _, start_y = self.start
        _, end_y = self.end
        return start_y == end_y

    @property
    def end(self) -> Point:
        return self.complement.start

    @property
    def segment(self) -> Segment:
        return Segment(self.start, self.end)

    def y_at(self, x: Scalar) -> Scalar:
        if self.is_vertical or self.is_horizontal:
            _, start_y = self.start
            return start_y
        else:
            start_x, start_y = self.start
            if x == start_x:
                return start_y
            end_x, end_y = self.end
            if x == end_x:
                return end_y
            _, result = _find_intersection(self.segment,
                                           Segment(Point(x, start_y),
                                                   Point(x, end_y)))
            return result

    def is_above(self, point: Point) -> bool:
        return (point_orientation_with_segment(point, self.segment)
                is Orientation.CLOCKWISE)

    def is_below(self, point: Point) -> bool:
        return (point_orientation_with_segment(point, self.segment)
                is Orientation.COUNTERCLOCKWISE)


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
        """
        Checks if the event should be processed before the other.
        """
        if not isinstance(other, EventsQueueKey):
            return NotImplemented
        event, other_event = self.event, other.event
        start_x, start_y = event.start
        other_start_x, other_start_y = other_event.start
        if start_x != other_start_x:
            # different x-coordinate,
            # the event with lower x-coordinate is processed first
            return start_x < other_start_x
        elif start_y != other_start_y:
            # different starts, but same x-coordinate,
            # the event with lower y-coordinate is processed first
            return start_y < other_start_y
        elif event.end == other_event.end:
            # same segments
            return (event.segments_ids < other_event.segments_ids
                    if event.is_intersection is other_event.is_intersection
                    else event.is_intersection)
        elif event.is_left_endpoint is not other_event.is_left_endpoint:
            # same start, but one is a left endpoint
            # and the other is a right endpoint,
            # the right endpoint is processed first
            return not event.is_left_endpoint
        else:
            # same start, different end,
            # both events are left endpoints
            # or both are right endpoints
            return event.end < other_event.end


class SweepLine:
    def __init__(self, *events: Event,
                 current_x: Optional[Scalar] = None) -> None:
        self.current_x = current_x
        self._tree = red_black.tree(*events,
                                    key=cast(Callable[[Event], SweepLineKey],
                                             partial(SweepLineKey, self)))

    __repr__ = generate_repr(__init__)

    @property
    def events(self) -> Sequence[Event]:
        return list(self._tree)

    def __contains__(self, event: Event) -> bool:
        return event in self._tree

    def move_to(self, point: Point) -> None:
        self.current_x, _ = point

    def add(self, event: Event) -> None:
        self._tree.add(event)

    def remove(self, event: Event) -> None:
        self._tree.remove(event)

    def above(self, event: Event) -> Event:
        return self._tree.next(event)

    def below(self, event: Event) -> Event:
        return self._tree.prev(event)


class SweepLineKey:
    __slots__ = ('sweep_line', 'event')

    def __init__(self, sweep_line: SweepLine, event: Event) -> None:
        self.sweep_line = sweep_line
        self.event = event

    __repr__ = generate_repr(__init__)

    def __eq__(self, other: 'SweepLineKey') -> bool:
        return (self.event == other.event
                if isinstance(other, SweepLineKey)
                else NotImplemented)

    def __lt__(self, other: 'SweepLineKey') -> bool:
        """
        Checks if the segment (or at least the point) associated with event
        is lower than other's.
        """
        if not isinstance(other, SweepLineKey):
            return NotImplemented
        if self is other:
            return False
        event, other_event = self.event, other.event
        if event is other_event:
            return False
        start, other_start = event.start, other_event.start
        end, other_end = event.end, other_event.end
        start_x, start_y = event.start
        other_start_x, other_start_y = other_event.start
        end_x, end_y = event.end
        other_end_x, other_end_y = other_event.end
        orientation_with_other_start = point_orientation_with_segment(
                other_start, event.segment)
        orientation_with_other_end = point_orientation_with_segment(
                other_end, event.segment)
        if orientation_with_other_start is orientation_with_other_end:
            if orientation_with_other_start is not Orientation.COLLINEAR:
                # other segment fully lies on one side
                return orientation_with_other_start is (
                    Orientation.COUNTERCLOCKWISE
                    if event.is_left_endpoint
                    else Orientation.CLOCKWISE)
            # segments are collinear
            elif start_x == other_start_x:
                if start_y != other_start_y:
                    return start_y < other_start_y
                elif end_x != other_end_x:
                    return end_x > other_end_x
                elif event.is_intersection is not other_event.is_intersection:
                    return event.is_intersection
                else:
                    event.segments_ids = other_event.segments_ids = _merge_ids(
                            event.segments_ids, other_event.segments_ids)
                    return not event.is_intersection
            # same start, different ends
            elif event.is_left_endpoint is not other_event.is_left_endpoint:
                # one start is a left endpoint
                # and the other is a right endpoint,
                # the right endpoint goes above
                return event.is_left_endpoint
            else:
                # both events are left endpoints or both are right endpoints
                return start_x > other_start_x
        elif start == other_start:
            if event.is_vertical:
                return orientation_with_other_end is (
                    Orientation.COUNTERCLOCKWISE
                    if end_x < other_end_x
                    else Orientation.CLOCKWISE)
            else:
                return orientation_with_other_end is (
                    Orientation.COUNTERCLOCKWISE
                    if event.is_left_endpoint
                    else Orientation.CLOCKWISE)
        elif start_x == other_start_x:
            return start_y < other_start_y
        elif orientation_with_other_start is Orientation.COLLINEAR:
            return orientation_with_other_end is Orientation.COUNTERCLOCKWISE
        elif orientation_with_other_end is Orientation.COLLINEAR:
            if event.is_vertical:
                if start_y != other_end_y:
                    return start_y < other_end_y
                else:
                    return not event.is_left_endpoint
            else:
                return orientation_with_other_start is (
                    Orientation.COUNTERCLOCKWISE
                    if (start_x, end_y) < (end_x, start_y)
                    else Orientation.CLOCKWISE)
        elif event.is_vertical:
            other_y_at_start_x = other_event.y_at(start_x)
            if start_y != other_y_at_start_x:
                return start_y < other_y_at_start_x
            else:
                return not event.is_left_endpoint
        else:
            x = self.sweep_line.current_x
            y_at_x, other_y_at_x = event.y_at(x), other_event.y_at(x)
            if y_at_x != other_y_at_x:
                return y_at_x < other_y_at_x
            else:
                _, start_y = event.start
                _, other_start_y = other_event.start
                end_x, end_y = event.end
                other_end_x, other_end_y = other_event.end
                return ((start_y, end_y, other_end_x)
                        < (other_start_y, other_end_y, end_x))


EventsQueue = cast(Callable[..., PriorityQueue[Event]],
                   partial(PriorityQueue[Event],
                           key=EventsQueueKey))


def _to_events_queue(segments: Sequence[Segment]) -> EventsQueue:
    segments_with_ids = sorted(
            (sorted(segment), segment_id)
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
        left_endpoint, right_endpoint = segment
        start_event = Event(is_left_endpoint=True,
                            is_intersection=False,
                            start=left_endpoint,
                            complement=None,
                            segments_ids=same_segments_ids)
        end_event = Event(is_left_endpoint=False,
                          is_intersection=False,
                          start=right_endpoint,
                          complement=start_event,
                          segments_ids=same_segments_ids)
        start_event.complement = end_event
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
    result = {}
    for segment_id, next_segment_id in _sweep(segments):
        for point in find_intersections(segments[segment_id],
                                        segments[next_segment_id]):
            result.setdefault(point, set()).add((segment_id, next_segment_id))
    return result


def _sweep(segments: Sequence[Segment]) -> Iterable[Tuple[int, int]]:
    events_queue = _to_events_queue(segments)
    sweep_line = SweepLine()
    intersections = defaultdict(set)
    while events_queue:
        event = events_queue.pop()
        point, same_point_events = event.start, [event]
        while events_queue and events_queue.peek().start == point:
            same_point_events.append(events_queue.pop())
        intersections[point].update(same_point_events)
        for event, other_event in product(same_point_events,
                                          repeat=2):
            for segment_id, other_segment_id in _to_combinations(
                    _merge_ids(event.segments_ids, other_event.segments_ids)):
                if (point in segments[segment_id]
                        and point in segments[other_segment_id]):
                    yield (segment_id, other_segment_id)
        sweep_line.move_to(point)
        for event in same_point_events:
            if event.is_left_endpoint:
                sweep_line.add(event)
                try:
                    below_event = sweep_line.below(event)
                except ValueError:
                    below_event = None
                try:
                    above_event = sweep_line.above(event)
                except ValueError:
                    above_event = None
                if below_event is not None:
                    yield from _detect_intersection(
                            below_event, event,
                            events_queue=events_queue,
                            intersections=intersections)
                if above_event is not None:
                    yield from _detect_intersection(
                            event, above_event,
                            events_queue=events_queue,
                            intersections=intersections)
            else:
                event = event.complement
                if event not in sweep_line:
                    continue
                try:
                    below_event = sweep_line.below(event)
                except ValueError:
                    below_event = None
                try:
                    above_event = sweep_line.above(event)
                except ValueError:
                    above_event = None
                sweep_line.remove(event)
                if below_event is not None and above_event is not None:
                    yield from _detect_intersection(
                            below_event, above_event,
                            events_queue=events_queue,
                            intersections=intersections)
    for same_point_events in intersections.values():
        for event, other_event in product(same_point_events,
                                          repeat=2):
            yield from _to_combinations(_merge_ids(event.segments_ids,
                                                   other_event.segments_ids))


def _detect_intersection(first_event: Event, second_event: Event,
                         events_queue: EventsQueue,
                         intersections: Dict[Point, Set[Event]]
                         ) -> Iterable[Tuple[int, int]]:
    def divide_segment(event: Event, break_point: Point,
                       segments_ids: Optional[Sequence[int]] = None) -> None:
        # "left event" of the "right line segment"
        # resulting from dividing event.segment
        if segments_ids is None:
            segments_ids = event.segments_ids
        else:
            event.segments_ids = segments_ids
        left_event = Event(is_left_endpoint=True,
                           is_intersection=True,
                           start=break_point,
                           complement=event.complement,
                           segments_ids=segments_ids)
        # "right event" of the "left line segment"
        # resulting from dividing event.segment
        right_event = Event(is_left_endpoint=False,
                            is_intersection=True,
                            start=break_point,
                            complement=event,
                            segments_ids=segments_ids)
        event.is_intersection = event.complement.is_intersection = True
        event.complement.complement, event.complement = left_event, right_event
        events_queue.push(left_event)
        events_queue.push(right_event)
        intersections[break_point].update([left_event, right_event])

    first_segment, second_segment = first_event.segment, second_event.segment
    relationship = to_segments_relationship(first_segment, second_segment)

    if relationship is SegmentsRelationship.NONE:
        return
    # segments intersect
    elif relationship is SegmentsRelationship.CROSS:
        point = _find_intersection(first_segment, second_segment)
        if point != first_event.start and point != first_event.end:
            divide_segment(first_event, point)
        if point != second_event.start and point != second_event.end:
            divide_segment(second_event, point)
        segments_ids = _merge_ids(first_event.segments_ids,
                                  second_event.segments_ids)
        intersections[point].update([first_event, second_event])
        yield from _to_combinations(segments_ids)
        return
    else:
        # segments overlap
        sorted_events = []
        if first_event.start == second_event.start:
            sorted_events.append(None)
        elif EventsQueueKey(first_event) > EventsQueueKey(second_event):
            sorted_events.append(second_event)
            sorted_events.append(first_event)
        else:
            sorted_events.append(first_event)
            sorted_events.append(second_event)

        if first_event.end == second_event.end:
            sorted_events.append(None)
        elif (EventsQueueKey(first_event.complement)
              > EventsQueueKey(second_event.complement)):
            sorted_events.append(second_event.complement)
            sorted_events.append(first_event.complement)
        else:
            sorted_events.append(first_event.complement)
            sorted_events.append(second_event.complement)

        if len(sorted_events) == 2:
            # both line segments are equal
            first_event.segments_ids = second_event.segments_ids = _merge_ids(
                    first_event.segments_ids, second_event.segments_ids)
            return
        segments_ids = _merge_ids(first_event.segments_ids,
                                  second_event.segments_ids)
        segments_pairs_ids = list(_to_combinations(segments_ids))
        yield from segments_pairs_ids
        if len(sorted_events) == 3:
            # line segments share endpoint
            if sorted_events[2]:
                # line segments share the left endpoint
                point = sorted_events[1].start
                intersections[point].update([first_event, second_event])
                divide_segment(sorted_events[2].complement, point,
                               segments_ids)
            else:
                # line segments share the right endpoint
                point = sorted_events[1].start
                intersections[point].update([first_event, second_event])
                divide_segment(sorted_events[0], point, segments_ids)
            return
        elif sorted_events[0] is not sorted_events[3].complement:
            # no line segment includes totally the other one
            first_point, second_point = (sorted_events[1].start,
                                         sorted_events[2].start)
            intersections[first_point].update([first_event, second_event])
            intersections[second_point].update([first_event, second_event])
            divide_segment(sorted_events[0], first_point, segments_ids)
            divide_segment(sorted_events[1], second_point, segments_ids)
        else:
            # one line segment includes the other one
            (first_event, second_event,
             third_event, fourth_event) = sorted_events
            first_point, second_point = second_event.start, third_event.start
            intersections[first_point].update([first_event, second_event])
            intersections[second_point].update([first_event, second_event])
            divide_segment(first_event, first_point, segments_ids)
            divide_segment(fourth_event.complement, second_point, segments_ids)


def _merge_ids(left_ids: Sequence[int],
               right_ids: Sequence[int]) -> Sequence[int]:
    return sorted({*left_ids, *right_ids})


_to_combinations = partial(combinations,
                           r=2)
