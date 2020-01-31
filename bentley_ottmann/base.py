from collections import defaultdict
from functools import partial
from itertools import (chain,
                       combinations)
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
                     _to_rational_segment,
                     find_intersections,
                     point_orientation_with_segment,
                     to_segments_relationship)
from .point import Point


class Event:
    __slots__ = ('is_left_endpoint', '_relationship',
                 'start', 'complement', '_segments_ids')

    def __init__(self,
                 is_left_endpoint: bool,
                 relationship: SegmentsRelationship,
                 start: Point,
                 complement: Optional['Event'],
                 segments_ids: Sequence[int]) -> None:
        self.is_left_endpoint = is_left_endpoint
        self._relationship = relationship
        self.start = start
        self.complement = complement
        self._segments_ids = segments_ids

    __repr__ = recursive_repr()(generate_repr(__init__))

    @property
    def segments_ids(self) -> Sequence[int]:
        return self._segments_ids

    @segments_ids.setter
    def segments_ids(self, segments_ids: Sequence[int]) -> None:
        self._segments_ids = self.complement._segments_ids = segments_ids

    @property
    def relationship(self) -> SegmentsRelationship:
        return self._relationship

    @relationship.setter
    def relationship(self, relationship: SegmentsRelationship) -> None:
        self._relationship = self.complement._relationship = relationship

    @property
    def is_intersection(self) -> bool:
        return self.relationship is not SegmentsRelationship.NONE

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
        return self.start, self.end

    def below_than_at_x(self, other: 'Event', x: Scalar) -> bool:
        y_at_x, other_y_at_x = self.y_at(x), other.y_at(x)
        if other_y_at_x != y_at_x:
            return y_at_x < other_y_at_x
        else:
            _, start_y = self.start
            _, other_start_y = other.start
            end_x, end_y = self.end
            other_end_x, other_end_y = other.end
            return ((start_y, end_y, other_end_x)
                    < (other_start_y, other_end_y, end_x))

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
                                           ((x, start_y), (x, end_y)))
            return result


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
                    # segments are vertical
                    return start_y < other_start_y
                # segments have same start
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
                return start_y > end_y
            else:
                return orientation_with_other_end is (
                    Orientation.COUNTERCLOCKWISE
                    if start_x < end_x
                    else Orientation.CLOCKWISE)
        elif start_x == other_start_x:
            return start_y < other_start_y
        elif orientation_with_other_start is Orientation.COLLINEAR:
            if other_event.is_vertical:
                return other_start_y < other_end_y
            elif start_x == other_end_x:
                return start_y < other_end_y
            else:
                return event.below_than_at_x(other_event,
                                             self.sweep_line.current_x)
        elif start == other_end:
            if event.is_vertical:
                return start_y > end_y
            else:
                return orientation_with_other_start is (
                    Orientation.COUNTERCLOCKWISE
                    if start_x < other_start_x
                    else Orientation.CLOCKWISE)
        elif start_x == other_end_x:
            return start_y < other_end_y
        elif orientation_with_other_end is Orientation.COLLINEAR:
            if event.is_vertical:
                return start_y < other_end_y
            else:
                return orientation_with_other_start is (
                    Orientation.COUNTERCLOCKWISE
                    if start_x < end_x
                    else Orientation.CLOCKWISE)
        elif event.is_vertical:
            other_y_at_start_x = other_event.y_at(start_x)
            if other_y_at_start_x != start_y:
                return start_y < other_y_at_start_x
            else:
                return start_y > end_y
        else:
            return event.below_than_at_x(other_event,
                                         self.sweep_line.current_x)


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
        segments_relationship = (SegmentsRelationship.NONE
                                 if len(same_segments_ids) == 1
                                 else SegmentsRelationship.OVERLAP)
        start_event = Event(is_left_endpoint=True,
                            relationship=segments_relationship,
                            start=left_endpoint,
                            complement=None,
                            segments_ids=same_segments_ids)
        end_event = Event(is_left_endpoint=False,
                          relationship=segments_relationship,
                          start=right_endpoint,
                          complement=start_event,
                          segments_ids=same_segments_ids)
        start_event.complement = end_event
        events_queue.push(start_event)
        events_queue.push(end_event)
    return events_queue


def segments_intersect(segments: Sequence[Segment],
                       *,
                       accurate: bool = True) -> bool:
    """
    Checks if segments have at least one intersection.

    Based on Shamos-Hoey algorithm.

    Time complexity:
        ``O(len(segments) * log len(segments))``
    Memory complexity:
        ``O(len(segments))``
    Reference:
        https://en.wikipedia.org/wiki/Sweep_line_algorithm

    :param segments: sequence of segments.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: true if segments intersection found, false otherwise.

    >>> segments_intersect([])
    False
    >>> segments_intersect([((0., 0.), (2., 2.))])
    False
    >>> segments_intersect([((0., 0.), (2., 0.)),
    ...                     ((0., 2.), (2., 2.))])
    False
    >>> segments_intersect([((0., 0.), (2., 2.)),
    ...                     ((0., 0.), (2., 2.))])
    True
    >>> segments_intersect([((0., 0.), (2., 2.)),
    ...                     ((2., 0.), (0., 2.))])
    True
    """
    return any(_sweep(segments,
                      accurate=accurate))


def edges_intersect(vertices: Sequence[Point],
                    *,
                    accurate: bool = True) -> bool:
    """
    Checks if polygon has self-intersection.

    Based on Shamos-Hoey algorithm.

    Time complexity:
        ``O(len(segments) * log len(segments))``
    Memory complexity:
        ``O(len(segments) + len(intersections))``
    Reference:
        https://en.wikipedia.org/wiki/Sweep_line_algorithm

    :param vertices: sequence of polygon vertices.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: true if polygon is self-intersecting, false otherwise.

    >>> edges_intersect([(0., 0.), (2., 0.), (2., 2.)])
    False
    >>> edges_intersect([(0., 0.), (2., 0.), (1., 0.)])
    True
    """
    edges = _vertices_to_edges(vertices)

    def non_neighbours_intersect(edges_ids: Iterable[Tuple[int, int]],
                                 last_edge_index: int = len(edges) - 1
                                 ) -> bool:
        return any(next_segment_id - segment_id > 1
                   and (segment_id != 0 or next_segment_id != last_edge_index)
                   for segment_id, next_segment_id in edges_ids)

    events = defaultdict(set)
    for point, (first_event, second_event) in _sweep(edges,
                                                     accurate=accurate):
        if (first_event.relationship is SegmentsRelationship.OVERLAP
                or second_event.relationship is SegmentsRelationship.OVERLAP
                or non_neighbours_intersect(_to_combinations(
                        _merge_ids(first_event.segments_ids,
                                   second_event.segments_ids)))):
            return True
        events[point].update((first_event, second_event))
    # we are collecting and processing events again
    # because of possible overlaps which can arise during sweeping/reordering
    return non_neighbours_intersect(_events_to_segments_ids_pairs(events))


def segments_intersections(segments: Sequence[Segment],
                           *,
                           accurate: bool = True
                           ) -> Dict[Point, Set[Tuple[int, int]]]:
    """
    Returns mapping between intersection points
    and corresponding segments indices.

    Based on Bentley-Ottmann algorithm.

    Time complexity:
        ``O((len(segments) + len(intersections)) * log len(segments))``
    Memory complexity:
        ``O(len(segments) + len(intersections))``
    Reference:
        https://en.wikipedia.org/wiki/Bentley%E2%80%93Ottmann_algorithm

    >>> segments_intersections([])
    {}
    >>> segments_intersections([((0., 0.), (2., 2.))])
    {}
    >>> segments_intersections([((0., 0.), (2., 0.)),
    ...                         ((0., 2.), (2., 2.))])
    {}
    >>> segments_intersections([((0., 0.), (2., 2.)),
    ...                         ((0., 0.), (2., 2.))])
    {(0.0, 0.0): {(0, 1)}, (2.0, 2.0): {(0, 1)}}
    >>> segments_intersections([((0., 0.), (2., 2.)),
    ...                         ((2., 0.), (0., 2.))])
    {(1.0, 1.0): {(0, 1)}}


    :param segments: sequence of segments.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns:
        mapping between intersection points and corresponding segments indices.
    """
    # we are collecting and processing events afterwards
    # because of possible overlaps which can arise during sweeping/reordering
    events = defaultdict(set)
    for point, events_pair in _sweep(segments,
                                     accurate=accurate):
        events[point].update(events_pair)
    result = {}
    for segment_id, next_segment_id in _events_to_segments_ids_pairs(events):
        for point in find_intersections(segments[segment_id],
                                        segments[next_segment_id]):
            result.setdefault(point, set()).add((segment_id, next_segment_id))
    return result


def _events_to_segments_ids_pairs(events: Dict[Point, Set[Event]]
                                  ) -> Set[Tuple[int, int]]:
    return set(chain.from_iterable(
            _to_combinations(_merge_ids(*[event.segments_ids
                                          for event in point_events]))
            for _, point_events in events.items()))


def _sweep(segments: Sequence[Segment],
           *,
           accurate: bool) -> Iterable[Tuple[Point, Tuple[Event, Event]]]:
    events_queue = _to_events_queue([_to_rational_segment(segment)
                                     for segment in segments]
                                    if accurate
                                    else segments)
    sweep_line = SweepLine()
    while events_queue:
        event = events_queue.pop()
        point, same_point_events = event.start, [event]
        while events_queue and events_queue.peek().start == point:
            same_point_events.append(events_queue.pop())
        for event, other_event in _to_combinations(same_point_events):
            yield point, (event, other_event)
        sweep_line.move_to(point)
        for event in same_point_events:
            if len(event.segments_ids) > 1:
                yield point, (event, event)

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
                    yield from _detect_intersection(below_event, event,
                                                    events_queue=events_queue)
                if above_event is not None:
                    yield from _detect_intersection(event, above_event,
                                                    events_queue=events_queue)
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
                    yield from _detect_intersection(below_event, above_event,
                                                    events_queue=events_queue)


def _detect_intersection(first_event: Event, second_event: Event,
                         events_queue: EventsQueue
                         ) -> Iterable[Tuple[Point, Tuple[Event, Event]]]:
    def divide_segment(event: Event, break_point: Point,
                       relationship: SegmentsRelationship,
                       segments_ids: Optional[Sequence[int]] = None) -> None:
        # "left event" of the "right line segment"
        # resulting from dividing event.segment
        if segments_ids is None:
            segments_ids = event.segments_ids
        else:
            event.segments_ids = segments_ids
        left_event = Event(is_left_endpoint=True,
                           relationship=relationship,
                           start=break_point,
                           complement=event.complement,
                           segments_ids=segments_ids)
        # "right event" of the "left line segment"
        # resulting from dividing event.segment
        right_event = Event(is_left_endpoint=False,
                            relationship=relationship,
                            start=break_point,
                            complement=event,
                            segments_ids=segments_ids)
        event.relationship = relationship
        event.complement.complement, event.complement = left_event, right_event
        events_queue.push(left_event)
        events_queue.push(right_event)

    first_segment, second_segment = first_event.segment, second_event.segment
    relationship = to_segments_relationship(first_segment, second_segment)

    if relationship is SegmentsRelationship.NONE:
        return
    # segments intersect
    elif relationship is SegmentsRelationship.CROSS:
        point = _find_intersection(first_segment, second_segment)
        if point != first_event.start and point != first_event.end:
            divide_segment(first_event, point, relationship)
        if point != second_event.start and point != second_event.end:
            divide_segment(second_event, point, relationship)
        yield point, (first_event, second_event)
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

        segments_ids = _merge_ids(first_event.segments_ids,
                                  second_event.segments_ids)
        if len(sorted_events) == 2:
            # both line segments are equal
            first_event.segments_ids = second_event.segments_ids = segments_ids
            yield first_event.start, (first_event, second_event)
            yield first_event.end, (first_event, second_event)
        elif len(sorted_events) == 3:
            # line segments share endpoint
            point = sorted_events[1].start
            yield point, (first_event, second_event)
            divide_segment(sorted_events[2].complement
                           # line segments share the left endpoint
                           if sorted_events[2]
                           # line segments share the right endpoint
                           else sorted_events[0], point,
                           relationship, segments_ids)
        else:
            first_point, second_point = (sorted_events[1].start,
                                         sorted_events[2].start)
            yield first_point, (first_event, second_event)
            yield second_point, (first_event, second_event)
            divide_segment(sorted_events[0], first_point, relationship,
                           segments_ids)
            divide_segment(sorted_events[0]
                           # one line segment includes the other one
                           if sorted_events[0] is sorted_events[3].complement
                           # no line segment includes totally the other one
                           else sorted_events[1], second_point, relationship,
                           segments_ids)


def _vertices_to_edges(vertices: Sequence[Point]) -> Sequence[Segment]:
    return [(vertices[index], vertices[(index + 1) % len(vertices)])
            for index in range(len(vertices))]


def _merge_ids(*sequences: Sequence[int]) -> Sequence[int]:
    result = set()
    for sequence in sequences:
        result.update(sequence)
    return sorted(result)


_to_combinations = partial(combinations,
                           r=2)
