from typing import Tuple

from hypothesis import given

from bentley_ottmann.linear import (Segment,
                                    SegmentsRelationship,
                                    to_segments_relationship)
from tests.utils import reverse_segment
from . import strategies


@given(strategies.segments_pairs)
def test_basic(segments_pair: Tuple[Segment, Segment]) -> None:
    first_segment, second_segment = segments_pair

    result = to_segments_relationship(first_segment, second_segment)

    assert isinstance(result, SegmentsRelationship)


@given(strategies.segments_pairs)
def test_commutativity(segments_pair: Tuple[Segment, Segment]) -> None:
    first_segment, second_segment = segments_pair

    result = to_segments_relationship(first_segment, second_segment)

    assert result is to_segments_relationship(second_segment, first_segment)


@given(strategies.segments)
def test_self(segment: Segment) -> None:
    result = to_segments_relationship(segment, segment)

    assert result is SegmentsRelationship.OVERLAP


@given(strategies.segments)
def test_reversed(segment: Segment) -> None:
    result = to_segments_relationship(segment, reverse_segment(segment))

    assert result is SegmentsRelationship.OVERLAP
