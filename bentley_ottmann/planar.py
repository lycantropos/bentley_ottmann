from itertools import (product as _product,
                       repeat as _repeat)
from typing import (Dict as _Dict,
                    Sequence as _Sequence,
                    Tuple as _Tuple,
                    Union as _Union)

from ground import hints as _hints
from ground.base import (Relation as _Relation,
                         get_context as _get_context)

from .core.base import sweep as _sweep
from .core.utils import (all_unique as _all_unique,
                         to_pairs_combinations as _to_pairs_combinations,
                         to_sorted_pair as _to_sorted_pair)


def edges_intersect(contour: _hints.Contour) -> bool:
    """
    Checks if polygonal contour has self-intersection.

    Based on Bentley-Ottmann algorithm.

    Time complexity:
        ``O(len(contour) * log len(contour))``
    Memory complexity:
        ``O(len(contour))``
    Reference:
        https://en.wikipedia.org/wiki/Sweep_line_algorithm

    :param contour: contour to check.
    :returns: true if contour is self-intersecting, false otherwise.

    .. note::
        Consecutive equal vertices like ``Point(2, 0)`` in

        .. code-block:: python

            Contour([Point(0, 0), Point(2, 0), Point(2, 0), Point(2, 2)])

        will be considered as self-intersection,
        if you don't want them to be treated as such
        -- filter out before passing as argument.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Contour, Point = context.contour_cls, context.point_cls
    >>> edges_intersect(Contour([Point(0, 0), Point(2, 0), Point(2, 2)]))
    False
    >>> edges_intersect(Contour([Point(0, 0), Point(2, 0), Point(1, 0)]))
    True
    """
    vertices = contour.vertices
    if len(vertices) < 3:
        raise ValueError('Contour {contour} is degenerate.'
                         .format(contour=contour))
    if not _all_unique(vertices):
        return True
    context = _get_context()
    segment_cls = context.segment_cls
    edges = [segment_cls(vertices[index - 1], vertices[index])
             for index in range(len(vertices))]

    def non_neighbours_disjoint(edge_id: int,
                                other_edge_id: int,
                                last_edge_id: int = len(edges) - 1) -> bool:
        min_edge_id, max_edge_id = _to_sorted_pair(edge_id, other_edge_id)
        return (max_edge_id - min_edge_id == 1
                or (min_edge_id == 0 and max_edge_id == last_edge_id))

    return not all(event.has_only_relations(_Relation.DISJOINT,
                                            _Relation.TOUCH)
                   and all(non_neighbours_disjoint(id_, other_id)
                           for tangent in [*event.tangents,
                                           *event.right.tangents]
                           for id_, other_id in _product(event.segments_ids,
                                                         tangent.segments_ids))
                   for event in _sweep(edges,
                                       context=context))


def segments_intersect(segments: _Sequence[_hints.Segment]) -> bool:
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
    :returns: true if segments intersection found, false otherwise.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Point, Segment = context.point_cls, context.segment_cls
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
    return not all(event.has_only_relations(_Relation.DISJOINT)
                   for event in _sweep(segments,
                                       context=_get_context()))


def segments_cross_or_overlap(segments: _Sequence[_hints.Segment]) -> bool:
    """
    Checks if at least one pair of segments crosses or overlaps.

    Based on Bentley-Ottmann algorithm.

    Time complexity:
        ``O((len(segments) + len(intersections)) * log len(segments))``
    Memory complexity:
        ``O(len(segments))``
    Reference:
        https://en.wikipedia.org/wiki/Sweep_line_algorithm

    :param segments: sequence of segments.
    :returns: true if segments overlap or cross found, false otherwise.

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Point, Segment = context.point_cls, context.segment_cls
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
    ...                            Segment(Point(0, 2), Point(2, 0))])
    True
    """
    return not all(event.has_only_relations(_Relation.DISJOINT,
                                            _Relation.TOUCH)
                   for event in _sweep(segments,
                                       context=_get_context()))


def segments_intersections(segments: _Sequence[_hints.Segment]
                           ) -> _Dict[_Tuple[int, int],
                                      _Union[_Tuple[_hints.Point],
                                             _Tuple[_hints.Point,
                                                    _hints.Point]]]:
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

    >>> from ground.base import get_context
    >>> context = get_context()
    >>> Point, Segment = context.point_cls, context.segment_cls
    >>> segments_intersections([]) == {}
    True
    >>> segments_intersections([Segment(Point(0, 0), Point(2, 2))]) == {}
    True
    >>> segments_intersections([Segment(Point(0, 0), Point(2, 0)),
    ...                         Segment(Point(0, 2), Point(2, 2))]) == {}
    True
    >>> (segments_intersections([Segment(Point(0, 0), Point(2, 2)),
    ...                          Segment(Point(0, 0), Point(2, 2))])
    ...  == {(0, 1): (Point(0, 0), Point(2, 2))})
    True
    >>> (segments_intersections([Segment(Point(0, 0), Point(2, 2)),
    ...                          Segment(Point(2, 0), Point(0, 2))])
    ...  == {(0, 1): (Point(1, 1),)})
    True

    :param segments: sequence of segments.
    :returns:
        mapping between intersection points and corresponding segments indices.
    """
    left_parts_ids, right_parts_ids = {}, {}
    left_tangents, right_tangents = {}, {}
    for event in _sweep(segments,
                        context=_get_context()):
        if event.tangents:
            (left_tangents.setdefault(event.start, {})
             .setdefault(event.end, set())
             .update(tangent.end for tangent in event.tangents))
        if event.right.tangents:
            (right_tangents.setdefault(event.end, {})
             .setdefault(event.start, set())
             .update(tangent.end for tangent in event.right.tangents))
        for start, ends_ids in event.parts_ids.items():
            for end, ids in ends_ids.items():
                (left_parts_ids.setdefault(start, {}).setdefault(end, set())
                 .update(ids))
                (right_parts_ids.setdefault(end, {}).setdefault(start, set())
                 .update(ids))
    result = {}
    for start, ends_ids in left_parts_ids.items():
        for end, ids in ends_ids.items():
            for ids_pair in _to_pairs_combinations(sorted(ids)):
                if ids_pair in result:
                    prev_start, prev_end = result[ids_pair]
                    endpoints = min(prev_start, start), max(prev_end, end)
                else:
                    endpoints = (start, end)
                result[ids_pair] = endpoints
    for intersection_point, ends_tangents_ends in left_tangents.items():
        left_intersection_point_ids, right_intersection_point_ids = (
            left_parts_ids.get(intersection_point),
            right_parts_ids.get(intersection_point))
        for end, tangents_ends in ends_tangents_ends.items():
            ids = left_intersection_point_ids[end]
            for tangent_end in tangents_ends:
                tangent_ids = (left_intersection_point_ids[tangent_end]
                               if intersection_point < tangent_end
                               else right_intersection_point_ids[tangent_end])
                ids_pairs = [
                    _to_sorted_pair(id_, tangent_id)
                    for id_, tangent_id in _product(ids - tangent_ids,
                                                    tangent_ids - ids)]
                ids_pairs = [ids_pair
                             for ids_pair in ids_pairs
                             if ids_pair not in result]
                result.update(zip(ids_pairs, _repeat((intersection_point,))))
    for intersection_point, starts_tangents_ends in right_tangents.items():
        left_intersection_point_ids, right_intersection_point_ids = (
            left_parts_ids.get(intersection_point),
            right_parts_ids.get(intersection_point))
        for start, tangents_ends in starts_tangents_ends.items():
            ids = right_intersection_point_ids[start]
            for tangent_end in tangents_ends:
                tangent_ids = (left_intersection_point_ids[tangent_end]
                               if intersection_point < tangent_end
                               else right_intersection_point_ids[tangent_end])
                ids_pairs = [
                    _to_sorted_pair(id_, tangent_id)
                    for id_, tangent_id in _product(ids - tangent_ids,
                                                    tangent_ids - ids)]
                ids_pairs = [ids_pair
                             for ids_pair in ids_pairs
                             if ids_pair not in result]
                result.update(zip(ids_pairs, _repeat((intersection_point,))))
    return result
