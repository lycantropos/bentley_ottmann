from itertools import (chain,
                       combinations)

from hypothesis import given

from bentley_ottmann.core.linear import (SegmentsRelationship,
                                         find_intersections,
                                         to_segments_relationship)
from bentley_ottmann.core.point import (is_real_point,
                                        to_real_point)
from bentley_ottmann.hints import Contour
from bentley_ottmann.planar import edges_intersect
from tests.utils import (contour_to_segments,
                         reverse_point_coordinates)
from . import strategies


@given(strategies.vertices_lists)
def test_basic(contour: Contour) -> None:
    result = edges_intersect(contour)

    assert isinstance(result, bool)


@given(strategies.empty_vertices_lists)
def test_base_case(contour: Contour) -> None:
    result = edges_intersect(contour)

    assert not result


@given(strategies.non_empty_vertices_lists)
def test_step(contour: Contour) -> None:
    first_vertex, *rest_vertices = contour

    result = edges_intersect(rest_vertices)
    next_result = edges_intersect(contour)

    first_vertex_real, rest_vertices_real = (
        (first_vertex, rest_vertices)
        if is_real_point(first_vertex)
        else (to_real_point(first_vertex),
              [to_real_point(vertex) for vertex in rest_vertices]))
    first_edge, last_edge = ((first_vertex_real, rest_vertices_real[0]),
                             (rest_vertices_real[-1], first_vertex_real))
    rest_edges = contour_to_segments(rest_vertices_real)
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
def test_reversed(contour: Contour) -> None:
    result = edges_intersect(contour)

    assert result is edges_intersect(contour[::-1])


@given(strategies.vertices_lists)
def test_reversed_coordinates(contour: Contour) -> None:
    result = edges_intersect(contour)

    assert result is edges_intersect([reverse_point_coordinates(vertex)
                                      for vertex in contour])
