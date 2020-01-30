from functools import partial
from numbers import Number
from types import MappingProxyType
from typing import (Any,
                    Callable,
                    Dict,
                    Hashable,
                    Iterable,
                    Tuple,
                    TypeVar)

from hypothesis import strategies
from hypothesis.strategies import SearchStrategy

from bentley_ottmann.linear import Segment
from bentley_ottmann.point import Point

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


def all_unique(values: Iterable[Hashable]) -> bool:
    seen = set()
    seen_add = seen.add
    for value in values:
        if value in seen:
            return False
        else:
            seen_add(value)
    return True


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
