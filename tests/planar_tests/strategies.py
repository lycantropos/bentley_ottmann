from functools import partial
from itertools import combinations, repeat, starmap
from typing import Any

from ground.hints import Point, Segment
from hypothesis import strategies as st

from tests.hints import ScalarT
from tests.strategies import points_strategies, segments_strategies
from tests.utils import Strategy, context, pack, scale_segment

contours = points_strategies.flatmap(partial(st.lists, min_size=3)).map(
    context.contour_cls
)
non_triangular_contours = points_strategies.flatmap(
    partial(st.lists, min_size=4)
).map(context.contour_cls)
triangular_contours = points_strategies.flatmap(
    partial(st.lists, min_size=3, max_size=3)
).map(context.contour_cls)
degenerate_contours = points_strategies.flatmap(
    partial(st.lists, max_size=2)
).map(context.contour_cls)


def points_to_nets(
    points: Strategy[Point[ScalarT]],
) -> Strategy[list[Segment[ScalarT]]]:
    def to_net(points_list: list[Point[ScalarT]]) -> list[Segment[ScalarT]]:
        return list(starmap(context.segment_cls, combinations(points_list, 2)))

    return st.lists(points, min_size=2, max_size=8, unique=True).map(to_net)


nets = points_strategies.flatmap(points_to_nets)
segments_lists = segments_strategies.flatmap(st.lists) | nets


def to_overlapped_segments(
    segments: list[Segment[ScalarT]], scale: int
) -> list[Segment[ScalarT]]:
    return segments + [
        scale_segment(segment, scale=scale) for segment in segments
    ]


segments_lists |= st.builds(
    to_overlapped_segments, segments_lists, st.integers(1, 100)
)
empty_segments_lists: st.SearchStrategy[list[Segment[Any]]] = st.builds(list)
non_empty_segments_lists: st.SearchStrategy[list[Segment[Any]]] = (
    segments_strategies.flatmap(partial(st.lists, min_size=1))
) | nets


def points_to_degenerate_segments(
    points: Strategy[Point[ScalarT]],
) -> Strategy[Segment[ScalarT]]:
    return points.map(partial(repeat, times=2)).map(pack(context.segment_cls))


degenerate_segments = points_strategies.flatmap(points_to_degenerate_segments)
degenerate_segments_lists = st.lists(degenerate_segments, min_size=1)
