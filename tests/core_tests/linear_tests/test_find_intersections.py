from typing import Tuple

from hypothesis import given

from bentley_ottmann.core.linear import (find_intersections)
from bentley_ottmann.hints import Segment
from tests.utils import (is_point,
                         reverse_segment)
from . import strategies


@given(strategies.segments_pairs)
def test_basic(segments_pair: Tuple[Segment, Segment]) -> None:
    first_segment, second_segment = segments_pair

    result = find_intersections(first_segment, second_segment)

    assert isinstance(result, tuple)
    assert all(is_point(element) for element in result)
    assert len(result) <= 2


@given(strategies.segments_pairs)
def test_commutativity(segments_pair: Tuple[Segment, Segment]) -> None:
    first_segment, second_segment = segments_pair

    result = find_intersections(first_segment, second_segment)

    assert result == find_intersections(second_segment, first_segment)


@given(strategies.segments)
def test_self(segment: Segment) -> None:
    result = find_intersections(segment, segment)

    assert result == tuple(sorted(segment))


@given(strategies.segments)
def test_reversed(segment: Segment) -> None:
    result = find_intersections(segment, reverse_segment(segment))

    assert result == tuple(sorted(segment))
