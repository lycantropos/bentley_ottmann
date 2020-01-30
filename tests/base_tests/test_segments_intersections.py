from itertools import chain
from typing import List

from hypothesis import given

from bentley_ottmann.base import segments_intersections
from bentley_ottmann.linear import (Segment,
                                    find_intersections)
from tests.utils import is_point
from . import strategies


@given(strategies.segments_lists)
def test_basic(segments: List[Segment]) -> None:
    result = segments_intersections(segments)

    assert isinstance(result, dict)
    assert all(is_point(key)
               for key in result.keys())
    assert all(isinstance(value, set)
               for value in result.values())
    assert all(isinstance(element, tuple)
               for value in result.values()
               for element in value)
    assert all(len(element) == 2 and all(isinstance(coordinate, int)
                                         for coordinate in element)
               for value in result.values()
               for element in value)


@given(strategies.empty_segments_lists)
def test_base_case(segments: List[Segment]) -> None:
    result = segments_intersections(segments)

    assert not result


@given(strategies.non_empty_segments_lists)
def test_step(segments: List[Segment]) -> None:
    *rest_segments, last_segment = segments

    result = segments_intersections(rest_segments)
    next_result = segments_intersections(segments)

    assert (next_result.keys() ==
            (result.keys()
             | set(chain.from_iterable(find_intersections(last_segment,
                                                          segment)
                                       for segment in rest_segments))))
    assert all(segment_id < next_segment_id == len(segments) - 1
               for point, intersections in next_result.items()
               for segment_id, next_segment_id in (intersections
                                                   - result.get(point, set())))
    assert all(point in find_intersections(segments[segment_id],
                                           segments[next_segment_id])
               for point, intersections in next_result.items()
               for segment_id, next_segment_id in (intersections
                                                   - result.get(point, set())))
