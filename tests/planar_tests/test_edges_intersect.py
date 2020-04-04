from itertools import (chain,
                       combinations)

from hypothesis import given

from bentley_ottmann.core.linear import (SegmentsRelationship,
                                         segments_intersections,
                                         segments_relationship)
from bentley_ottmann.hints import Contour
from bentley_ottmann.planar import edges_intersect
from tests.utils import (contour_to_segments,
                         reverse_point_coordinates)
from . import strategies


@given(strategies.contours)
def test_basic(contour: Contour) -> None:
    result = edges_intersect(contour)

    assert isinstance(result, bool)


@given(strategies.empty_contours)
def test_base_case(contour: Contour) -> None:
    result = edges_intersect(contour)

    assert not result


@given(strategies.non_empty_contours)
def test_step(contour: Contour) -> None:
    first_vertex, *rest_vertices = contour

    result = edges_intersect(rest_vertices)
    next_result = edges_intersect(contour)

    first_edge, last_edge = ((first_vertex, rest_vertices[0]),
                             (rest_vertices[-1], first_vertex))
    rest_edges = contour_to_segments(rest_vertices)
    assert (next_result
            is (result
                and len(rest_vertices) > 2
                and (any(segments_intersections(rest_edges[index],
                                                rest_edges[other_index])
                         for index in range(len(rest_edges) - 1)
                         for other_index in chain(
                            range(index - 1),
                            range(index + 2, len(rest_edges) - 1)))
                     or any(segments_relationship(edge, other_edge)
                            is SegmentsRelationship.OVERLAP
                            for edge, other_edge in combinations(
                                    rest_edges[:-1], 2)))
                or any(segments_intersections(first_edge, edge)
                       for edge in rest_edges[1:-1])
                or any(segments_intersections(last_edge, edge)
                       for edge in rest_edges[:-2])
                or len(rest_vertices) > 1
                and (segments_relationship(first_edge, rest_edges[0])
                     is SegmentsRelationship.OVERLAP
                     or segments_relationship(first_edge, last_edge)
                     is SegmentsRelationship.OVERLAP
                     or segments_relationship(last_edge, rest_edges[0])
                     is SegmentsRelationship.OVERLAP)))


@given(strategies.contours)
def test_reversed(contour: Contour) -> None:
    result = edges_intersect(contour)

    assert result is edges_intersect(contour[::-1])


@given(strategies.contours)
def test_reversed_coordinates(contour: Contour) -> None:
    result = edges_intersect(contour)

    assert result is edges_intersect([reverse_point_coordinates(vertex)
                                      for vertex in contour])
