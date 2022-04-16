from itertools import product as _product
from typing import (Optional as _Optional,
                    Sequence as _Sequence)

from ground.base import (Context as _Context,
                         Relation as _Relation,
                         get_context as _get_context)
from ground.hints import (Contour as _Contour,
                          Segment as _Segment)

from .core.base import sweep as _sweep
from .core.utils import (all_unique as _all_unique,
                         to_sorted_pair as _to_sorted_pair)


def contour_self_intersects(contour: _Contour,
                            *,
                            context: _Optional[_Context] = None) -> bool:
    """
    Checks if contour has self-intersection.

    Based on Bentley-Ottmann algorithm.

    Time complexity:
        ``O(len(contour.vertices) * log len(contour.vertices))``
    Memory complexity:
        ``O(len(contour.vertices))``
    Reference:
        https://en.wikipedia.org/wiki/Sweep_line_algorithm

    :param contour: contour to check.
    :param context: geometrical context.
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
    >>> contour_self_intersects(Contour([Point(0, 0), Point(2, 0),
    ...                                  Point(2, 2)]))
    False
    >>> contour_self_intersects(Contour([Point(0, 0), Point(2, 0),
    ...                                  Point(1, 0)]))
    True
    """
    vertices = contour.vertices
    if len(vertices) < 3:
        raise ValueError('Contour {contour} is degenerate.'
                         .format(contour=contour))
    if not _all_unique(vertices):
        return True
    if context is None:
        context = _get_context()
    segments = context.contour_segments(contour)

    def non_neighbours_disjoint(segment_id: int,
                                other_segment_id: int,
                                last_segment_id: int = len(segments) - 1
                                ) -> bool:
        min_edge_id, max_edge_id = _to_sorted_pair(segment_id,
                                                   other_segment_id)
        return (max_edge_id - min_edge_id == 1
                or (min_edge_id == 0 and max_edge_id == last_segment_id))

    return not all(event.has_only_relations(_Relation.DISJOINT,
                                            _Relation.TOUCH)
                   and all(non_neighbours_disjoint(id_, other_id)
                           for tangent in [*event.tangents,
                                           *event.right.tangents]
                           for id_, other_id in _product(event.segments_ids,
                                                         tangent.segments_ids))
                   for event in _sweep(segments,
                                       context=context))


def segments_intersect(segments: _Sequence[_Segment],
                       *,
                       context: _Optional[_Context] = None) -> bool:
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
    :param context: geometrical context.
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
                                       context=(_get_context()
                                                if context is None
                                                else context)))


def segments_cross_or_overlap(segments: _Sequence[_Segment],
                              *,
                              context: _Optional[_Context] = None) -> bool:
    """
    Checks if at least one pair of segments crosses or overlaps.

    Based on Bentley-Ottmann algorithm.

    Time complexity:
        ``O(len(segments) * log len(segments))``
    Memory complexity:
        ``O(len(segments))``
    Reference:
        https://en.wikipedia.org/wiki/Bentley%E2%80%93Ottmann_algorithm

    :param segments: sequence of segments.
    :param context: geometrical context.
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
                                       context=(_get_context()
                                                if context is None
                                                else context)))
