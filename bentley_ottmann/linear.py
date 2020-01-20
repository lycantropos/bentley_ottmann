from enum import (IntEnum,
                  unique)
from typing import (NamedTuple,
                    Tuple,
                    Union)

from robust import parallelogram

from .angular import (AngleKind,
                      Orientation,
                      to_angle_kind,
                      to_orientation)
from .point import (Point,
                    _to_real_point)

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
    left_start_orientation = point_orientation_with_segment(right, left_start)
    left_end_orientation = point_orientation_with_segment(right, left_end)
    if (left_start_orientation is Orientation.COLLINEAR
            and _in_segment(left_start, right)):
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
          and _in_segment(left_end, right)):
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
    right_start_orientation = point_orientation_with_segment(left, right_start)
    right_end_orientation = point_orientation_with_segment(left, right_end)
    if (left_start_orientation * left_end_orientation < 0
            and right_start_orientation * right_end_orientation < 0):
        return SegmentsRelationship.CROSS
    elif (right_start_orientation is Orientation.COLLINEAR
          and _in_segment(right_start, left)):
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
          and _in_segment(right_end, left)):
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


def point_orientation_with_segment(segment, point: Point) -> Orientation:
    start, end = segment
    return to_orientation(end, start, point)


def to_segment(start: Point, end: Point) -> Segment:
    if start == end:
        raise ValueError('Degenerate segment found.')
    return Segment(start, end)


def _in_segment(point: Point, segment: Segment) -> bool:
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
        else:
            first_start_real, first_end_real = (_to_real_point(first_start),
                                                _to_real_point(first_end))
            second_start_real, second_end_real = (_to_real_point(second_start),
                                                  _to_real_point(second_end))
            numerator = parallelogram.signed_area(first_start_real,
                                                  second_start_real,
                                                  second_start_real,
                                                  second_end_real)
            denominator = parallelogram.signed_area(first_start_real,
                                                    first_end_real,
                                                    second_start_real,
                                                    second_end_real)
            first_start_x, first_start_y = first_start
            first_end_x, first_end_y = first_end
            first_delta_x, first_delta_y = (first_end_x - first_start_x,
                                            first_end_y - first_start_y)
            denominator_inv = 1 / denominator
            x = ((first_start_x * denominator + first_delta_x * numerator)
                 * denominator_inv)
            y = ((first_start_y * denominator + first_delta_y * numerator)
                 * denominator_inv)
            return Point(x, y),
    else:
        _, first_intersection_point, second_intersection_point, _ = sorted(
                first_segment + second_segment)
        return first_intersection_point, second_intersection_point
