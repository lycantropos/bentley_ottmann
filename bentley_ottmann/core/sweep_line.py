from functools import partial
from typing import (Callable,
                    Optional,
                    Sequence,
                    cast)

from dendroid import red_black
from reprit.base import generate_repr
from robust.angular import (Orientation,
                            orientation)

from bentley_ottmann.hints import Scalar
from .event import Event
from .point import RealPoint
from .utils import merge_ids


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

    def move_to(self, point: RealPoint) -> None:
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
        orientation_with_other_start = orientation(end, start, other_start)
        orientation_with_other_end = orientation(end, start, other_end)
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
                    event.segments_ids = other_event.segments_ids = merge_ids(
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
