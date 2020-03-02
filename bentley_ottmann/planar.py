from typing import (Dict,
                    Hashable,
                    Iterable,
                    Sequence,
                    Set,
                    Tuple)

from bentley_ottmann.hints import (Point,
                                   Segment)
from .core import planar as _planar
from .core.linear import (SegmentsRelationship,
                          find_intersections)
from .core.utils import (merge_ids as _merge_ids,
                         to_pairs_combinations as _to_pairs_combinations)


def edges_intersect(vertices: Sequence[Point],
                    *,
                    accurate: bool = True) -> bool:
    """
    Checks if polygon has self-intersection.

    Based on Shamos-Hoey algorithm.

    Time complexity:
        ``O(len(segments) * log len(segments))``
    Memory complexity:
        ``O(len(segments))``
    Reference:
        https://en.wikipedia.org/wiki/Sweep_line_algorithm

    :param vertices: sequence of polygon vertices.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: true if polygon is self-intersecting, false otherwise.

    .. note::
        Consecutive equal vertices like ``(2., 0.)`` in

        .. code-block:: python

            [(0., 0.), (2., 0.), (2., 0.), (2., 2.)]

        will be considered as self-intersection,
        if you don't want them to be treated as such
        -- filter out before passing as argument.

    >>> edges_intersect([(0., 0.), (2., 0.), (2., 2.)])
    False
    >>> edges_intersect([(0., 0.), (2., 0.), (1., 0.)])
    True
    """
    if not _all_unique(vertices):
        return True

    edges = _vertices_to_edges(vertices)

    def non_neighbours_intersect(edges_ids: Iterable[Tuple[int, int]],
                                 last_edge_index: int = len(edges) - 1
                                 ) -> bool:
        return any(next_segment_id - segment_id > 1
                   and (segment_id != 0 or next_segment_id != last_edge_index)
                   for segment_id, next_segment_id in edges_ids)

    return any((first_event.relationship is SegmentsRelationship.OVERLAP
                or second_event.relationship is SegmentsRelationship.OVERLAP
                or non_neighbours_intersect(_to_pairs_combinations(_merge_ids(
                    first_event.segments_ids, second_event.segments_ids))))
               for first_event, second_event in _planar.sweep(edges, accurate))


def _vertices_to_edges(vertices: Sequence[Point]) -> Sequence[Segment]:
    return [(vertices[index], vertices[(index + 1) % len(vertices)])
            for index in range(len(vertices))]


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
                       accurate: bool = True) -> bool:
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
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns: true if segments intersection found, false otherwise.

    >>> segments_intersect([])
    False
    >>> segments_intersect([((0., 0.), (2., 2.))])
    False
    >>> segments_intersect([((0., 0.), (2., 0.)),
    ...                     ((0., 2.), (2., 2.))])
    False
    >>> segments_intersect([((0., 0.), (2., 2.)),
    ...                     ((0., 0.), (2., 2.))])
    True
    >>> segments_intersect([((0., 0.), (2., 2.)),
    ...                     ((2., 0.), (0., 2.))])
    True
    """
    return any(_planar.sweep(segments, accurate))


def segments_intersections(segments: Sequence[Segment],
                           *,
                           accurate: bool = True
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

    >>> segments_intersections([])
    {}
    >>> segments_intersections([((0., 0.), (2., 2.))])
    {}
    >>> segments_intersections([((0., 0.), (2., 0.)),
    ...                         ((0., 2.), (2., 2.))])
    {}
    >>> segments_intersections([((0., 0.), (2., 2.)),
    ...                         ((0., 0.), (2., 2.))])
    {(0.0, 0.0): {(0, 1)}, (2.0, 2.0): {(0, 1)}}
    >>> segments_intersections([((0., 0.), (2., 2.)),
    ...                         ((2., 0.), (0., 2.))])
    {(1.0, 1.0): {(0, 1)}}


    :param segments: sequence of segments.
    :param accurate:
        flag that tells whether to use slow but more accurate arithmetic
        for floating point numbers.
    :returns:
        mapping between intersection points and corresponding segments indices.
    """
    result = {}
    for first_event, second_event in _planar.sweep(segments, accurate):
        for segment_id, next_segment_id in _to_pairs_combinations(_merge_ids(
                first_event.segments_ids, second_event.segments_ids)):
            for point in find_intersections(segments[segment_id],
                                            segments[next_segment_id]):
                result.setdefault(point, set()).add((segment_id,
                                                     next_segment_id))
    return result
