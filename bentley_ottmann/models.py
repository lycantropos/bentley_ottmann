from typing import (Generic,
                    TypeVar)

Domain = TypeVar('Domain')


class Pair(tuple, Generic[Domain]):
    def __new__(cls, first: Domain, second: Domain) -> 'Pair':
        return super().__new__(cls, (first, second))
