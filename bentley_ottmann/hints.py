from numbers import Real
from typing import (Sequence,
                    Tuple,
                    Type)

Coordinate = Real
Base = Type[Coordinate]
Point = Tuple[Coordinate, Coordinate]
Segment = Tuple[Point, Point]
Contour = Sequence[Point]
