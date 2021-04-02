from functools import partial
from typing import (Callable,
                    Optional)

from dendroid import red_black
from ground.base import (Context,
                         Orientation)
from ground.hints import Point
from reprit.base import generate_repr

from .event import LeftEvent


class SweepLine:
    __slots__ = 'context', '_set'

    def __init__(self, context: Context) -> None:
        self.context = context
        self._set = red_black.set_(key=partial(SweepLineKey,
                                               context.angle_orientation))

    __repr__ = generate_repr(__init__)

    def add(self, event: LeftEvent) -> None:
        self._set.add(event)

    def find_equal(self, event: LeftEvent) -> Optional[LeftEvent]:
        try:
            candidate = self._set.floor(event)
        except ValueError:
            return None
        else:
            return (candidate
                    if (candidate.start == event.start
                        and candidate.end == event.end)
                    else None)

    def remove(self, event: LeftEvent) -> None:
        self._set.remove(event)

    def above(self, event: LeftEvent) -> Optional[LeftEvent]:
        try:
            return self._set.next(event)
        except ValueError:
            return None

    def below(self, event: LeftEvent) -> Optional[LeftEvent]:
        try:
            return self._set.prev(event)
        except ValueError:
            return None


class SweepLineKey:
    __slots__ = 'event', 'orienteer'

    def __init__(self,
                 orienteer: Callable[[Point, Point, Point], Orientation],
                 event: LeftEvent) -> None:
        self.event, self.orienteer = event, orienteer

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: 'SweepLineKey') -> bool:
        """
        Checks if the segment (or at least the point) associated with event
        is lower than other's.
        """
        event, other_event = self.event, other.event
        if event is other_event:
            return False
        start, other_start = event.start, other_event.start
        end, other_end = event.end, other_event.end
        other_start_orientation = self.orienteer(start, end, other_start)
        other_end_orientation = self.orienteer(start, end, other_end)
        if other_start_orientation is other_end_orientation:
            start_x, start_y = start.x, start.y
            other_start_x, other_start_y = other_start.x, other_start.y
            if other_start_orientation is not Orientation.COLLINEAR:
                # other segment fully lies on one side
                return other_start_orientation is Orientation.COUNTERCLOCKWISE
            # segments are collinear
            elif start_x == other_start_x:
                end_x, end_y = end.x, end.y
                other_end_x, other_end_y = other_end.x, other_end.y
                if start_y != other_start_y:
                    # segments are vertical
                    return start_y < other_start_y
                # segments have same start
                elif end_y != other_end_y:
                    return end_y < other_end_y
                else:
                    # we can add handling of equal segments' fragments here
                    # to reduce number of searches,
                    # but it will make this implicit and complex
                    return end_x < other_end_x
            elif start_y != other_start_y:
                return start_y < other_start_y
            else:
                # segments are horizontal
                return start_x < other_start_x
        start_orientation = self.orienteer(other_start, other_end, start)
        end_orientation = self.orienteer(other_start, other_end, end)
        if start_orientation is end_orientation:
            return start_orientation is Orientation.CLOCKWISE
        elif other_start_orientation is Orientation.COLLINEAR:
            return other_end_orientation is Orientation.COUNTERCLOCKWISE
        elif start_orientation is Orientation.COLLINEAR:
            return end_orientation is Orientation.CLOCKWISE
        elif end_orientation is Orientation.COLLINEAR:
            return start_orientation is Orientation.CLOCKWISE
        else:
            return other_start_orientation is Orientation.COUNTERCLOCKWISE
