from typing import Tuple

from ground.core.hints import (QuaternaryPointFunction,
                               TernaryPointFunction)
from ground.hints import Point
from ground.linear import SegmentsRelationship

SegmentContainmentChecker = TernaryPointFunction[bool]
SegmentsIntersector = QuaternaryPointFunction[Tuple[Point, ...]]
SegmentsRelater = QuaternaryPointFunction[SegmentsRelationship]
