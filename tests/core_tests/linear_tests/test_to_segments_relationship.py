from typing import Tuple

from hypothesis import given

from bentley_ottmann.core.linear import (RealSegment,
                                         SegmentsRelationship,
                                         segments_relationship)
from tests.utils import (reflect_segment,
                         reverse_segment)
from . import strategies


@given(strategies.real_segments_pairs)
def test_basic(segments_pair: Tuple[RealSegment, RealSegment]) -> None:
    first_segment, second_segment = segments_pair

    result = segments_relationship(first_segment, second_segment)

    assert isinstance(result, SegmentsRelationship)


@given(strategies.real_segments_pairs)
def test_commutativity(segments_pair: Tuple[RealSegment, RealSegment]) -> None:
    first_segment, second_segment = segments_pair

    result = segments_relationship(first_segment, second_segment)

    assert result is segments_relationship(second_segment, first_segment)


@given(strategies.real_segments)
def test_self(segment: RealSegment) -> None:
    result = segments_relationship(segment, segment)

    assert result is SegmentsRelationship.OVERLAP


@given(strategies.real_segments)
def test_reversed(segment: RealSegment) -> None:
    result = segments_relationship(segment, reverse_segment(segment))

    assert result is SegmentsRelationship.OVERLAP


@given(strategies.real_segments)
def test_reflected(segment: RealSegment) -> None:
    result = segments_relationship(segment, reflect_segment(segment))

    assert result is SegmentsRelationship.CROSS
