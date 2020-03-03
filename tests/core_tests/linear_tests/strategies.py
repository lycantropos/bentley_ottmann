from functools import partial
from typing import (Callable,
                    Optional,
                    Tuple)

from hypothesis import strategies

from bentley_ottmann.hints import (Scalar,
                                   Segment)
from tests.strategies import segments_strategies
from tests.utils import (Strategy,
                         identity,
                         reflect_segment,
                         reverse_segment,
                         scale_segment,
                         to_pairs)


def to_pythagorean_triplets(*,
                            min_value: int = 1,
                            max_value: Optional[int] = None
                            ) -> Strategy[Tuple[int, int, int]]:
    if min_value < 1:
        raise ValueError('`min_value` should be positive.')

    def to_increasing_integers_pairs(value: int) -> Strategy[Tuple[int, int]]:
        return strategies.tuples(strategies.just(value),
                                 strategies.integers(min_value=value + 1,
                                                     max_value=max_value))

    def to_pythagorean_triplet(increasing_integers_pair: Tuple[int, int]
                               ) -> Tuple[int, int, int]:
        first, second = increasing_integers_pair
        first_squared = first ** 2
        second_squared = second ** 2
        return (second_squared - first_squared,
                2 * first * second,
                first_squared + second_squared)

    return (strategies.integers(min_value=min_value,
                                max_value=(max_value - 1
                                           if max_value is not None
                                           else max_value))
            .flatmap(to_increasing_integers_pairs)
            .map(to_pythagorean_triplet))


pythagorean_triplets = to_pythagorean_triplets(max_value=1000)


def to_maybe_intersecting_segments(segments: Strategy[Segment]
                                   ) -> Strategy[Tuple[Segment,
                                                       Segment]]:
    def to_scaled_segments_pair(segment_with_scale: Tuple[Segment, Scalar]
                                ) -> Tuple[Segment, Segment]:
        segment, scale = segment_with_scale
        return segment, scale_segment(segment,
                                      scale=scale)

    def to_rotated_segments_pair(
            segment_with_pythagorean_triplet: Tuple[Segment,
                                                    Tuple[int, int, int]]
    ) -> Tuple[Segment, Segment]:
        segment, pythagorean_triplet = segment_with_pythagorean_triplet
        start, end = segment
        (start_x, start_y), (end_x, end_y) = start, end
        area_sine, area_cosine, area = pythagorean_triplet
        dx, dy = end_x - start_x, end_y - start_y
        return segment, (start, ((area_cosine * dx - area_sine * dy) / area,
                                 (area_sine * dx + area_cosine * dy) / area))

    def map_first(map_: Callable[[Segment], Segment],
                  segments_pair: Tuple[Segment, Segment]
                  ) -> Tuple[Segment, Segment]:
        first, second = segments_pair
        return map_(first), second

    def map_second(map_: Callable[[Segment], Segment],
                   segments_pair: Tuple[Segment, Segment]
                   ) -> Tuple[Segment, Segment]:
        first, second = segments_pair
        return first, map_(second)

    variants = [segments.map(lambda segment: (segment, segment)),
                (strategies.tuples(segments,
                                   strategies.integers(min_value=-100,
                                                       max_value=-1)
                                   | strategies.integers(min_value=1,
                                                         max_value=100))
                 .map(to_scaled_segments_pair)),
                (strategies.tuples(segments, pythagorean_triplets)
                 .map(to_rotated_segments_pair)),
                strategies.tuples(segments, segments)]
    for map_ in (reverse_segment, reflect_segment):
        variants.extend([base.map(partial(map_first, map_))
                         for base in variants]
                        + [base.map(partial(map_second, map_))
                           for base in variants])
    return strategies.one_of(variants)


segments = segments_strategies.flatmap(identity)
segments_pairs = (
        segments_strategies.flatmap(to_pairs)
        | segments_strategies.flatmap(to_maybe_intersecting_segments))
