from collections.abc import Sequence as _Sequence

from ground.context import Context as _Context, get_context as _get_context
from ground.enums import Relation as _Relation
from ground.hints import Contour as _Contour, Segment as _Segment

from ._core.base import sweep as _sweep
from ._core.hints import ScalarT as _ScalarT
from ._core.utils import all_unique as _all_unique


def contour_self_intersects(
    contour: _Contour[_ScalarT],
    /,
    *,
    context: _Context[_ScalarT] | None = None,
) -> bool:
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
    >>> contour_self_intersects(
    ...     Contour([Point(0, 0), Point(2, 0), Point(2, 2)])
    ... )
    False
    >>> contour_self_intersects(
    ...     Contour([Point(0, 0), Point(2, 0), Point(1, 0)])
    ... )
    True
    """
    vertices = contour.vertices
    if len(vertices) < 3:
        raise ValueError(f'Contour {contour} is degenerate.')
    if not _all_unique(vertices):
        return True
    if context is None:
        context = _get_context()
    segments = context.contour_segments(contour)
    return not all(
        event.relation in (_Relation.DISJOINT, _Relation.TOUCH)
        for event in _sweep(
            segments,
            context.angle_orientation,
            lambda first_start, first_end, second_start, second_end: (
                context.segments_intersection(
                    context.segment_cls(first_start, first_end),
                    context.segment_cls(second_start, second_end),
                )
            ),
        )
    )


def segments_intersect(
    segments: _Sequence[_Segment[_ScalarT]],
    /,
    *,
    context: _Context[_ScalarT] | None = None,
) -> bool:
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
    >>> segments_intersect(
    ...     [
    ...         Segment(Point(0, 0), Point(2, 0)),
    ...         Segment(Point(0, 2), Point(2, 2)),
    ...     ]
    ... )
    False
    >>> segments_intersect(
    ...     [
    ...         Segment(Point(0, 0), Point(2, 2)),
    ...         Segment(Point(0, 0), Point(2, 2)),
    ...     ]
    ... )
    True
    >>> segments_intersect(
    ...     [
    ...         Segment(Point(0, 0), Point(2, 2)),
    ...         Segment(Point(2, 0), Point(0, 2)),
    ...     ]
    ... )
    True
    """
    context = _get_context() if context is None else context
    return not all(
        event.relation is _Relation.DISJOINT
        for event in _sweep(
            segments,
            context.angle_orientation,
            lambda first_start, first_end, second_start, second_end: (
                context.segments_intersection(
                    context.segment_cls(first_start, first_end),
                    context.segment_cls(second_start, second_end),
                )
            ),
        )
    )


def segments_cross_or_overlap(
    segments: _Sequence[_Segment[_ScalarT]],
    /,
    *,
    context: _Context[_ScalarT] | None = None,
) -> bool:
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
    >>> segments_cross_or_overlap(
    ...     [
    ...         Segment(Point(0, 0), Point(2, 0)),
    ...         Segment(Point(0, 2), Point(2, 2)),
    ...     ]
    ... )
    False
    >>> segments_cross_or_overlap(
    ...     [
    ...         Segment(Point(0, 0), Point(2, 2)),
    ...         Segment(Point(0, 0), Point(2, 2)),
    ...     ]
    ... )
    True
    >>> segments_cross_or_overlap(
    ...     [
    ...         Segment(Point(0, 0), Point(2, 2)),
    ...         Segment(Point(0, 2), Point(2, 0)),
    ...     ]
    ... )
    True
    """
    context = _get_context() if context is None else context
    return not all(
        event.relation in (_Relation.DISJOINT, _Relation.TOUCH)
        for event in _sweep(
            segments,
            context.angle_orientation,
            lambda first_start, first_end, second_start, second_end: (
                context.segments_intersection(
                    context.segment_cls(first_start, first_end),
                    context.segment_cls(second_start, second_end),
                )
            ),
        )
    )
