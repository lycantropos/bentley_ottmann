from typing import Tuple

from hypothesis import given

from bentley_ottmann.linear import (Segment,
                                    find_intersections)
from bentley_ottmann.point import Point
from . import strategies


@given(strategies.segments_pairs)
def test_basic(segments_pair: Tuple[Segment, Segment]) -> None:
    first_segment, second_segment = segments_pair

    result = find_intersections(first_segment, second_segment)

    assert isinstance(result, tuple)
    assert all(isinstance(element, Point) for element in result)
    assert len(result) <= 2


@given(strategies.segments_pairs)
def test_commutativity(segments_pair: Tuple[Segment, Segment]) -> None:
    first_segment, second_segment = segments_pair

    result = find_intersections(first_segment, second_segment)

    assert result == find_intersections(second_segment, first_segment)
