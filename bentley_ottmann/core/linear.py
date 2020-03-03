from typing import (Tuple,
                    Union)

from robust.hints import Segment as RealSegment
from robust.linear import (SegmentsRelationship,
                           segments_intersection as find_intersection,
                           segments_relationship)

from bentley_ottmann.hints import (Base,
                                   Point,
                                   Segment)
from .point import (is_real_point,
                    to_rational_point,
                    to_real_point,
                    to_scalar_point)

RealSegment = RealSegment
SegmentsRelationship = SegmentsRelationship
segments_relationship = segments_relationship


def find_intersections(left: Segment,
                       right: Segment) -> Union[Tuple[()], Tuple[Point],
                                                Tuple[Point, Point]]:
    are_real_segments = is_real_segment(left)
    left_real, right_real = ((left, right)
                             if are_real_segments
                             else (to_real_segment(left),
                                   to_real_segment(right)))
    relationship = segments_relationship(left_real, right_real)
    if relationship is SegmentsRelationship.NONE:
        return ()
    elif relationship is SegmentsRelationship.CROSS:
        intersection_point = find_intersection(left_real, right_real)
        if not are_real_segments:
            intersection_point = to_scalar_point(intersection_point,
                                                 _to_segment_base(left))
        return intersection_point,
    else:
        _, first_intersection_point, second_intersection_point, _ = sorted(
                left + right)
        return first_intersection_point, second_intersection_point


def _to_segment_base(segment: Segment) -> Base:
    start, _ = segment
    start_x, _ = start
    return type(start_x)


def is_real_segment(segment: Segment) -> bool:
    start, _ = segment
    return is_real_point(start)


def to_rational_segment(segment: Segment) -> Segment:
    start, end = segment
    return to_rational_point(start), to_rational_point(end)


def to_real_segment(segment: Segment) -> Segment:
    start, end = segment
    return to_real_point(start), to_real_point(end)
