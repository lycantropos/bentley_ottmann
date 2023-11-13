from __future__ import annotations

from functools import partial
from typing import (Any,
                    Callable,
                    Optional)

from dendroid import red_black
from dendroid.hints import KeyedSet
from ground.base import (Context,
                         Orientation)
from ground.hints import Point
from reprit.base import generate_repr

from .event import LeftEvent

"""
Implementation of the Sweep Line data structure for the Bentley-Ottmann algorithm.

This script defines the 'SweepLine' class, a key component of the Bentley-Ottmann algorithm 
for detecting intersections in a set of line segments. The Sweep Line is a dynamic ordered 
set that tracks the segments currently intersecting with the sweep line (an imaginary line 
sweeping across the plane). It's implemented using a red-black tree for efficient insertion, 
deletion, and querying of segments.

Classes:
    SweepLine: Manages the state of the sweep line during the execution of the algorithm.
    SweepLineKey: Provides a custom ordering for segments in the sweep line based on their 
    geometric properties.

The Sweep Line class offers methods to add and remove segments, and to find a segment directly 
above or below a given segment in the current state of the sweep line. The ordering of segments 
in the sweep line is determined by the SweepLineKey class, which compares segments based on 
their intersection with the sweep line and their orientation relative to each other.

The implementation is tailored for handling the complexities of geometric calculations and 
intersection detection in the Bentley-Ottmann algorithm, ensuring efficient processing of 
events and segments during the sweep.

Example:
    Given a set of line segments and a geometric context, the SweepLine class can be used 
    within the Bentley-Ottmann algorithm to manage segments intersecting with the sweep line:
    >>> sweep_line = SweepLine(your_context)
    >>> for segment in segments:
    ...     sweep_line.add(segment)
    ...     # Process intersections and update sweep line as needed
    ...     sweep_line.remove(segment)
"""


class SweepLine:
    """
    Represents the sweep line in the Bentley-Ottmann algorithm for intersection detection.

    This class manages the state of the sweep line, which is an imaginary vertical line 
    sweeping across the plane, intersecting with line segments. It tracks the segments 
    currently intersecting with the sweep line, ordered by their position relative to the 
    sweep line.

    Attributes:
        context (Context): The geometric context providing necessary operations for comparing points.
        _set (KeyedSet[SweepLineKey, LeftEvent]): A set of events ordered based on their geometric positioning.
    """

    __slots__ = 'context', '_set'

    def __init__(self, context: Context) -> None:
        """
        Initializes the SweepLine instance.

        Args:
            context (Context): Geometric context for comparing points.
        """
        self.context = context
        # Initialize a red-black tree set with a custom key function for ordering the segments.
        self._set: KeyedSet[SweepLineKey, LeftEvent] = red_black.set_(
                key=partial(SweepLineKey, context.angle_orientation)
        )

    __repr__ = generate_repr(__init__)

    def add(self, event: LeftEvent) -> None:
        """
        Adds a left event (representing a line segment) to the sweep line.

        Args:
            event (LeftEvent): The event to be added to the sweep line.
        """
        self._set.add(event)

    def find_equal(self, event: LeftEvent) -> Optional[LeftEvent]:
        """
        Finds an event in the sweep line that has the same start and end points as the given event.

        Args:
            event (LeftEvent): The event to find an equal match for.

        Returns:
            Optional[LeftEvent]: An event equal to the given event, or None if no match is found.
        """
        try:
            # Finds the largest event in the set that is less than or equal to the given event
            candidate = self._set.floor(event)
        except ValueError:
            # If no such event exists, return None
            return None
        else:
            # Return the candidate if it matches the start and end points of the given event
            return (candidate
                    if (candidate.start == event.start
                        and candidate.end == event.end)
                    else None)

    def remove(self, event: LeftEvent) -> None:
        """
        Removes an event from the sweep line.

        Args:
            event (LeftEvent): The event to be removed from the sweep line.
        """
        self._set.remove(event)

    def above(self, event: LeftEvent) -> Optional[LeftEvent]:
        """
        Finds the event immediately above the given event on the sweep line.

        Args:
            event (LeftEvent): The event to find the above neighbor for.

        Returns:
            Optional[LeftEvent]: The event above the given event, or None if there is no such event.
        """
        try:
            # Returns the smallest event in the set that is greater than the given event
            return self._set.next(event)
        except ValueError:
            # If no such event exists, return None
            return None

    def below(self, event: LeftEvent) -> Optional[LeftEvent]:
        """
        Finds the event immediately below the given event on the sweep line.

        Args:
            event (LeftEvent): The event to find the below neighbor for.

        Returns:
            Optional[LeftEvent]: The event below the given event, or None if there is no such event.
        """
        try:
            # Returns the largest event in the set that is less than the given event
            return self._set.prev(event)
        except ValueError:
            # If no such event exists, return None
            return None

class SweepLineKey:
    """
    Key class used for ordering segments in the sweep line.

    This class defines a custom ordering for the segments intersecting the sweep line in 
    the Bentley-Ottmann algorithm. The ordering is crucial to accurately determine the 
    relative positions of segments as the sweep line progresses.

    Attributes:
        event (LeftEvent): The left event associated with this key.
        orienteer (Callable[[Point, Point, Point], Orientation]): A function to determine 
            the orientation of points relative to each other.
    """

    __slots__ = 'event', 'orienteer'

    def __init__(self,
                 orienteer: Callable[[Point, Point, Point], Orientation],
                 event: LeftEvent) -> None:
        """
        Initializes a SweepLineKey instance.

        Args:
            orienteer: A function that determines the orientation of three points.
            event: The left event to be ordered in the sweep line.
        """
        self.event, self.orienteer = event, orienteer

    __repr__ = generate_repr(__init__)

    def __lt__(self, other: SweepLineKey) -> Any:
        """
        Determines the ordering of two segments in the sweep line.

        This method is used to compare two segments to determine which one appears lower 
        on the sweep line. The comparison is based on the orientation of the segments 
        relative to each other and their position along the y-axis.

        Args:
            other (SweepLineKey): Another SweepLineKey to compare with.

        Returns:
            bool: True if this segment is lower than the other segment on the sweep line.
        """
        event, other_event = self.event, other.event

        # Return False immediately if comparing the same event
        if event is other_event:
            return False

        start, other_start = event.start, other_event.start
        end, other_end = event.end, other_event.end

        # Determine the orientation of the other segment's start and end relative to this segment
        other_start_orientation = self.orienteer(start, end, other_start)
        other_end_orientation = self.orienteer(start, end, other_end)

        if other_start_orientation is other_end_orientation:
            # Handle the case where the other segment is collinear or on one side of this segment
            return self._handle_collinear_or_side_comparison(start, end, other_start, other_end, other_start_orientation)
        else:
            # Handle the case where the other segment intersects or overlaps with this segment
            return self._handle_intersection_comparison(start, end, other_start, other_end, other_start_orientation)

    def _handle_collinear_or_side_comparison(self, start, end, other_start, other_end, other_orientation):
        """
        Handles comparison when the other segment is collinear or on one side.

        Args:
            start, end (Point): Start and end points of this segment.
            other_start, other_end (Point): Start and end points of the other segment.
            other_orientation (Orientation): Orientation of the other segment relative to this segment.

        Returns:
            bool: Result of the comparison.
        """
        start_x, start_y = start.x, start.y
        other_start_x, other_start_y = other_start.x, other_start.y

        if other_orientation is not Orientation.COLLINEAR:
            # If the other segment lies entirely on one side of this segment
            return other_orientation is Orientation.COUNTERCLOCKWISE
        elif start_y == other_start_y:
            # If segments are collinear and horizontal
            return self._compare_horizontal_segments(start_x, end.x, other_start_x, other_end.x, end.y, other_end.y)
        else:
            # If segments are not horizontal, compare based on y-coordinate
            return start_y < other_start_y

    def _handle_intersection_comparison(self, start, end, other_start, other_end, other_start_orientation):
        """
        Handles comparison when the other segment intersects or overlaps.

        Args:
            start, end (Point): Start and end points of this segment.
            other_start, other_end (Point): Start and end points of the other segment.
            other_start_orientation (Orientation): Orientation of the other segment's start relative to this segment.

        Returns:
            bool: Result of the comparison.
        """
        start_orientation = self.orienteer(other_start, other_end, start)
        end_orientation = self.orienteer(other_start, other_end, end)

        if start_orientation is end_orientation:
            return start_orientation is Orientation.CLOCKWISE
        elif other_start_orientation is Orientation.COLLINEAR:
            return end_orientation is Orientation.COUNTERCLOCKWISE
        elif start_orientation is Orientation.COLLINEAR:
            return end_orientation is Orientation.CLOCKWISE
        elif end_orientation is Orientation.COLLINEAR:
            return start_orientation is Orientation.CLOCKWISE
        else:
            return other_start_orientation is Orientation.COUNTERCLOCKWISE

    def _compare_horizontal_segments(self, start_x, end_x, other_start_x, other_end_x, end_y, other_end_y):
        """
        Compares horizontal segments based on their x and y coordinates.

        Args:
            start_x, end_x (float): X-coordinates of this segment's start and end points.
            other_start_x, other_end_x (float): X-coordinates of the other segment's start and end points.
            end_y, other_end_y (float): Y-coordinates of this segment's and the other segment's end points.

        Returns:
            bool: Result of the comparison.
        """
        if start_x != other_start_x:
            return start_x < other_start_x
        elif end_y != other_end_y:
            return end_y < other_end_y
        else:
            return end_x < other_end_x
