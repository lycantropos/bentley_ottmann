from itertools import (chain,
                       combinations)
from typing import List

from hypothesis import given

from bentley_ottmann.base import (_vertices_to_edges,
                                  edges_intersect)
from bentley_ottmann.linear import (Segment, SegmentsRelationship,
                                    find_intersections,
                                    to_segments_relationship)
from bentley_ottmann.point import Point
from tests.utils import reverse_point_coordinates
from . import strategies


@given(strategies.vertices_lists)
def test_basic(vertices: List[Point]) -> None:
    result = edges_intersect(vertices)

    assert isinstance(result, bool)


@given(strategies.empty_vertices_lists)
def test_base_case(vertices: List[Point]) -> None:
    result = edges_intersect(vertices)

    assert not result


@given(strategies.non_empty_vertices_lists)
def test_step(vertices: List[Point]) -> None:
    first_vertex, *rest_vertices = vertices

    result = edges_intersect(rest_vertices)
    next_result = edges_intersect(vertices)

    first_edge, last_edge = (Segment(first_vertex, rest_vertices[0]),
                             Segment(rest_vertices[-1], first_vertex))
    rest_edges = _vertices_to_edges(rest_vertices)
    assert (next_result
            is (result
                and len(rest_vertices) > 2
                and (any(find_intersections(rest_edges[index],
                                            rest_edges[other_index])
                         for index in range(len(rest_edges) - 1)
                         for other_index in chain(
                            range(index - 1),
                            range(index + 2, len(rest_edges) - 1)))
                     or any(to_segments_relationship(edge, other_edge)
                            is SegmentsRelationship.OVERLAP
                            for edge, other_edge in combinations(
                                    rest_edges[:-1], 2)))
                or any(find_intersections(first_edge, edge)
                       for edge in rest_edges[1:-1])
                or any(find_intersections(last_edge, edge)
                       for edge in rest_edges[:-2])
                or len(rest_vertices) > 1
                and (to_segments_relationship(first_edge, rest_edges[0])
                     is SegmentsRelationship.OVERLAP
                     or to_segments_relationship(first_edge, last_edge)
                     is SegmentsRelationship.OVERLAP
                     or to_segments_relationship(last_edge, rest_edges[0])
                     is SegmentsRelationship.OVERLAP)))


@given(strategies.vertices_lists)
def test_reversed(vertices: List[Point]) -> None:
    result = edges_intersect(vertices)

    assert result is edges_intersect(vertices[::-1])


@given(strategies.vertices_lists)
def test_reversed_coordinates(vertices: List[Point]) -> None:
    result = edges_intersect(vertices)

    assert result is edges_intersect([reverse_point_coordinates(vertex)
                                      for vertex in vertices])
