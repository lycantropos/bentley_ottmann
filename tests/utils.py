from collections.abc import Callable, Iterable, Mapping, Sequence
from fractions import Fraction
from functools import partial
from types import MappingProxyType
from typing import Any, TypeVar

from ground.context import get_context, set_context
from ground.hints import Contour, Point, Segment
from hypothesis import strategies
from hypothesis.strategies import SearchStrategy

from tests.hints import ScalarT

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Strategy = SearchStrategy
context = get_context().replace(coordinate_factory=Fraction)
set_context(context)

MAX_SCALAR = 10**20
MIN_SCALAR = -MAX_SCALAR


def to_pairs(strategy: Strategy[Domain], /) -> Strategy[tuple[Domain, Domain]]:
    return strategies.tuples(strategy, strategy)


def identity(value: Domain, /) -> Domain:
    return value


def pack(
    function: Callable[..., Range], /
) -> Callable[[Iterable[Any]], Range]:
    return partial(apply, function)


def apply(
    function: Callable[..., Range],
    args: Iterable[Domain],
    kwargs: Mapping[str, Domain] = MappingProxyType({}),
    /,
) -> Range:
    return function(*args, **kwargs)


def pop_left_vertex(
    contour: Contour[ScalarT], /
) -> tuple[Point[ScalarT], Contour[ScalarT]]:
    first_vertex, *rest_vertices = contour.vertices
    rest_contour = type(contour)(rest_vertices)
    return first_vertex, rest_contour


def reflect_segment(segment: Segment[ScalarT], /) -> Segment[ScalarT]:
    return scale_segment(segment, scale=-1)


def reverse_contour(contour: Contour[ScalarT], /) -> Contour[ScalarT]:
    return type(contour)(contour.vertices[::-1])


def reverse_contour_coordinates(
    contour: Contour[ScalarT], /
) -> Contour[ScalarT]:
    return type(contour)(
        [reverse_point_coordinates(vertex) for vertex in contour.vertices]
    )


def reverse_segment(segment: Segment[ScalarT], /) -> Segment[ScalarT]:
    return type(segment)(segment.end, segment.start)


def reverse_segment_coordinates(
    segment: Segment[ScalarT], /
) -> Segment[ScalarT]:
    return type(segment)(
        reverse_point_coordinates(segment.start),
        reverse_point_coordinates(segment.end),
    )


def reverse_segments_coordinates(
    segments: Sequence[Segment[ScalarT]], /
) -> Sequence[Segment[ScalarT]]:
    return [reverse_segment_coordinates(segment) for segment in segments]


def reverse_point_coordinates(point: Point[ScalarT], /) -> Point[ScalarT]:
    return type(point)(point.y, point.x)


def scale_segment(
    segment: Segment[ScalarT], /, *, scale: int
) -> Segment[ScalarT]:
    start, end = segment.start, segment.end
    start_x, start_y = start.x, start.y
    end_x, end_y = end.x, end.y
    return type(segment)(
        start,
        context.point_cls(
            start_x + context.coordinate_factory(scale) * (end_x - start_x),
            start_y + context.coordinate_factory(scale) * (end_y - start_y),
        ),
    )
