import pytest
from ground.context import Context
from ground.enums import Relation
from ground.hints import Segment
from hypothesis import given

from bentley_ottmann.planar import segments_cross_or_overlap
from tests.hints import ScalarT
from tests.utils import reverse_segment, reverse_segments_coordinates

from . import strategies


@given(strategies.segments_lists)
def test_basic(segments: list[Segment[ScalarT]]) -> None:
    result = segments_cross_or_overlap(segments)

    assert isinstance(result, bool)


@given(strategies.empty_segments_lists)
def test_base_case(segments: list[Segment[ScalarT]]) -> None:
    result = segments_cross_or_overlap(segments)

    assert not result


@given(strategies.non_empty_segments_lists)
def test_step(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    first_segment, *rest_segments = segments

    result = segments_cross_or_overlap(rest_segments)
    next_result = segments_cross_or_overlap(segments)

    assert next_result is (
        result
        or any(
            context.segments_relation(first_segment, segment)
            in (
                Relation.COMPONENT,
                Relation.COMPOSITE,
                Relation.CROSS,
                Relation.EQUAL,
                Relation.OVERLAP,
            )
            for segment in rest_segments
        )
    )


@given(strategies.segments_lists)
def test_reversed(segments: list[Segment[ScalarT]]) -> None:
    result = segments_cross_or_overlap(segments)

    assert result is segments_cross_or_overlap(segments[::-1])


@given(strategies.segments_lists)
def test_reversed_endpoints(segments: list[Segment[ScalarT]]) -> None:
    result = segments_cross_or_overlap(segments)

    assert result is segments_cross_or_overlap(
        [reverse_segment(segment) for segment in segments]
    )


@given(strategies.segments_lists)
def test_reversed_coordinates(segments: list[Segment[ScalarT]]) -> None:
    result = segments_cross_or_overlap(segments)

    assert result is segments_cross_or_overlap(
        reverse_segments_coordinates(segments)
    )


@given(strategies.degenerate_segments_lists)
def test_degenerate_segments(segments: list[Segment[ScalarT]]) -> None:
    with pytest.raises(ValueError):
        segments_cross_or_overlap(segments)
