from robust.linear import (SegmentsRelationship,
                           segments_intersection,
                           segments_intersections,
                           segments_relationship)

from bentley_ottmann.hints import Segment
from .point import to_rational_point

SegmentsRelationship = SegmentsRelationship
segments_relationship = segments_relationship
segments_intersection = segments_intersection
segments_intersections = segments_intersections


def to_rational_segment(segment: Segment) -> Segment:
    start, end = segment
    return to_rational_point(start), to_rational_point(end)


def sort_endpoints(segment: Segment) -> Segment:
    start, end = segment
    return (segment
            if start < end
            else (end, start))
