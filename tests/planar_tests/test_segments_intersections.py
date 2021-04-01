from typing import List

import pytest
from ground.base import (Context,
                         Relation)
from ground.hints import Segment
from hypothesis import given

from bentley_ottmann.core.utils import to_sorted_pair
from bentley_ottmann.planar import segments_intersections
from tests.utils import (is_point,
                         reverse_point_coordinates,
                         reverse_segments_coordinates)
from . import strategies


@given(strategies.segments_lists)
def test_basic(segments: List[Segment]) -> None:
    result = segments_intersections(segments)

    assert isinstance(result, dict)
    assert all(isinstance(key, tuple)
               and all(isinstance(coordinate, int) for coordinate in key)
               for key in result.keys())
    assert all(isinstance(value, tuple)
               and all(is_point(coordinate) for coordinate in value)
               for value in result.values())
    assert all(len(key) == 2 for key in result.keys())
    assert all(1 <= len(value) <= 2 for value in result.values())


@given(strategies.empty_segments_lists)
def test_base_case(segments: List[Segment]) -> None:
    result = segments_intersections(segments)

    assert not result


@given(strategies.non_empty_segments_lists)
def test_step(context: Context,
              segments: List[Segment]) -> None:
    *rest_segments, last_segment = segments

    result = segments_intersections(rest_segments)
    next_result = segments_intersections(segments)

    assert (next_result.keys()
            == (result.keys()
                | {(index, len(segments) - 1)
                   for index, segment in enumerate(rest_segments)
                   if context.segments_relation(segment.start, segment.end,
                                                last_segment.start,
                                                last_segment.end)
                   is not Relation.DISJOINT}))
    assert result.items() <= next_result.items()
    assert all(segment_id < next_segment_id == len(segments) - 1
               for segment_id, next_segment_id in (next_result.keys()
                                                   - result.keys()))
    assert all(context.segments_intersection(segments[segment_id].start,
                                             segments[segment_id].end,
                                             segments[next_segment_id].start,
                                             segments[next_segment_id].end)
               == next_result[(segment_id, next_segment_id)][0]
               if len(next_result[(segment_id, next_segment_id)]) == 1
               else
               context.segments_intersection(segments[segment_id].start,
                                             segments[segment_id].end,
                                             segments[next_segment_id].start,
                                             segments[next_segment_id].end)
               not in (Relation.DISJOINT, Relation.TOUCH, Relation.CROSS)
               and (to_sorted_pair(*next_result[(segment_id, next_segment_id)])
                    == next_result[(segment_id, next_segment_id)])
               and all(context.segment_contains_point(
                       segments[segment_id].start, segments[segment_id].end,
                       point)
                       for point in next_result[(segment_id, next_segment_id)])
               and all(context.segment_contains_point(
                       segments[next_segment_id].start,
                       segments[next_segment_id].end, point)
                       for point in next_result[(segment_id, next_segment_id)])
               for segment_id, next_segment_id in (next_result.keys()
                                                   - result.keys()))
    assert all(context.segments_relation(segments[segment_id].start,
                                         segments[segment_id].end,
                                         segments[next_segment_id].start,
                                         segments[next_segment_id].end)
               is not Relation.DISJOINT
               for segment_id, next_segment_id in (next_result.keys()
                                                   - result.keys()))


@given(strategies.segments_lists)
def test_reversed_coordinates(segments: List[Segment]) -> None:
    result = segments_intersections(segments)

    reversed_result = segments_intersections(reverse_segments_coordinates(
            segments))
    assert result == {
        ids_pair: to_sorted_pair(reverse_point_coordinates(start),
                                 reverse_point_coordinates(end))
        for ids_pair, (start, end) in reversed_result.items()}


@given(strategies.degenerate_segments_lists)
def test_degenerate_segments(segments: List[Segment]) -> None:
    with pytest.raises(ValueError):
        segments_intersections(segments)
