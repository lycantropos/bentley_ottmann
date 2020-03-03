from functools import partial
from numbers import Number
from types import MappingProxyType
from typing import (Any,
                    Callable,
                    Dict,
                    Iterable,
                    Sequence,
                    Tuple,
                    TypeVar)

from hypothesis import strategies
from hypothesis.strategies import SearchStrategy

from bentley_ottmann.hints import (Contour,
                                   Point,
                                   Scalar,
                                   Segment)

Domain = TypeVar('Domain')
Range = TypeVar('Range')
Strategy = SearchStrategy


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


def scale_segment(segment: Segment,
                  *,
                  scale: Scalar) -> Segment:
    start, end = segment
    start_x, start_y = start
    end_x, end_y = end
    return (start, (start_x + scale * (end_x - start_x),
                    start_y + scale * (end_y - start_y)))


def reflect_segment(segment: Segment) -> Segment:
    return scale_segment(segment,
                         scale=-1)


def reverse_segment(segment: Segment) -> Segment:
    start, end = segment
    return end, start


def reverse_segment_coordinates(segment: Segment) -> Segment:
    start, end = segment
    return (reverse_point_coordinates(start),
            reverse_point_coordinates(end))


def reverse_point_coordinates(point: Point) -> Point:
    x, y = point
    return y, x


def is_point(object_: Any) -> bool:
    return (isinstance(object_, tuple)
            and len(object_) == 2
            and all(isinstance(coordinate, Number)
                    for coordinate in object_))


def contour_to_segments(contour: Contour) -> Sequence[Segment]:
    return [(contour[index], contour[(index + 1) % len(contour)])
            for index in range(len(contour))]
