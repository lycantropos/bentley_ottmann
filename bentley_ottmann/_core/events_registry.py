from __future__ import annotations

from typing import Generic, TYPE_CHECKING

from dendroid import red_black
from ground import hints
from ground.enums import Orientation
from prioq.base import PriorityQueue

from .event import (
    Event,
    is_event_left,
    segment_id_to_left_event,
    segment_id_to_right_event,
)
from .events_queue_key import EventsQueueKey
from .hints import ScalarT
from .sweep_line_key import SweepLineKey
from .utils import to_sorted_pair

if TYPE_CHECKING:
    from collections.abc import Iterator, Sequence

    from dendroid.hints import KeyedSet

    from .hints import Orienteer, SegmentsIntersector


class EventsRegistry(Generic[ScalarT]):
    @classmethod
    def from_segments(
        cls,
        segments: Sequence[hints.Segment[ScalarT]],
        orienteer: Orienteer[ScalarT],
        segments_intersector: SegmentsIntersector[ScalarT],
        /,
        *,
        unique: bool,
    ) -> EventsRegistry[ScalarT]:
        result = cls(orienteer, segments_intersector, unique)
        for segment_id, segment in enumerate(segments):
            left_event = segment_id_to_left_event(segment_id)
            right_event = segment_id_to_right_event(segment_id)
            start, end = to_sorted_pair(segment.start, segment.end)
            if start == end:
                raise ValueError(
                    'Degenerate segment found '
                    f'with both endpoints being: {start}.'
                )
            result._endpoints.append(start)
            result._endpoints.append(end)
            result._opposites.append(right_event)
            result._opposites.append(left_event)
            result._push(left_event)
            result._push(right_event)
        result._min_collinear_segments_ids = list(range(len(segments)))
        result._segments_ids = list(range(len(segments)))
        return result

    @property
    def unique(self, /) -> bool:
        return self._unique

    def are_collinear(
        self, first_segment_id: int, second_segment_id: int, /
    ) -> bool:
        return self._to_min_collinear_segment_id(
            first_segment_id
        ) == self._to_min_collinear_segment_id(second_segment_id)

    def to_event_end(self, event: Event, /) -> hints.Point[ScalarT]:
        return self.to_event_start(self._to_opposite_event(event))

    def to_event_segment_id(self, event: Event, /) -> int:
        return self._to_left_event_segment_id(
            event if is_event_left(event) else self._to_opposite_event(event)
        )

    def to_event_start(self, event: Event, /) -> hints.Point[ScalarT]:
        return self._endpoints[event]

    def to_segment_end(self, segment_id: int, /) -> hints.Point[ScalarT]:
        return self.to_event_start(segment_id_to_right_event(segment_id))

    def to_segment_start(self, segment_id: int, /) -> hints.Point[ScalarT]:
        return self.to_event_start(segment_id_to_left_event(segment_id))

    __slots__ = (
        '_endpoints',
        '_events_queue_data',
        '_min_collinear_segments_ids',
        '_opposites',
        '_orienteer',
        '_segments_ids',
        '_segments_intersector',
        '_sweep_line_data',
        '_unique',
    )

    def __init__(
        self,
        orienteer: Orienteer[ScalarT],
        segments_intersector: SegmentsIntersector[ScalarT],
        unique: bool,  # noqa: FBT001
        /,
    ) -> None:
        self._orienteer, self._segments_intersector, self._unique = (
            orienteer,
            segments_intersector,
            unique,
        )
        self._opposites: list[Event] = []
        self._endpoints: list[hints.Point[ScalarT]] = []
        self._segments_ids: list[int] = []
        self._min_collinear_segments_ids: list[int] = []
        self._events_queue_data: PriorityQueue[
            EventsQueueKey[ScalarT], Event
        ] = PriorityQueue(
            key=lambda event: EventsQueueKey(
                self._endpoints, self._opposites, event
            )
        )
        self._sweep_line_data: KeyedSet[SweepLineKey[ScalarT], Event] = (
            red_black.set_(key=self._event_to_sweep_line_key)
        )

    def _event_to_sweep_line_key(
        self, event: Event, /
    ) -> SweepLineKey[ScalarT]:
        return SweepLineKey(
            self._endpoints, self._opposites, event, self._orienteer
        )

    def __bool__(self, /) -> bool:
        return bool(self._events_queue_data)

    def __iter__(self, /) -> Iterator[Event]:
        while self:
            event = self._pop()
            if is_event_left(event):
                equal_segment_event = self._find(event)
                if equal_segment_event is None:
                    self._add(event)
                    below_event = self._below(event)
                    if below_event is not None:
                        self._detect_intersection(below_event, event)
                    above_event = self._above(event)
                    if above_event is not None:
                        self._detect_intersection(event, above_event)
                    yield event
                else:
                    self._merge_equal_segment_events(
                        equal_segment_event, event
                    )
                    if not self.unique:
                        yield event
            else:
                event_opposite = self._to_opposite_event(event)
                equal_segment_event = self._find(event_opposite)
                if equal_segment_event is not None:
                    above_event, below_event = (
                        self._above(equal_segment_event),
                        self._below(equal_segment_event),
                    )
                    self._remove(equal_segment_event)
                    if below_event is not None and above_event is not None:
                        self._detect_intersection(below_event, above_event)
                    if event != equal_segment_event:
                        self._merge_equal_segment_events(
                            equal_segment_event, event_opposite
                        )
                    yield event
                elif not self.unique:
                    yield event

    def _above(self, event: Event, /) -> Event | None:
        assert is_event_left(event)
        try:
            return self._sweep_line_data.next(event)
        except ValueError:
            return None

    def _add(self, event: Event, /) -> None:
        assert is_event_left(event)
        self._sweep_line_data.add(event)

    def _below(self, event: Event, /) -> Event | None:
        assert is_event_left(event)
        try:
            return self._sweep_line_data.prev(event)
        except ValueError:
            return None

    def _detect_intersection(
        self, below_event: Event, event: Event, /
    ) -> None:
        event_start = self.to_event_start(event)
        event_end = self.to_event_end(event)
        below_event_start = self.to_event_start(below_event)
        below_event_end = self.to_event_end(below_event)
        event_start_orientation = self._orienteer(
            below_event_end, below_event_start, event_start
        )
        event_end_orientation = self._orienteer(
            below_event_end, below_event_start, event_end
        )
        if event_start_orientation is event_end_orientation:
            if event_start_orientation is Orientation.COLLINEAR:
                if event_start == below_event_start:
                    assert event_end != below_event_end, (
                        event_start,
                        event_end,
                        below_event_start,
                        below_event_end,
                    )
                    max_end_event, min_end_event = (
                        (below_event, event)
                        if event_end < below_event_end
                        else (event, below_event)
                    )
                    self._remove(max_end_event)
                    min_end = self.to_event_end(min_end_event)
                    _, min_end_max_end_event = self._divide(
                        max_end_event, min_end
                    )
                    self._push(min_end_max_end_event)
                    self._merge_equal_segment_events(event, below_event)
                elif event_end == below_event_end:
                    max_start_event, min_start_event = (
                        (below_event, event)
                        if event_start < below_event_start
                        else (event, below_event)
                    )
                    max_start = self.to_event_start(max_start_event)
                    (max_start_to_min_start_event, max_start_to_end_event) = (
                        self._divide(min_start_event, max_start)
                    )
                    self._push(max_start_to_min_start_event)
                    self._merge_equal_segment_events(
                        max_start_event, max_start_to_end_event
                    )
                elif below_event_start < event_start < below_event_end:
                    if event_end < below_event_end:
                        self._divide_event_by_mid_segment_event_endpoints(
                            below_event, event, event_start, event_end
                        )
                    else:
                        max_start, min_end = event_start, below_event_end
                        self._divide_overlapping_events(
                            below_event, event, max_start, min_end
                        )
                elif event_start < below_event_start < event_end:
                    if below_event_end < event_end:
                        self._divide_event_by_mid_segment_event_endpoints(
                            event,
                            below_event,
                            below_event_start,
                            below_event_end,
                        )
                    else:
                        max_start, min_end = below_event_start, event_end
                        self._divide_overlapping_events(
                            event, below_event, max_start, min_end
                        )
        elif event_start_orientation is Orientation.COLLINEAR:
            if below_event_start < event_start < below_event_end:
                point = event_start
                self._divide_event_by_midpoint(below_event, point)
        elif event_end_orientation is Orientation.COLLINEAR:
            if below_event_start < event_end < below_event_end:
                point = event_end
                self._divide_event_by_midpoint(below_event, point)
        else:
            below_event_start_orientation = self._orienteer(
                event_start, event_end, below_event_start
            )
            below_event_end_orientation = self._orienteer(
                event_start, event_end, below_event_end
            )
            if below_event_start_orientation is Orientation.COLLINEAR:
                assert below_event_end_orientation is not Orientation.COLLINEAR
                if event_start < below_event_start < event_end:
                    point = below_event_start
                    self._divide_event_by_midpoint_checking_above(event, point)
            elif below_event_end_orientation is Orientation.COLLINEAR:
                if event_start < below_event_end < event_end:
                    point = below_event_end
                    self._divide_event_by_midpoint_checking_above(event, point)
            elif (
                below_event_start_orientation
                is not below_event_end_orientation
            ):
                cross_point = self._segments_intersector(
                    event_start, event_end, below_event_start, below_event_end
                )
                if below_event_start < cross_point < below_event_end:
                    self._divide_event_by_midpoint(below_event, cross_point)
                if event_start < cross_point < event_end:
                    self._divide_event_by_midpoint_checking_above(
                        event, cross_point
                    )

    def _divide(
        self, event: Event, mid_point: hints.Point[ScalarT], /
    ) -> tuple[Event, Event]:
        assert is_event_left(event)
        opposite_event = self._to_opposite_event(event)
        mid_point_to_event_end_event = Event(len(self._endpoints))
        self._segments_ids.append(self._to_left_event_segment_id(event))
        self._endpoints.append(mid_point)
        self._opposites.append(opposite_event)
        self._opposites[opposite_event] = mid_point_to_event_end_event
        mid_point_to_event_start_event = Event(len(self._endpoints))
        self._endpoints.append(mid_point)
        self._opposites.append(event)
        self._opposites[event] = mid_point_to_event_start_event
        return mid_point_to_event_start_event, mid_point_to_event_end_event

    def _divide_event_by_mid_segment_event_endpoints(
        self,
        event: Event,
        mid_segment_event: Event,
        mid_segment_event_start: hints.Point[ScalarT],
        mid_segment_event_end: hints.Point[ScalarT],
        /,
    ) -> None:
        self._divide_event_by_midpoint(event, mid_segment_event_end)
        (
            mid_segment_event_start_to_event_start_event,
            min_segment_event_start_to_min_segment_event_end_event,
        ) = self._divide(event, mid_segment_event_start)
        self._push(mid_segment_event_start_to_event_start_event)
        self._merge_equal_segment_events(
            mid_segment_event,
            min_segment_event_start_to_min_segment_event_end_event,
        )

    def _divide_event_by_midpoint(
        self, event: Event, point: hints.Point[ScalarT], /
    ) -> None:
        point_to_event_start_event, point_to_event_end_event = self._divide(
            event, point
        )
        self._push(point_to_event_start_event)
        self._push(point_to_event_end_event)

    def _divide_event_by_midpoint_checking_above(
        self, event: Event, point: hints.Point[ScalarT], /
    ) -> None:
        above_event = self._above(event)
        if above_event is not None and (
            self.to_event_start(above_event) == self.to_event_start(event)
            and self.to_event_end(above_event) == point
        ):
            self._remove(above_event)
            self._divide_event_by_midpoint(event, point)
            self._merge_equal_segment_events(event, above_event)
            return
        self._divide_event_by_midpoint(event, point)

    def _divide_overlapping_events(
        self,
        min_start_event: Event,
        max_start_event: Event,
        max_start: hints.Point[ScalarT],
        min_end: hints.Point[ScalarT],
        /,
    ) -> None:
        self._divide_event_by_midpoint(max_start_event, min_end)
        (max_start_to_min_start_event, max_start_to_min_end_event) = (
            self._divide(min_start_event, max_start)
        )
        self._push(max_start_to_min_start_event)
        self._merge_equal_segment_events(
            max_start_event, max_start_to_min_end_event
        )

    def _find(self, event: Event, /) -> Event | None:
        assert is_event_left(event)
        try:
            candidate = self._sweep_line_data.floor(event)
        except ValueError:
            return None
        else:
            return (
                candidate
                if (
                    (
                        self.to_event_start(candidate)
                        == self.to_event_start(event)
                    )
                    and (
                        self.to_event_end(candidate)
                        == self.to_event_end(event)
                    )
                )
                else None
            )

    def _merge_equal_segment_events(
        self, first: Event, second: Event, /
    ) -> None:
        first_segment_id = self._to_left_event_segment_id(first)
        second_segment_id = self._to_left_event_segment_id(second)
        first_min_collinear_segment_id = self._min_collinear_segments_ids[
            first_segment_id
        ]
        second_min_collinear_segment_id = self._min_collinear_segments_ids[
            second_segment_id
        ]
        min_collinear_segment_id = min(
            first_min_collinear_segment_id, second_min_collinear_segment_id
        )
        self._min_collinear_segments_ids[first_segment_id] = (
            min_collinear_segment_id
        )
        self._min_collinear_segments_ids[second_segment_id] = (
            min_collinear_segment_id
        )
        self._min_collinear_segments_ids[first_min_collinear_segment_id] = (
            min_collinear_segment_id
        )
        self._min_collinear_segments_ids[second_min_collinear_segment_id] = (
            min_collinear_segment_id
        )

    def _pop(self, /) -> Event:
        return self._events_queue_data.pop()

    def _push(self, event: Event, /) -> None:
        self._events_queue_data.push(event)

    def _remove(self, event: Event, /) -> None:
        assert is_event_left(event)
        self._sweep_line_data.remove(event)

    def _to_left_event_segment_id(self, event: Event, /) -> int:
        assert is_event_left(event)
        return self._segments_ids[event // 2]

    def _to_min_collinear_segment_id(self, segment_id: int, /) -> int:
        candidate = segment_id
        iterations_count = 0
        while self._min_collinear_segments_ids[candidate] != candidate:
            candidate = self._min_collinear_segments_ids[candidate]
            iterations_count += 1
        assert iterations_count <= (
            len(self._segments_ids).bit_length() - 1
        ), (iterations_count, self._min_collinear_segments_ids)
        return candidate

    def _to_opposite_event(self, event: Event, /) -> Event:
        return self._opposites[event]
