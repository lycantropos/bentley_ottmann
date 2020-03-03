from enum import (IntEnum,
                  unique)
from fractions import Fraction
from typing import (Tuple,
                    Union)

from robust import parallelogram

from bentley_ottmann.hints import (Point,
                                   Segment)
from .angular import (AngleKind,
                      Orientation,
                      to_angle_kind,
                      to_orientation)
from .point import (RealPoint,
                    is_real_point,
                    to_rational_point,
                    to_real_point,
                    to_scalar_point)

RealSegment = Tuple[RealPoint, RealPoint]


@unique
class SegmentsRelationship(IntEnum):
    NONE = 0
    CROSS = 1
    OVERLAP = 2


def to_segments_relationship(left: RealSegment,
                             right: RealSegment) -> SegmentsRelationship:
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


def point_orientation_with_segment(point: RealPoint,
                                   segment: RealSegment) -> Orientation:
    start, end = segment
    return to_orientation(end, start, point)


def _point_in_segment(point: RealPoint, segment: RealSegment) -> bool:
    (start_x, start_y), (end_x, end_y) = segment
    left_x, right_x = ((start_x, end_x)
                       if start_x < end_x
                       else (end_x, start_x))
    bottom_y, top_y = ((start_y, end_y)
                       if start_y < end_y
                       else (end_y, start_y))
    point_x, point_y = point
    return left_x <= point_x <= right_x and bottom_y <= point_y <= top_y


def find_intersections(left: Segment,
                       right: Segment) -> Union[Tuple[()], Tuple[Point],
                                                Tuple[Point, Point]]:
    are_real_segments = is_real_segment(left)
    left_real, right_real = ((left, right)
                             if are_real_segments
                             else (to_real_segment(left),
                                   to_real_segment(right)))
    relationship = to_segments_relationship(left_real, right_real)
    if relationship is SegmentsRelationship.NONE:
        return ()
    elif relationship is SegmentsRelationship.CROSS:
        intersection_point = find_intersection(left_real, right_real)
        if not are_real_segments:
            start, _ = left
            start_x, _ = start
            coordinate_type = type(start_x)
            intersection_point = to_scalar_point(intersection_point,
                                                 coordinate_type)
        return intersection_point,
    else:
        _, first_intersection_point, second_intersection_point, _ = sorted(
                left + right)
        return first_intersection_point, second_intersection_point


def point_in_segment(point: RealPoint, segment: RealSegment) -> bool:
    return (point in segment
            or (_point_in_segment(point, segment)
                and (point_orientation_with_segment(point, segment)
                     is Orientation.COLLINEAR)))


def find_intersection(left: RealSegment, right: RealSegment) -> Point:
    left_start, left_end = left
    right_start, right_end = right
    if point_in_segment(right_start, left):
        return right_start
    elif point_in_segment(right_end, left):
        return right_end
    elif point_in_segment(left_start, right):
        return left_start
    elif point_in_segment(left_end, right):
        return left_end
    else:
        left_start_x, left_start_y = left_start
        left_end_x, left_end_y = left_end
        right_start_x, right_start_y = right_start
        right_end_x, right_end_y = right_end

        denominator = parallelogram.signed_area(left_start, left_end,
                                                right_start, right_end)
        left_base_numerator = parallelogram.signed_area(
                left_start, right_start, right_start, right_end)
        right_base_numerator = parallelogram.signed_area(
                left_start, right_start, left_start, left_end)
        base_numerators_diff = (abs(right_base_numerator)
                                - abs(left_base_numerator))
        if not base_numerators_diff:
            left_delta_x, left_delta_y = (left_end_x - left_start_x,
                                          left_end_y - left_start_y)
            right_delta_x, right_delta_y = (right_end_x - right_start_x,
                                            right_end_y - right_start_y)
            left_numerator_x = (left_start_x * denominator
                                + left_delta_x * left_base_numerator)
            left_numerator_y = (left_start_y * denominator
                                + left_delta_y * left_base_numerator)
            right_numerator_x = (right_start_x * denominator
                                 + right_delta_x * right_base_numerator)
            right_numerator_y = (right_start_y * denominator
                                 + right_delta_y * right_base_numerator)
            numerator_x, numerator_y = ((Fraction(left_numerator_x
                                                  + right_numerator_x, 2),
                                         Fraction(left_numerator_y
                                                  + right_numerator_y, 2))
                                        if isinstance(denominator, int)
                                        else ((left_numerator_x
                                               + right_numerator_x) / 2,
                                              (left_numerator_y
                                               + right_numerator_y) / 2))
        elif base_numerators_diff > 0:
            numerator_x = (left_start_x * denominator
                           + left_base_numerator * (left_end_x - left_start_x))
            numerator_y = (left_start_y * denominator
                           + left_base_numerator * (left_end_y - left_start_y))
        else:
            numerator_x = (right_start_x * denominator
                           + right_base_numerator
                           * (right_end_x - right_start_x))
            numerator_y = (right_start_y * denominator
                           + right_base_numerator
                           * (right_end_y - right_start_y))
        denominator_inv = (Fraction(1, denominator)
                           if isinstance(denominator, int)
                           else 1 / denominator)
        return numerator_x * denominator_inv, numerator_y * denominator_inv


def is_real_segment(segment: Segment) -> bool:
    start, _ = segment
    return is_real_point(start)


def to_rational_segment(segment: Segment) -> Segment:
    start, end = segment
    return to_rational_point(start), to_rational_point(end)


def to_real_segment(segment: Segment) -> Segment:
    start, end = segment
    return to_real_point(start), to_real_point(end)
