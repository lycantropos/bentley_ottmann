from functools import partial
from types import MappingProxyType
from typing import (Callable,
                    Dict,
                    Iterable,
                    Tuple,
                    TypeVar)

from hypothesis import strategies
from hypothesis.strategies import SearchStrategy

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
