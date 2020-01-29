from typing import List

from hypothesis import given

from bentley_ottmann.base import edges_intersect
from bentley_ottmann.linear import (Segment,
                                    find_intersections)
from tests.utils import (reverse_segment,
                         reverse_segment_coordinates)
from . import strategies


@given(strategies.edges_lists)
def test_basic(edges: List[Segment]) -> None:
    result = edges_intersect(edges)

    assert isinstance(result, bool)


@given(strategies.empty_edges_lists)
def test_base_case(edges: List[Segment]) -> None:
    result = edges_intersect(edges)

    assert not result


@given(strategies.non_empty_edges_lists)
def test_step(edges: List[Segment]) -> None:
    first_segment, *rest_edges = edges

    result = edges_intersect(rest_edges)
    next_result = edges_intersect(edges)

    assert next_result is (result
                           or (len(rest_edges) > 2
                               and bool(find_intersections(rest_edges[0],
                                                           rest_edges[-1])))
                           or any(find_intersections(first_segment, edge)
                                  for edge in rest_edges[1:-1]))


@given(strategies.edges_lists)
def test_reversed(edges: List[Segment]) -> None:
    result = edges_intersect(edges)

    assert result is edges_intersect(edges[::-1])


@given(strategies.edges_lists)
def test_reversed_endpoints(edges: List[Segment]) -> None:
    result = edges_intersect(edges)

    assert result is edges_intersect([reverse_segment(edge)
                                      for edge in edges])


@given(strategies.edges_lists)
def test_reversed_coordinates(edges: List[Segment]) -> None:
    result = edges_intersect(edges)

    assert result is edges_intersect([reverse_segment_coordinates(edge)
                                      for edge in edges])
