from functools import partial
from types import MappingProxyType
from typing import (Any,
                    Callable,
                    Dict,
                    Iterable,
                    Sequence,
                    Tuple,
                    TypeVar)

from ground.geometries import (to_contour_cls,
                               to_point_cls,
                               to_segment_cls)
from ground.hints import Coordinate
from hypothesis import strategies
from hypothesis.strategies import SearchStrategy

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Strategy = SearchStrategy
Contour = to_contour_cls()
Point = to_point_cls()
Segment = to_segment_cls()


def to_pairs(strategy: Strategy[Domain]) -> Strategy[Tuple[Domain, Domain]]:
    return strategies.tuples(strategy, strategy)


def identity(value: Domain) -> Domain:
    return value


def pack(function: Callable[..., Range]
         ) -> Callable[[Iterable[Domain]], Range]:
    return partial(apply, function)


def apply(function: Callable[..., Range],
          args: Iterable[Domain],
          kwargs: Dict[str, Domain] = MappingProxyType({})) -> Range:
    return function(*args, **kwargs)


def is_point(object_: Any) -> bool:
    return isinstance(object_, Point)


def contour_to_edges(contour: Contour) -> Sequence[Segment]:
    vertices = contour.vertices
    return [Segment(vertices[index], vertices[(index + 1) % len(vertices)])
            for index in range(len(vertices))]


def scale_segment(segment: Segment,
                  *,
                  scale: Coordinate) -> Segment:
    start, end = segment.start, segment.end
    start_x, start_y = start.x, start.y
    end_x, end_y = end.x, end.y
    return Segment(start, Point(start_x + scale * (end_x - start_x),
                                start_y + scale * (end_y - start_y)))


def reflect_segment(segment: Segment) -> Segment:
    return scale_segment(segment,
                         scale=-1)


def reverse_contour(contour: Contour) -> Contour:
    return Contour(contour.vertices[::-1])


def reverse_contour_coordinates(contour: Contour) -> Contour:
    return Contour([reverse_point_coordinates(vertex)
                    for vertex in contour.vertices])


def reverse_segment(segment: Segment) -> Segment:
    return Segment(segment.end, segment.start)


def reverse_segment_coordinates(segment: Segment) -> Segment:
    return Segment(reverse_point_coordinates(segment.start),
                   reverse_point_coordinates(segment.end))


def reverse_point_coordinates(point: Point) -> Point:
    return Point(point.y, point.x)
