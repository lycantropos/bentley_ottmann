from enum import (IntEnum,
                  unique)
from fractions import Fraction
from numbers import Real
from typing import (NamedTuple,
                    Tuple,
                    Union)

from robust import parallelogram

from .angular import (AngleKind,
                      Orientation,
                      to_angle_kind,
                      to_orientation)
from .point import (Point,
                    _to_rational_point,
                    _to_real_point,
                    _to_scalar_point)

Segment = NamedTuple('Segment', [('start', Point), ('end', Point)])


@unique
class SegmentsRelationship(IntEnum):
    NONE = 0
    CROSS = 1
    OVERLAP = 2


def to_segments_relationship(left: Segment,
                             right: Segment) -> SegmentsRelationship:
    if left == right:
        return SegmentsRelationship.OVERLAP
    left_start, left_end = left
    right_start, right_end = right
    left_start_orientation = point_orientation_with_segment(left_start, right)
    left_end_orientation = point_orientation_with_segment(left_end, right)
    if (left_start_orientation is Orientation.COLLINEAR
            and _point_in_segment(left_start, right)):
        if left_end_orientation is Orientation.COLLINEAR:
            if left_start == right_start:
                if (to_angle_kind(left_end, left_start, right_end)
                        is AngleKind.ACUTE):
                    return SegmentsRelationship.OVERLAP
                else:
                    return SegmentsRelationship.CROSS
            elif left_start == right_end:
                if (to_angle_kind(left_end, left_start, right_start)
                        is AngleKind.ACUTE):
                    return SegmentsRelationship.OVERLAP
                else:
                    return SegmentsRelationship.CROSS
            else:
                return SegmentsRelationship.OVERLAP
        else:
            return SegmentsRelationship.CROSS
    elif (left_end_orientation is Orientation.COLLINEAR
          and _point_in_segment(left_end, right)):
        if left_start_orientation is Orientation.COLLINEAR:
            if left_end == right_start:
                if (to_angle_kind(left_start, left_end, right_end)
                        is AngleKind.ACUTE):
                    return SegmentsRelationship.OVERLAP
                else:
                    return SegmentsRelationship.CROSS
            elif left_end == right_end:
                if (to_angle_kind(left_start, left_end, right_start)
                        is AngleKind.ACUTE):
                    return SegmentsRelationship.OVERLAP
                else:
                    return SegmentsRelationship.CROSS
            else:
                return SegmentsRelationship.OVERLAP
        else:
            return SegmentsRelationship.CROSS
    right_start_orientation = point_orientation_with_segment(right_start, left)
    right_end_orientation = point_orientation_with_segment(right_end, left)
    if (left_start_orientation * left_end_orientation < 0
            and right_start_orientation * right_end_orientation < 0):
        return SegmentsRelationship.CROSS
    elif (right_start_orientation is Orientation.COLLINEAR
          and _point_in_segment(right_start, left)):
        if right_end_orientation is Orientation.COLLINEAR:
            if right_start == left_start:
                if (to_angle_kind(right_end, right_start, left_end)
                        is AngleKind.ACUTE):
                    return SegmentsRelationship.OVERLAP
                else:
                    return SegmentsRelationship.CROSS
            elif right_start == left_end:
                if (to_angle_kind(right_end, right_start, left_start)
                        is AngleKind.ACUTE):
                    return SegmentsRelationship.OVERLAP
                else:
                    return SegmentsRelationship.CROSS
            else:
                return SegmentsRelationship.OVERLAP
        else:
            return SegmentsRelationship.CROSS
    elif (right_end_orientation is Orientation.COLLINEAR
          and _point_in_segment(right_end, left)):
        if right_start_orientation is Orientation.COLLINEAR:
            if right_end == left_start:
                if (to_angle_kind(right_start, right_end, left_end)
                        is AngleKind.ACUTE):
                    return SegmentsRelationship.OVERLAP
                else:
                    return SegmentsRelationship.CROSS
            elif right_end == left_end:
                if (to_angle_kind(right_start, right_end, left_start)
                        is AngleKind.ACUTE):
                    return SegmentsRelationship.OVERLAP
                else:
                    return SegmentsRelationship.CROSS
            else:
                return SegmentsRelationship.OVERLAP
        else:
            return SegmentsRelationship.CROSS
    else:
        return SegmentsRelationship.NONE


def point_orientation_with_segment(point: Point,
                                   segment: Segment) -> Orientation:
    start, end = segment
    return to_orientation(end, start, point)


def _point_in_segment(point: Point, segment: Segment) -> bool:
    segment_start, segment_end = segment
    if point == segment_start or point == segment_end:
        return True
    else:
        segment_start_x, segment_start_y = segment_start
        segment_end_x, segment_end_y = segment_end
        left_x, right_x = ((segment_start_x, segment_end_x)
                           if segment_start_x < segment_end_x
                           else (segment_end_x, segment_start_x))
        bottom_y, top_y = ((segment_start_y, segment_end_y)
                           if segment_start_y < segment_end_y
                           else (segment_end_y, segment_start_y))
        point_x, point_y = point
        return left_x <= point_x <= right_x and bottom_y <= point_y <= top_y


def find_intersections(first_segment: Segment, second_segment: Segment
                       ) -> Union[Tuple[()], Tuple[Point],
                                  Tuple[Point, Point]]:
    relationship = to_segments_relationship(first_segment, second_segment)
    if relationship is SegmentsRelationship.NONE:
        return ()
    elif relationship is SegmentsRelationship.CROSS:
        return _find_intersection(first_segment, second_segment),
    else:
        _, first_intersection_point, second_intersection_point, _ = sorted(
                first_segment + second_segment)
        return first_intersection_point, second_intersection_point


def _find_intersection(first_segment: Segment, second_segment: Segment,
                       _origin: Point = Point(0, 0)) -> Point:
    first_start, first_end = first_segment
    second_start, second_end = second_segment
    if first_start == second_start or first_start == second_end:
        return first_start
    elif first_end == second_start or first_end == second_end:
        return first_end
    elif (point_orientation_with_segment(second_start, first_segment)
          is Orientation.COLLINEAR):
        return second_start
    elif (point_orientation_with_segment(second_end, first_segment)
          is Orientation.COLLINEAR) is Orientation.COLLINEAR:
        return second_end
    elif (point_orientation_with_segment(first_start, second_segment)
          is Orientation.COLLINEAR):
        return first_start
    elif (point_orientation_with_segment(first_end, second_segment)
          is Orientation.COLLINEAR) is Orientation.COLLINEAR:
        return first_end
    else:
        coordinate, _ = first_start
        coordinate_type = type(coordinate)
        are_real_segments = issubclass(coordinate_type, Real)
        first_segment, second_segment = (_to_rational_segment(first_segment),
                                         _to_rational_segment(second_segment))
        first_start, first_end = first_segment
        second_start, second_end = second_segment
        denominator = parallelogram.signed_area(first_start, first_end,
                                                second_start, second_end)
        first_numerator = parallelogram.signed_area(
                first_start, second_start, second_start, second_end)
        second_numerator = parallelogram.signed_area(
                first_start, second_start, first_start, first_end)
        first_start_x, first_start_y = first_start
        first_end_x, first_end_y = first_end
        second_start_x, second_start_y = second_start
        second_end_x, second_end_y = second_end
        first_delta_x, first_delta_y = (first_end_x - first_start_x,
                                        first_end_y - first_start_y)
        second_delta_x, second_delta_y = (second_end_x - second_start_x,
                                          second_end_y - second_start_y)
        first_numerator_x = (first_start_x * denominator
                             + first_delta_x * first_numerator)
        first_numerator_y = (first_start_y * denominator
                             + first_delta_y * first_numerator)
        second_numerator_x = (second_start_x * denominator
                              + second_delta_x * second_numerator)
        second_numerator_y = (second_start_y * denominator
                              + second_delta_y * second_numerator)
        numerator_x, numerator_y, denominator_inv = (
            (Fraction(first_numerator_x + second_numerator_x, 2),
             Fraction(first_numerator_y + second_numerator_y, 2),
             Fraction(1, denominator))
            if isinstance(denominator, int)
            else ((first_numerator_x + second_numerator_x) / 2,
                  (first_numerator_y + second_numerator_y) / 2,
                  1 / denominator))
        intersection_point = Point(numerator_x * denominator_inv,
                                   numerator_y * denominator_inv)
        return (intersection_point
                if are_real_segments
                else _to_scalar_point(_to_real_point(intersection_point),
                                      coordinate_type))


def _to_rational_segment(segment: Segment) -> Segment:
    start, end = segment
    return Segment(_to_rational_point(start), _to_rational_point(end))
