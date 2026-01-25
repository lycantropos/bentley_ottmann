from itertools import chain, combinations

import pytest
from ground.context import Context
from ground.enums import Relation
from ground.hints import Contour
from hypothesis import given

from bentley_ottmann.planar import contour_self_intersects
from tests.hints import ScalarT
from tests.utils import (
    pop_left_vertex,
    reverse_contour,
    reverse_contour_coordinates,
)

from .strategies import (
    contour_strategy,
    degenerate_contour_strategy,
    non_triangular_contour_strategy,
    triangular_contour_strategy,
)


@given(contour_strategy)
def test_basic(context: Context[ScalarT], contour: Contour[ScalarT]) -> None:
    result = contour_self_intersects(contour, context=context)

    assert isinstance(result, bool)


@given(triangular_contour_strategy)
def test_base_case(
    context: Context[ScalarT], contour: Contour[ScalarT]
) -> None:
    result = contour_self_intersects(contour, context=context)

    left_vertex, mid_vertex, right_vertex = sorted(contour.vertices)
    assert result is context.segment_contains_point(
        context.segment_cls(left_vertex, right_vertex), mid_vertex
    )


@given(non_triangular_contour_strategy)
def test_step(context: Context[ScalarT], contour: Contour[ScalarT]) -> None:
    first_vertex, rest_contour = pop_left_vertex(contour)
    rest_vertices = rest_contour.vertices

    result = contour_self_intersects(rest_contour, context=context)
    next_result = contour_self_intersects(contour, context=context)

    first_edge = context.segment_cls(first_vertex, rest_vertices[0])
    last_edge = context.segment_cls(rest_vertices[-1], first_vertex)
    rest_edges = context.contour_segments(rest_contour)
    overlap_relations = (
        Relation.COMPONENT,
        Relation.COMPOSITE,
        Relation.EQUAL,
        Relation.OVERLAP,
    )
    assert next_result is (
        (
            result
            and len(rest_vertices) > 2
            and (
                any(
                    (
                        context.segments_relation(
                            rest_edges[index], rest_edges[other_index]
                        )
                        is not Relation.DISJOINT
                    )
                    for index in range(len(rest_edges) - 1)
                    for other_index in chain(
                        range(index - 1), range(index + 2, len(rest_edges) - 1)
                    )
                )
                or any(
                    (
                        context.segments_relation(edge, other_edge)
                        in overlap_relations
                    )
                    for edge, other_edge in combinations(rest_edges[:-1], 2)
                )
            )
        )
        or any(
            (
                context.segments_relation(first_edge, edge)
                is not Relation.DISJOINT
            )
            for edge in rest_edges[1:-1]
        )
        or any(
            context.segments_relation(last_edge, edge) is not Relation.DISJOINT
            for edge in rest_edges[:-2]
        )
        or (
            len(rest_vertices) > 1
            and (
                context.segments_relation(first_edge, rest_edges[0])
                in overlap_relations
                or context.segments_relation(first_edge, last_edge)
                in overlap_relations
                or context.segments_relation(last_edge, rest_edges[0])
                in overlap_relations
            )
        )
    )


@given(contour_strategy)
def test_reversed(
    context: Context[ScalarT], contour: Contour[ScalarT]
) -> None:
    result = contour_self_intersects(contour, context=context)

    assert result is contour_self_intersects(
        reverse_contour(contour), context=context
    )


@given(contour_strategy)
def test_reversed_coordinates(
    context: Context[ScalarT], contour: Contour[ScalarT]
) -> None:
    result = contour_self_intersects(contour, context=context)

    assert result is contour_self_intersects(
        reverse_contour_coordinates(contour), context=context
    )


@given(degenerate_contour_strategy)
def test_degenerate_contour(
    context: Context[ScalarT], contour: Contour[ScalarT]
) -> None:
    with pytest.raises(ValueError):
        contour_self_intersects(contour, context=context)
