from operator import ne

from ground.hints import Point, Segment
from hypothesis import strategies as st

from tests.hints import ScalarT
from tests.utils import MAX_SCALAR, MIN_SCALAR, context, pack, to_pair_strategy

scalar_strategy_strategy = st.just(st.fractions(MIN_SCALAR, MAX_SCALAR))


def scalar_to_segment_strategy(
    scalar_strategy: st.SearchStrategy[ScalarT], /
) -> st.SearchStrategy[Segment[ScalarT]]:
    return (
        to_pair_strategy(scalar_to_point_strategy(scalar_strategy))
        .filter(pack(ne))
        .map(pack(context.segment_cls))
    )


def scalar_to_point_strategy(
    scalar_strategy: st.SearchStrategy[ScalarT], /
) -> st.SearchStrategy[Point[ScalarT]]:
    return st.builds(context.point_cls, scalar_strategy, scalar_strategy)


point_strategy_strategy = scalar_strategy_strategy.map(
    scalar_to_point_strategy
)
segment_strategy_strategy = scalar_strategy_strategy.map(
    scalar_to_segment_strategy
)
