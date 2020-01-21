from fractions import Fraction
from typing import List

from hypothesis import given

from bentley_ottmann.base import segments_intersect
from bentley_ottmann.linear import Segment, find_intersections
from bentley_ottmann.point import Point
from . import strategies


@given(strategies.segments_lists)
def test_basic(segments_list: List[Segment]) -> None:
    result = segments_intersect(segments_list)

    assert isinstance(result, bool)


@given(strategies.empty_segments_lists)
def test_base_case(segments_list: List[Segment]) -> None:
    result = segments_intersect(segments_list)

    assert not result


@given(strategies.non_empty_segments_lists)
def test_step(segments_list: List[Segment]) -> None:
    first_segment, *rest_segments = segments_list

    result = segments_intersect(rest_segments)
    next_result = segments_intersect(segments_list)

    assert next_result is (result
                           or any(find_intersections(first_segment, segment)
                                  for segment in rest_segments))


@given(strategies.segments_lists)
def test_reversed(segments_list: List[Segment]) -> None:
    result = segments_intersect(segments_list)

    assert result is segments_intersect(segments_list[::-1])
