from typing import List

import pytest
from ground.base import (Context,
                         Relation)
from ground.hints import Segment
from hypothesis import given

from bentley_ottmann.planar import segments_intersect
from tests.utils import (reverse_segment,
                         reverse_segments_coordinates)
from . import strategies


@given(strategies.segments_lists)
def test_basic(segments: List[Segment]) -> None:
    result = segments_intersect(segments)

    assert isinstance(result, bool)


@given(strategies.empty_segments_lists)
def test_base_case(segments: List[Segment]) -> None:
    result = segments_intersect(segments)

    assert not result


@given(strategies.non_empty_segments_lists)
def test_step(context: Context, segments: List[Segment]) -> None:
    first_segment, *rest_segments = segments

    result = segments_intersect(rest_segments)
    next_result = segments_intersect(segments)

    assert (next_result
            is (result
                or any(context.segments_relation(first_segment, segment)
                       is not Relation.DISJOINT
                       for segment in rest_segments)))


@given(strategies.segments_lists)
def test_reversed(segments: List[Segment]) -> None:
    result = segments_intersect(segments)

    assert result is segments_intersect(segments[::-1])


@given(strategies.segments_lists)
def test_reversed_endpoints(segments: List[Segment]) -> None:
    result = segments_intersect(segments)

    assert result is segments_intersect([reverse_segment(segment)
                                         for segment in segments])


@given(strategies.segments_lists)
def test_reversed_coordinates(segments: List[Segment]) -> None:
    result = segments_intersect(segments)

    assert result is segments_intersect(reverse_segments_coordinates(segments))


@given(strategies.degenerate_segments_lists)
def test_degenerate_segments(segments: List[Segment]) -> None:
    with pytest.raises(ValueError):
        segments_intersect(segments)
