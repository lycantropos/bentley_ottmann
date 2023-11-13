from __future__ import annotations

from abc import (ABC,
                 abstractmethod)
from reprlib import recursive_repr
from typing import (ClassVar,
                    Dict,
                    List,
                    Optional,
                    Sequence,
                    Set,
                    Tuple)

from ground.base import Relation
from ground.hints import (Point,
                          Segment)
from reprit.base import generate_repr

from .utils import (classify_overlap,
                    to_sorted_pair)

"""
This script implements a key component of the Bentley-Ottmann algorithm, 
an efficient method for finding all intersections in a set of line segments in computational geometry.
It focuses on the definition and management of events, which are critical
in determining and processing the intersections and overlaps of segments.

The core of the script consists of the 'Event' abstract base class and its
two concrete subclasses 'LeftEvent' and 'RightEvent'. These classes model
the geometric events encountered during the algorithm's execution:

1. 'Event': An abstract base class defining the common interface for all events,
including essential properties and methods such as 'start', 'end', 'original_start',
'original_end', 'segments_ids', 'tangents', and an abstract method 'register_tangent'.

2. 'LeftEvent': Represents events occurring at the left end of line segments.
It includes functionality to create events from segments, handle event divisions,
merge with other events, and manage tangents and relations.
This class is essential for detecting and processing intersections and overlaps among segments.

3. 'RightEvent': Complements 'LeftEvent' by representing events on the right side of segments.
It maintains links to corresponding 'LeftEvent' instances and supports tangent management.

The design allows for a flexible handling of geometric events,
crucial for the efficient execution of the Bentley-Ottmann algorithm in various computational geometry applications.
The script is structured with clear definitions and comprehensive documentation,
making it useful for implementing the Bentley-Ottmann algorithm or similar geometric processing tasks.
"""

class Event(ABC):
    __slots__ = ()

    is_left: ClassVar[bool]
    left: LeftEvent
    right: RightEvent

    @property
    @abstractmethod
    def end(self) -> Point:
        """Returns end of the event."""

    @property
    @abstractmethod
    def original_end(self) -> Point:
        """Returns original end of the event."""

    @property
    @abstractmethod
    def original_start(self) -> Point:
        """Returns original start of the segment."""

    @abstractmethod
    def register_tangent(self, tangent: 'Event') -> None:
        """Registers new tangent to the event"""

    @property
    @abstractmethod
    def segments_ids(self) -> Set[int]:
        """Returns segments ids of the event."""

    @property
    @abstractmethod
    def start(self) -> Point:
        """Returns start of the event."""

    @property
    @abstractmethod
    def tangents(self) -> Sequence['Event']:
        """Returns tangents of the event."""


class LeftEvent(Event):
    """
    Represents a 'LeftEvent' which is a subtype of 'Event'.
    This class is specifically designed to handle events that are 'left' in nature in a geometrical context.
    It is associated with a 'RightEvent' to form a complementary pair.
    """

    @classmethod
    def from_segment(cls, segment: Segment, segment_id: int) -> 'LeftEvent':
        """
        Class method to create a LeftEvent from a given segment.

        Args:
            segment (Segment): The segment from which the LeftEvent is to be created.
            segment_id (int): Identifier for the segment.

        Returns:
            LeftEvent: An instance of LeftEvent created from the given segment.
        """
        # Ensure start and end points of the segment are sorted.
        start, end = to_sorted_pair(segment.start, segment.end)

        # Create a LeftEvent with start point and segment information.
        result = LeftEvent(start, None, start, {start: {end: {segment_id}}})

        # Associate a corresponding RightEvent with the LeftEvent.
        result._right = RightEvent(end, result, end)
        return result

    is_left = True  # Flag indicating this event is a 'left' event.

    @property
    def end(self) -> Point:
        """
        Property to get the end point of the event.

        Returns:
            Point: The end point of the associated RightEvent.
        """
        return self.right.start

    @property
    def original_start(self) -> Point:
        """
        Property to get the original start point of the event.

        Returns:
            Point: The original start point of the LeftEvent.
        """
        return self._original_start

    @property
    def original_end(self) -> Point:
        """
        Property to get the original end point of the event.

        Returns:
            Point: The original start point of the associated RightEvent.
        """
        return self.right.original_start

    @property
    def segments_ids(self) -> Set[int]:
        """
        Property to get the segment IDs associated with this event.

        Returns:
            Set[int]: A set of segment IDs associated with this event.
        """
        return self.parts_ids[self.start][self.end]

    @property
    def right(self) -> 'RightEvent':
        """
        Property to get the associated RightEvent.

        Returns:
            RightEvent: The associated RightEvent.

        Raises:
            AssertionError: If the RightEvent is not set.
        """
        result = self._right
        assert result is not None, self  # Ensure the RightEvent exists.
        return result

    @right.setter
    def right(self, value: 'RightEvent') -> None:
        """
        Setter for the RightEvent.

        Args:
            value (RightEvent): The RightEvent to be associated with this LeftEvent.
        """
        self._right = value

    @property
    def start(self) -> Point:
        """
        Property to get the start point of the event.

        Returns:
            Point: The start point of the LeftEvent.
        """
        return self._start

    @property
    def tangents(self) -> Sequence[Event]:
        """
        Property to get the tangents of the event.

        Returns:
            Sequence[Event]: A sequence of events that are tangents to this event.
        """
        return self._tangents

    _right: Optional[RightEvent]  # Optional right event, complementing the left event.

    __slots__ = ('parts_ids', '_original_start', '_relations_mask', '_right',
                 '_start', '_tangents')  # Optimization: predefined attributes for faster attribute access.

    def __init__(self,
                 start: Point,
                 right: Optional[RightEvent],
                 original_start: Point,
                 parts_ids: Dict[Point, Dict[Point, Set[int]]]) -> None:
        """
        Initialize an instance of the class.

        Args:
            start (Point): The starting point of the event.
            right (Optional[RightEvent]): The event on the right.
            original_start (Point): The original starting point.
            parts_ids (Dict[Point, Dict[Point, Set[int]]]): A dictionary 
                mapping points to parts and their corresponding IDs.

        The constructor sets up the initial state of the object by initializing
        various attributes related to the event's position, its relationships,
        and tangents, if any.
        """
        # Assigning the provided parameters to instance variables
        self._right, self.parts_ids, self._original_start, self._start = (
            right, parts_ids, original_start, start
        )
        self._relations_mask = 0  # Initialize relation mask to zero
        self._tangents = []  # Initialize the list to store tangent events

    __repr__ = recursive_repr()(generate_repr(__init__))

    def divide(self, point: Point) -> Tuple[RightEvent, LeftEvent]:
        """
        Divides the event at a given breakpoint and returns the tail events.

        Args:
            point (Point): The point at which to divide the event.

        Returns:
            Tuple[RightEvent, LeftEvent]: A tuple containing the new right 
                and left events resulting from the division.

        This method is responsible for splitting an event into two parts at a 
        specified point and updating the parts IDs to reflect this division.
        """
        # Retrieve IDs of the segments associated with this event
        segments_ids = self.segments_ids

        # Update parts IDs to include the new division points
        (self.parts_ids.setdefault(self.start, {})
         .setdefault(point, set()).update(segments_ids))
        (self.parts_ids.setdefault(point, {})
         .setdefault(self.end, set()).update(segments_ids))

        # Create new events for the divided segments
        point_to_end_event = self.right.left = LeftEvent(
                point, self.right, self.original_start, self.parts_ids
        )
        point_to_start_event = self._right = RightEvent(point, self,
                                                        self.original_end)

        return point_to_start_event, point_to_end_event

    def has_only_relations(self, *relations: Relation) -> bool:
        """
        Checks if the event only has specified relations.

        Args:
            relations (Relation): Variable number of relation types to check.

        Returns:
            bool: True if the event has only the specified relations, False otherwise.

        This method determines if an event is exclusively characterized by the 
        given relations by checking against its relations mask.
        """
        mask = self._relations_mask
        for relation in relations:
            mask &= ~(1 << relation)
        return not mask

    def merge_with(self, other: LeftEvent) -> None:
        """
        Merges the current event with another left event.

        Args:
            other (LeftEvent): The other left event to merge with.

        This method merges two events if they have the same start and end points,
        combining their parts IDs and registering the appropriate relations
        between them.
        """
        assert self.start == other.start and self.end == other.end
        full_relation = classify_overlap(
                other.original_start, other.original_end,
                self.original_start, self.original_end
        )
        self.register_relation(full_relation)
        other.register_relation(full_relation.complement)

        # Merge parts IDs from both events
        start, end = self.start, self.end
        self.parts_ids[start][end] = other.parts_ids[start][end] = (
                self.parts_ids[start][end] | other.parts_ids[start][end]
        )

    def register_tangent(self, tangent: Event) -> None:
        """
        Registers a tangent event.

        Args:
            tangent (Event): The tangent event to register.

        This method adds a tangent event to the list of tangents, asserting that 
        it starts at the same point as the current event.
        """
        assert self.start == tangent.start
        self._tangents.append(tangent)

    def register_relation(self, relation: Relation) -> None:
        """
        Registers a relation type to the event.

        Args:
            relation (Relation): The relation type to register.

        This method updates the relation mask to include the specified relation 
        type, thereby expanding the set of relations associated with this event.
        """
        self._relations_mask |= 1 << relation



class RightEvent(Event):
    """
    Represents a right event in a geometric context, extending the generic Event class.

    This class specifically deals with events on the right side of a point or segment.
    It holds references to its corresponding left event and maintains a list of tangent
    events, among other properties.
    """
    is_left = False  # Indicates that this is a right event

    @property
    def end(self) -> Point:
        """
        The end point of the right event.

        Returns:
            Point: The starting point of the left event, which serves as the end
                   point of this right event.

        This property method provides easy access to the end point of the right event,
        which is conceptually the start of the associated left event.
        """
        return self.left.start

    @property
    def left(self) -> LeftEvent:
        """
        The left event associated with this right event.

        Returns:
            LeftEvent: The left event corresponding to this right event.

        Raises:
            AssertionError: If the left event is not set.

        This property method allows for access to the left event linked with this right
        event, ensuring it has been properly set.
        """
        result = self._left
        assert result is not None, self  # Ensures the left event is not None
        return result

    @left.setter
    def left(self, value: LeftEvent) -> None:
        """
        Sets the left event associated with this right event.

        Args:
            value (LeftEvent): The left event to associate with this right event.

        This setter allows for the assignment of the left event to this right event,
        creating a link between the two.
        """
        self._left = value

    @property
    def original_end(self) -> Point:
        """
        The original end point of the right event.

        Returns:
            Point: The original start point of the left event, which is considered
                   the original end point of this right event.

        This property provides access to the original end point of the right event,
        which is derived from the left event's original start point.
        """
        return self.left.original_start

    @property
    def original_start(self) -> Point:
        """
        The original start point of the right event.

        Returns:
            Point: The original start point of this right event.

        This property provides access to the original start point of the right event,
        maintaining the consistency of the event's original position.
        """
        return self._original_start

    @property
    def segments_ids(self) -> Set[int]:
        """
        The IDs of the segments associated with this right event.

        Returns:
            Set[int]: A set of segment IDs associated with this right event.

        This property method provides a set of segment IDs that are linked to this
        right event, typically inherited from the associated left event.
        """
        return self.left.segments_ids

    @property
    def start(self) -> Point:
        """
        The start point of the right event.

        Returns:
            Point: The start point of this right event.

        This property method offers access to the start point of the right event,
        representing the point where the event begins.
        """
        return self._start

    @property
    def tangents(self) -> Sequence[Event]:
        """
        The tangent events associated with this right event.

        Returns:
            Sequence[Event]: A sequence of tangent events linked to this right event.

        This property method allows for the retrieval of a list of tangent events
        related to this right event, useful for geometric calculations.
        """
        return self._tangents

    # Optional attribute for a LeftEvent, initially not set
    _left: Optional[LeftEvent]

    # Declaring slots for memory optimization and attribute management
    __slots__ = '_left', '_original_start', '_start', '_tangents'

    def __init__(self,
                 start: Point,
                 left: Optional[LeftEvent],
                 original_start: Point) -> None:
        """
        Initialize a RightEvent instance.

        Args:
            start (Point): The start point of the right event.
            left (Optional[LeftEvent]): The associated left event, if any.
            original_start (Point): The original start point of the right event.

        This constructor initializes a RightEvent with its starting point,
        associated left event, and the original starting point. It also sets up
        an empty list for storing tangent events.
        """
        self._left, self._original_start, self._start = (left, original_start,
                                                         start)
        self._tangents = []  # Initialize an empty list for tangent events

    __repr__ = recursive_repr()(generate_repr(__init__))

    def register_tangent(self, tangent: 'Event') -> None:
        """
        Registers a tangent event to this right event.

        Args:
            tangent (Event): The tangent event to be registered.

        This method adds a tangent event to this right event's list of tangents.
        It checks that the start point of the tangent is the same as this right
        event's start point.

        Raises:
            AssertionError: If the start points do not match.
        """
        assert self.start == tangent.start  # Ensure start points match
        self._tangents.append(tangent)  # Add the tangent event to the list
