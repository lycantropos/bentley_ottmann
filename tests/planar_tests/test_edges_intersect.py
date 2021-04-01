from itertools import (chain,
                       combinations)

import pytest
from ground.base import (Context,
                         Relation)
from ground.hints import Contour
from hypothesis import given

from bentley_ottmann.planar import edges_intersect
from tests.utils import (contour_to_edges,
                         pop_left_vertex,
                         reverse_contour,
                         reverse_contour_coordinates)
from . import strategies


@given(strategies.contours)
def test_basic(contour: Contour) -> None:
    result = edges_intersect(contour)

    assert isinstance(result, bool)


@given(strategies.triangular_contours)
def test_base_case(context: Context, contour: Contour) -> None:
    result = edges_intersect(contour)

    left_vertex, mid_vertex, right_vertex = sorted(contour.vertices)
    assert result is context.segment_contains_point(left_vertex, right_vertex,
                                                    mid_vertex)


@given(strategies.non_triangular_contours)
def test_step(context: Context, contour: Contour) -> None:
    first_vertex, rest_contour = pop_left_vertex(contour)
    rest_vertices = rest_contour.vertices

    result = edges_intersect(rest_contour)
    next_result = edges_intersect(contour)

    first_edge_start, first_edge_end = first_vertex, rest_vertices[0]
    last_edge_start, last_edge_end = rest_vertices[-1], first_vertex
    rest_edges = contour_to_edges(rest_contour)
    overlap_relations = (Relation.COMPONENT, Relation.COMPOSITE,
                         Relation.EQUAL, Relation.OVERLAP)
    assert (next_result
            is (result
                and len(rest_vertices) > 2
                and (any(context.segments_relation(
                            rest_edges[index].start, rest_edges[index].end,
                            rest_edges[other_index].start,
                            rest_edges[other_index].end)
                         is not Relation.DISJOINT
                         for index in range(len(rest_edges) - 1)
                         for other_index
                         in chain(range(index - 1),
                                  range(index + 2, len(rest_edges) - 1)))
                     or any(context.segments_relation(edge.start, edge.end,
                                                      other_edge.start,
                                                      other_edge.end)
                            in overlap_relations
                            for edge, other_edge
                            in combinations(rest_edges[:-1], 2)))
                or any(context.segments_relation(first_edge_start,
                                                 first_edge_end, edge.start,
                                                 edge.end)
                       is not Relation.DISJOINT
                       for edge in rest_edges[1:-1])
                or any(context.segments_relation(last_edge_start,
                                                 last_edge_end, edge.start,
                                                 edge.end)
                       is not Relation.DISJOINT
                       for edge in rest_edges[:-2])
                or len(rest_vertices) > 1
                and (context.segments_relation(
                            first_edge_start, first_edge_end,
                            rest_edges[0].start, rest_edges[0].end)
                     in overlap_relations
                     or context.segments_relation(
                                    first_edge_start, first_edge_end,
                                    last_edge_start, last_edge_end)
                     in overlap_relations
                     or context.segments_relation(
                                    last_edge_start, last_edge_end,
                                    rest_edges[0].start, rest_edges[0].end)
                     in overlap_relations)))


@given(strategies.contours)
def test_reversed(contour: Contour) -> None:
    result = edges_intersect(contour)

    assert result is edges_intersect(reverse_contour(contour))


@given(strategies.contours)
def test_reversed_coordinates(contour: Contour) -> None:
    result = edges_intersect(contour)

    assert result is edges_intersect(reverse_contour_coordinates(contour))


@given(strategies.degenerate_contours)
def test_degenerate_contour(contour: Contour) -> None:
    with pytest.raises(ValueError):
        edges_intersect(contour)
