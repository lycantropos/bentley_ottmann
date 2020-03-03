from decimal import Decimal
from numbers import Real
from typing import (Sequence,
                    Tuple,
                    Type,
                    TypeVar)

Scalar = TypeVar('Scalar', Real, Decimal)
Base = Type[Scalar]
Point = Tuple[Scalar, Scalar]
Segment = Tuple[Point, Point]
Contour = Sequence[Point]
