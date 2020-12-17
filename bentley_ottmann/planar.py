from typing import (Dict,
                    Hashable,
                    Iterable,
                    Sequence,
                    Set,
                    Tuple)

from ground.geometries import to_segment_cls as _to_segment_cls
from ground.hints import (Contour,
                          Point,
                          Segment)
from ground.linear import (SegmentsRelationship as _SegmentsRelationship,
                           to_segments_intersector as _to_segments_intersector)

from .core import planar as _planar
from .core.utils import (merge_ids as _merge_ids,
                         to_pairs_combinations as _to_pairs_combinations)


def edges_intersect(contour: Contour,
                    *,
                    validate: bool = True) -> bool:
    """
    Checks if polygonal contour has self-intersection.

    Based on Shamos-Hoey algorithm.

    Time complexity:
        ``O(len(contour) * log len(contour))``
    Memory complexity:
        ``O(len(contour))``
    Reference:
        https://en.wikipedia.org/wiki/Sweep_line_algorithm

    :param contour: contour to check.
    :param validate:
        flag that tells whether to check contour for degeneracies
        and raise an exception in case of occurrence.
    :raises ValueError: if ``validate`` flag is set and contour is degenerate.
    :returns: true if contour is self-intersecting, false otherwise.

    .. note::
        Consecutive equal vertices like ``Point(2, 0)`` in

        .. code-block:: python

            Contour([Point(0, 0), Point(2, 0), Point(2, 0), Point(2, 2)])

        will be considered as self-intersection,
        if you don't want them to be treated as such
        -- filter out before passing as argument.

    >>> from ground.geometries import to_contour_cls, to_point_cls
    >>> Contour, Point = to_contour_cls(), to_point_cls()
    >>> edges_intersect(Contour([Point(0., 0.), Point(2., 0.), Point(2., 2.)]))
    False
    >>> edges_intersect(Contour([Point(0., 0.), Point(2., 0.), Point(1., 0.)]))
    True
    """
    vertices = contour.vertices
    if validate and len(vertices) < 3:
        raise ValueError('Contour {contour} is degenerate.'
                         .format(contour=contour))
    if not _all_unique(vertices):
        return True
    segment_cls = _to_segment_cls()
    edges = [segment_cls(vertices[index - 1], vertices[index])
             for index in range(len(vertices))]

    def non_neighbours_intersect(edges_ids: Iterable[Tuple[int, int]],
                                 last_edge_index: int = len(edges) - 1
                                 ) -> bool:
        return any(next_segment_id - segment_id > 1
                   and (segment_id != 0 or next_segment_id != last_edge_index)
                   for segment_id, next_segment_id in edges_ids)

    return any((first_event.relationship is _SegmentsRelationship.OVERLAP
                or second_event.relationship is _SegmentsRelationship.OVERLAP
                or non_neighbours_intersect(_to_pairs_combinations(_merge_ids(
                    first_event.segments_ids, second_event.segments_ids))))
               for first_event, second_event in _planar.sweep(edges, False))


def _all_unique(values: Iterable[Hashable]) -> bool:
    seen = set()
    seen_add = seen.add
    for value in values:
        if value in seen:
            return False
        else:
            seen_add(value)
    return True


def segments_intersect(segments: Sequence[Segment],
                       *,
                       validate: bool = True) -> bool:
    """
    Checks if segments have at least one intersection.

    Based on Shamos-Hoey algorithm.

    Time complexity:
        ``O(len(segments) * log len(segments))``
    Memory complexity:
        ``O(len(segments))``
    Reference:
        https://en.wikipedia.org/wiki/Sweep_line_algorithm

    :param segments: sequence of segments.
    :param validate:
        flag that tells whether to check segments for degeneracies
        and raise an exception in case of occurrence.
    :raises ValueError:
        if ``validate`` flag is set and degenerate segment found.
    :returns: true if segments intersection found, false otherwise.

    >>> from ground.geometries import to_point_cls, to_segment_cls
    >>> Point, Segment = to_point_cls(), _to_segment_cls()
    >>> segments_intersect([])
    False
    >>> segments_intersect([Segment(Point(0, 0), Point(2, 2))])
    False
    >>> segments_intersect([Segment(Point(0, 0), Point(2, 0)),
    ...                     Segment(Point(0, 2), Point(2, 2))])
    False
    >>> segments_intersect([Segment(Point(0, 0), Point(2, 2)),
    ...                     Segment(Point(0, 0), Point(2, 2))])
    True
    >>> segments_intersect([Segment(Point(0, 0), Point(2, 2)),
    ...                     Segment(Point(2, 0), Point(0, 2))])
    True
    """
    return any(_planar.sweep(segments, validate))


def segments_cross_or_overlap(segments: Sequence[Segment],
                              *,
                              validate: bool = True) -> bool:
    """
    Checks if at least one pair of segments crosses or overlaps.

    Based on Shamos-Hoey algorithm.

    Time complexity:
        ``O((len(segments) + len(intersections)) * log len(segments))``
    Memory complexity:
        ``O(len(segments))``
    Reference:
        https://en.wikipedia.org/wiki/Sweep_line_algorithm

    :param segments: sequence of segments.
    :param validate:
        flag that tells whether to check segments for degeneracies
        and raise an exception in case of occurrence.
    :raises ValueError:
        if ``validate`` flag is set and degenerate segment found.
    :returns: true if segments overlap or cross found, false otherwise.

    >>> from ground.geometries import to_point_cls, to_segment_cls
    >>> Point, Segment = to_point_cls(), _to_segment_cls()
    >>> segments_cross_or_overlap([])
    False
    >>> segments_cross_or_overlap([Segment(Point(0, 0), Point(2, 2))])
    False
    >>> segments_cross_or_overlap([Segment(Point(0, 0), Point(2, 0)),
    ...                            Segment(Point(0, 2), Point(2, 2))])
    False
    >>> segments_cross_or_overlap([Segment(Point(0, 0), Point(2, 2)),
    ...                            Segment(Point(0, 0), Point(2, 2))])
    True
    >>> segments_cross_or_overlap([Segment(Point(0, 0), Point(2, 2)),
    ...                            Segment(Point(2, 0), Point(0, 2))])
    True
    """
    relationships = _SegmentsRelationship.CROSS, _SegmentsRelationship.OVERLAP
    return any(first_event.relationship in relationships
               or second_event.relationship in relationships
               for first_event, second_event in _planar.sweep(segments,
                                                              validate))


def segments_intersections(segments: Sequence[Segment],
                           *,
                           validate: bool = True
                           ) -> Dict[Point, Set[Tuple[int, int]]]:
    """
    Returns mapping between intersection points
    and corresponding segments indices.

    Based on Bentley-Ottmann algorithm.

    Time complexity:
        ``O((len(segments) + len(intersections)) * log len(segments))``
    Memory complexity:
        ``O(len(segments) + len(intersections))``
    Reference:
        https://en.wikipedia.org/wiki/Bentley%E2%80%93Ottmann_algorithm

    >>> from ground.geometries import to_point_cls, to_segment_cls
    >>> Point, Segment = to_point_cls(), _to_segment_cls()
    >>> segments_intersections([]) == {}
    True
    >>> segments_intersections([Segment(Point(0, 0), Point(2, 2))]) == {}
    True
    >>> segments_intersections([Segment(Point(0, 0), Point(2, 0)),
    ...                         Segment(Point(0, 2), Point(2, 2))]) == {}
    True
    >>> (segments_intersections([Segment(Point(0, 0), Point(2, 2)),
    ...                          Segment(Point(0, 0), Point(2, 2))])
    ...  == {(0, 0): {(0, 1)}, (2, 2): {(0, 1)}})
    True
    >>> (segments_intersections([Segment(Point(0, 0), Point(2, 2)),
    ...                          Segment(Point(2, 0), Point(0, 2))])
    ...  == {(1, 1): {(0, 1)}})
    True

    :param segments: sequence of segments.
    :param validate:
        flag that tells whether to check segments for degeneracies
        and raise an exception in case of occurrence.
    :raises ValueError:
        if ``validate`` flag is set and degenerate segment found.
    :returns:
        mapping between intersection points and corresponding segments indices.
    """
    result = {}
    segments_intersector = _to_segments_intersector()
    for first_event, second_event in _planar.sweep(segments, validate):
        for segment_id, next_segment_id in _to_pairs_combinations(_merge_ids(
                first_event.segments_ids, second_event.segments_ids)):
            segment, next_segment = (segments[segment_id],
                                     segments[next_segment_id])
            for point in segments_intersector(segment.start, segment.end,
                                              next_segment.start,
                                              next_segment.end):
                result.setdefault(point, set()).add((segment_id,
                                                     next_segment_id))
    return result
