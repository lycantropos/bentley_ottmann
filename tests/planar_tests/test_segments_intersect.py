import pytest
from ground.context import Context
from ground.enums import Relation
from ground.hints import Segment
from hypothesis import given

from bentley_ottmann.planar import segments_intersect
from tests.hints import ScalarT
from tests.utils import reverse_segment, reverse_segments_coordinates

from . import strategies


@given(strategies.segments_lists)
def test_basic(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    result = segments_intersect(segments, context=context)

    assert isinstance(result, bool)


@given(strategies.empty_segments_lists)
def test_base_case(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    result = segments_intersect(segments, context=context)

    assert not result


@given(strategies.non_empty_segments_lists)
def test_step(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    first_segment, *rest_segments = segments

    result = segments_intersect(rest_segments, context=context)
    next_result = segments_intersect(segments, context=context)

    assert next_result is (
        result
        or any(
            context.segments_relation(first_segment, segment)
            is not Relation.DISJOINT
            for segment in rest_segments
        )
    )


@given(strategies.segments_lists)
def test_reversed(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    result = segments_intersect(segments, context=context)

    assert result is segments_intersect(segments[::-1], context=context)


@given(strategies.segments_lists)
def test_reversed_endpoints(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    result = segments_intersect(segments, context=context)

    assert result is segments_intersect(
        [reverse_segment(segment) for segment in segments], context=context
    )


@given(strategies.segments_lists)
def test_reversed_coordinates(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    result = segments_intersect(segments, context=context)

    assert result is segments_intersect(
        reverse_segments_coordinates(segments), context=context
    )


@given(strategies.degenerate_segments_lists)
def test_degenerate_segments(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    with pytest.raises(ValueError):
        segments_intersect(segments, context=context)
