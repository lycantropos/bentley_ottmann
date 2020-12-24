from typing import Callable

from ground.core.hints import (QuaternaryPointFunction,
                               Range)
from ground.hints import Point

TernaryPointFunction = Callable[[Point, Point, Point], Range]
QuaternaryPointFunction = QuaternaryPointFunction
