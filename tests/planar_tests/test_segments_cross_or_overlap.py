from collections.abc import Sequence

import pytest
from ground.context import Context
from ground.enums import Relation
from ground.hints import Segment
from hypothesis import given

from bentley_ottmann.planar import segments_cross_or_overlap
from tests.hints import ScalarT
from tests.utils import reverse_segment, reverse_segments_coordinates

from .strategies import (
    degenerate_segment_sequence_strategy,
    empty_segment_sequence_strategy,
    non_empty_segment_sequence_strategy,
    segment_sequence_strategy,
)


@given(segment_sequence_strategy)
def test_basic(
    context: Context[ScalarT], segments: Sequence[Segment[ScalarT]]
) -> None:
    result = segments_cross_or_overlap(segments, context=context)

    assert isinstance(result, bool)


@given(empty_segment_sequence_strategy)
def test_base_case(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    result = segments_cross_or_overlap(segments, context=context)

    assert not result


@given(non_empty_segment_sequence_strategy)
def test_step(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    first_segment, *rest_segments = segments

    result = segments_cross_or_overlap(rest_segments, context=context)
    next_result = segments_cross_or_overlap(segments, context=context)

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


@given(segment_sequence_strategy)
def test_reversed(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    result = segments_cross_or_overlap(segments, context=context)

    assert result is segments_cross_or_overlap(segments[::-1], context=context)


@given(segment_sequence_strategy)
def test_reversed_endpoints(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    result = segments_cross_or_overlap(segments, context=context)

    assert result is segments_cross_or_overlap(
        [reverse_segment(segment) for segment in segments], context=context
    )


@given(segment_sequence_strategy)
def test_reversed_coordinates(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    result = segments_cross_or_overlap(segments, context=context)

    assert result is segments_cross_or_overlap(
        reverse_segments_coordinates(segments), context=context
    )


@given(degenerate_segment_sequence_strategy)
def test_degenerate_segments(
    context: Context[ScalarT], segments: list[Segment[ScalarT]]
) -> None:
    with pytest.raises(ValueError):
        segments_cross_or_overlap(segments, context=context)
