from collections.abc import Sequence
from functools import partial
from itertools import combinations, repeat, starmap
from typing import Any

from ground.hints import Point, Segment
from hypothesis import strategies as st

from tests.hints import ScalarT
from tests.strategies import point_strategy_strategy, segment_strategy_strategy
from tests.utils import context, pack, scale_segment

contour_strategy = point_strategy_strategy.flatmap(
    partial(st.lists, min_size=3)
).map(context.contour_cls)
non_triangular_contour_strategy = point_strategy_strategy.flatmap(
    partial(st.lists, min_size=4)
).map(context.contour_cls)
triangular_contour_strategy = point_strategy_strategy.flatmap(
    partial(st.lists, min_size=3, max_size=3)
).map(context.contour_cls)
degenerate_contour_strategy = point_strategy_strategy.flatmap(
    partial(st.lists, max_size=2)
).map(context.contour_cls)


def point_to_net_strategy(
    point_strategy: st.SearchStrategy[Point[ScalarT]], /
) -> st.SearchStrategy[Sequence[Segment[ScalarT]]]:
    def to_net(
        points_list: Sequence[Point[ScalarT]], /
    ) -> Sequence[Segment[ScalarT]]:
        return list(starmap(context.segment_cls, combinations(points_list, 2)))

    return st.lists(point_strategy, min_size=2, max_size=8, unique=True).map(
        to_net
    )


net_strategy = point_strategy_strategy.flatmap(point_to_net_strategy)
segment_sequence_strategy = (
    segment_strategy_strategy.flatmap(st.lists) | net_strategy
)


def to_overlapped_segments(
    segments: Sequence[Segment[ScalarT]], scale: int, /
) -> list[Segment[ScalarT]]:
    return [
        *segments,
        *[scale_segment(segment, scale=scale) for segment in segments],
    ]


segment_sequence_strategy |= st.builds(
    to_overlapped_segments, segment_sequence_strategy, st.integers(1, 100)
)
empty_segment_sequence_strategy: st.SearchStrategy[Sequence[Segment[Any]]] = (
    st.builds(list)
)
non_empty_segment_sequence_strategy = (
    segment_strategy_strategy.flatmap(partial(st.lists, min_size=1))
) | net_strategy


def point_to_degenerate_segment_strategy(
    point_strategy: st.SearchStrategy[Point[ScalarT]], /
) -> st.SearchStrategy[Segment[ScalarT]]:
    return point_strategy.map(partial(repeat, times=2)).map(
        pack(context.segment_cls)
    )


degenerate_segment_strategy = point_strategy_strategy.flatmap(
    point_to_degenerate_segment_strategy
)
degenerate_segment_sequence_strategy = st.lists(
    degenerate_segment_strategy, min_size=1
)
