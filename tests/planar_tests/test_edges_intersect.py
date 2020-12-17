from itertools import (chain,
                       combinations)

import pytest
from ground.linear import SegmentsRelationship
from hypothesis import given

from bentley_ottmann.planar import edges_intersect
from tests.hints import (SegmentContainmentChecker,
                         SegmentsIntersector,
                         SegmentsRelater)
from tests.utils import (Contour,
                         Segment,
                         contour_to_edges,
                         reverse_contour,
                         reverse_contour_coordinates)
from . import strategies


@given(strategies.contours)
def test_basic(contour: Contour) -> None:
    result = edges_intersect(contour)

    assert isinstance(result, bool)


@given(strategies.triangular_contours)
def test_base_case(segment_containment_checker: SegmentContainmentChecker,
                   contour: Contour) -> None:
    result = edges_intersect(contour)

    left_vertex, mid_vertex, right_vertex = sorted(contour.vertices)
    assert result is segment_containment_checker(left_vertex, right_vertex,
                                                 mid_vertex)


@given(strategies.non_triangular_rational_contours)
def test_step(segments_intersector: SegmentsIntersector,
              segments_relater: SegmentsRelater,
              contour: Contour) -> None:
    first_vertex, *rest_vertices = contour.vertices
    rest_contour = Contour(rest_vertices)

    result = edges_intersect(rest_contour)
    next_result = edges_intersect(contour)

    first_edge, last_edge = (Segment(first_vertex, rest_vertices[0]),
                             Segment(rest_vertices[-1], first_vertex))
    rest_edges = contour_to_edges(rest_contour)
    assert (next_result
            is (result
                and len(rest_vertices) > 2
                and (any(segments_intersector(rest_edges[index].start,
                                              rest_edges[index].end,
                                              rest_edges[other_index].start,
                                              rest_edges[other_index].end)
                         for index in range(len(rest_edges) - 1)
                         for other_index
                         in chain(range(index - 1),
                                  range(index + 2, len(rest_edges) - 1)))
                     or any(segments_relater(edge.start, edge.end,
                                             other_edge.start, other_edge.end)
                            is SegmentsRelationship.OVERLAP
                            for edge, other_edge
                            in combinations(rest_edges[:-1], 2)))
                or any(segments_intersector(first_edge.start, first_edge.end,
                                            edge.start, edge.end)
                       for edge in rest_edges[1:-1])
                or any(segments_intersector(last_edge.start, last_edge.end,
                                            edge.start, edge.end)
                       for edge in rest_edges[:-2])
                or len(rest_vertices) > 1
                and (segments_relater(first_edge.start, first_edge.end,
                                      rest_edges[0].start, rest_edges[0].end)
                     is SegmentsRelationship.OVERLAP
                     or segments_relater(first_edge.start, first_edge.end,
                                         last_edge.start, last_edge.end)
                     is SegmentsRelationship.OVERLAP
                     or segments_relater(last_edge.start, last_edge.end,
                                         rest_edges[0].start,
                                         rest_edges[0].end)
                     is SegmentsRelationship.OVERLAP)))


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
