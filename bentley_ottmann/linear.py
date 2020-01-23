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


def find_intersections(first_segment: Segment, second_segment: Segment,
                       _origin: Point = Point(0, 0)
                       ) -> Union[Tuple[()], Tuple[Point],
                                  Tuple[Point, Point]]:
    relationship = to_segments_relationship(first_segment, second_segment)
    if relationship is SegmentsRelationship.NONE:
        return ()
    elif relationship is SegmentsRelationship.CROSS:
        first_start, first_end = first_segment
        second_start, second_end = second_segment
        if first_start == second_start or first_start == second_end:
            return first_start,
        elif first_end == second_start or first_end == second_end:
            return first_end,
        elif to_orientation(first_start, first_end,
                            second_start) is Orientation.COLLINEAR:
            return second_start,
        elif to_orientation(first_start, first_end,
                            second_end) is Orientation.COLLINEAR:
            return second_end,
        elif to_orientation(second_start, second_end,
                            first_start) is Orientation.COLLINEAR:
            return first_start,
        elif to_orientation(second_start, second_end,
                            first_end) is Orientation.COLLINEAR:
            return first_end,
        else:
            coordinate, _ = first_start
            coordinate_type = type(coordinate)
            are_real_segments = issubclass(coordinate_type, Real)
            if not are_real_segments:
                first_start, first_end = (_to_real_point(first_start),
                                          _to_real_point(first_end))
                second_start, second_end = (_to_real_point(second_start),
                                            _to_real_point(second_end))
            denominator = parallelogram.signed_area(first_start, first_end,
                                                    second_start, second_end)
            first_cross_product = parallelogram.signed_area(
                    _origin, first_start, _origin, first_end)
            second_cross_product = parallelogram.signed_area(
                    _origin, second_start, _origin, second_end)
            first_start_x, first_start_y = first_start
            first_end_x, first_end_y = first_end
            second_start_x, second_start_y = second_start
            second_end_x, second_end_y = second_end
            denominator_inv = (Fraction(1, denominator)
                               if issubclass(coordinate_type, int)
                               else 1 / denominator)
            x = ((first_cross_product * (second_start_x - second_end_x)
                  - second_cross_product * (first_start_x - first_end_x))
                 * denominator_inv)
            y = ((first_cross_product * (second_start_y - second_end_y)
                  - second_cross_product * (first_start_y - first_end_y))
                 * denominator_inv)
            intersection_point = Point(x, y)
            return (intersection_point
                    if are_real_segments
                    else _to_scalar_point(intersection_point,
                                          coordinate_type)),
    else:
        _, first_intersection_point, second_intersection_point, _ = sorted(
                first_segment + second_segment)
        return first_intersection_point, second_intersection_point
