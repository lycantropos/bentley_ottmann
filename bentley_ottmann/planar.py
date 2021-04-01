from itertools import (product,
                       repeat)
from typing import (Dict,
                    Hashable,
                    Iterable,
                    Sequence,
                    Tuple)

from ground import hints as _hints
from ground.base import (Relation as _Relation,
                         get_context as _get_context)

from .core.base import sweep as _sweep
from .core.utils import (to_pairs_combinations as _to_pairs_combinations,
                         to_sorted_pair)


def edges_intersect(contour: _hints.Contour) -> bool:
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

    def non_neighbours_intersect(segment_id: int,
                                 next_segment_id: int,
                                 last_edge_index: int = len(edges) - 1
                                 ) -> bool:
        return (next_segment_id - segment_id > 1
                and (segment_id != 0 or next_segment_id != last_edge_index))

    return any(not event.has_only_relations(_Relation.DISJOINT,
                                            _Relation.TOUCH)
               or any(non_neighbours_intersect(*to_sorted_pair(id_,
                                                               tangent_id))
                      for tangent in event.tangents + event.opposite.tangents
                      for id_, tangent_id in product(event.ids, tangent.ids))
               for event in _sweep(edges,
                                   context=context))


def _all_unique(values: Iterable[Hashable]) -> bool:
    seen = set()
    seen_add = seen.add
    for value in values:
        if value in seen:
            return False
        else:
            seen_add(value)
    return True


def segments_intersect(segments: Sequence[_hints.Segment]) -> bool:
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


def segments_cross_or_overlap(segments: Sequence[_hints.Segment]) -> bool:
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


def segments_intersections(segments: Sequence[_hints.Segment]
                           ) -> Dict[Tuple[int, int],
                                     Tuple[_hints.Point, _hints.Point]]:
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
    ...  == {(0, 1): (Point(1, 1), Point(1, 1))})
    True

    :param segments: sequence of segments.
    :returns:
        mapping between intersection points and corresponding segments indices.
    """
    result = {}
    all_parts_ids = {}
    tangents = {}
    for event in _sweep(segments,
                        context=_get_context()):
        event_tangents = event.tangents + event.opposite.tangents
        if event_tangents:
            (tangents.setdefault(event.start, {}).setdefault(event.end, [])
             .extend(event_tangents))
        for start, ends_ids in event.parts_ids.items():
            for end, ids in ends_ids.items():
                all_end_ids = all_parts_ids.setdefault(start, {})
                if end in all_end_ids:
                    all_end_ids[end].update(ids)
                else:
                    all_end_ids[end] = ids
                for ids_pair in _to_pairs_combinations(sorted(ids)):
                    if ids_pair in result:
                        prev_start, prev_end = result[ids_pair]
                        endpoints = min(prev_start, start), max(prev_end, end)
                    else:
                        endpoints = (start, end)
                    result[ids_pair] = endpoints
    for start, ends_tangents in tangents.items():
        for end, end_tangents in ends_tangents.items():
            for tangent in end_tangents:
                endpoint = tangent.start
                ids, tangent_ids = (all_parts_ids[start][end],
                                    all_parts_ids[endpoint][tangent.end]
                                    if tangent.is_left_endpoint
                                    else all_parts_ids[tangent.end][endpoint])
                if ids.isdisjoint(tangent_ids):
                    result.update(zip(
                            [to_sorted_pair(first_id, second_id)
                             for first_id, second_id in product(ids,
                                                                tangent_ids)],
                            repeat((endpoint, endpoint))))
    return result
