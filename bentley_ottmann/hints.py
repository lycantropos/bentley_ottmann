from decimal import Decimal
from numbers import Real
from typing import (Sequence,
                    Tuple,
                    TypeVar)

Scalar = TypeVar('Scalar', Real, Decimal)
Point = Tuple[Scalar, Scalar]
Segment = Tuple[Point, Point]
Contour = Sequence[Point]
