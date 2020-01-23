from typing import List

from hypothesis import given

from bentley_ottmann.base import edges_intersect
from bentley_ottmann.linear import (Segment,
                                    find_intersections)
from . import strategies


@given(strategies.segments_lists)
def test_basic(segments_list: List[Segment]) -> None:
    result = edges_intersect(segments_list)

    assert isinstance(result, bool)


@given(strategies.empty_segments_lists)
def test_base_case(segments_list: List[Segment]) -> None:
    result = edges_intersect(segments_list)

    assert not result


@given(strategies.non_empty_segments_lists)
def test_step(segments_list: List[Segment]) -> None:
    first_segment, *rest_segments = segments_list

    result = edges_intersect(rest_segments)
    next_result = edges_intersect(segments_list)

    assert next_result is (result
                           or (len(rest_segments) > 2
                               and bool(find_intersections(rest_segments[0],
                                                           rest_segments[-1])))
                           or any(find_intersections(first_segment, segment)
                                  for segment in rest_segments[1:-1]))


@given(strategies.segments_lists)
def test_reversed(segments_list: List[Segment]) -> None:
    result = edges_intersect(segments_list)

    assert result is edges_intersect(segments_list[::-1])
