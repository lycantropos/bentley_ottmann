from functools import partial
from itertools import (combinations,
                       repeat,
                       starmap)
from typing import List

from hypothesis import strategies

from tests.strategies import (points_strategies,
                              segments_strategies)
from tests.utils import (Contour,
                         Point,
                         Segment,
                         Strategy,
                         pack,
                         scale_segment)

contours = (points_strategies.flatmap(partial(strategies.lists,
                                              min_size=3))
            .map(Contour))
non_triangular_contours = (points_strategies
                           .flatmap(partial(strategies.lists,
                                            min_size=4))
                           .map(Contour))
triangular_contours = (points_strategies
                       .flatmap(partial(strategies.lists,
                                        min_size=3,
                                        max_size=3))
                       .map(Contour))
degenerate_contours = (points_strategies
                       .flatmap(partial(strategies.lists,
                                        max_size=2))
                       .map(Contour))


def points_to_nets(points: Strategy[Point]) -> Strategy[List[Segment]]:
    def to_net(points_list: List[Point]) -> List[Segment]:
        return list(starmap(Segment, combinations(points_list, 2)))

    return (strategies.lists(points,
                             min_size=2,
                             max_size=8,
                             unique=True)
            .map(to_net))


nets = points_strategies.flatmap(points_to_nets)
segments_lists = segments_strategies.flatmap(strategies.lists) | nets


def to_overlapped_segments(segments: List[Segment],
                           scale: int) -> List[Segment]:
    return segments + [scale_segment(segment,
                                     scale=scale)
                       for segment in segments]


segments_lists |= strategies.builds(to_overlapped_segments, segments_lists,
                                    strategies.integers(1, 100))
empty_segments_lists = strategies.builds(list)
non_empty_segments_lists = ((segments_strategies
                             .flatmap(partial(strategies.lists,
                                              min_size=1)))
                            | nets)


def points_to_degenerate_segments(points: Strategy[Point]
                                  ) -> Strategy[Segment]:
    return (points.map(partial(repeat,
                               times=2))
            .map(pack(Segment)))


degenerate_segments = points_strategies.flatmap(points_to_degenerate_segments)
degenerate_segments_lists = strategies.lists(degenerate_segments,
                                             min_size=1)
