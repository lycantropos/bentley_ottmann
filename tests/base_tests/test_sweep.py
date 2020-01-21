from typing import (Iterable,
                    List)

from hypothesis import given

from bentley_ottmann.base import sweep
from bentley_ottmann.linear import (Segment,
                                    find_intersections)
from bentley_ottmann.point import Point
from tests.utils import all_unique
from . import strategies


@given(strategies.segments_lists)
def test_basic(segments_list: List[Segment]) -> None:
    result = sweep(segments_list)

    assert isinstance(result, Iterable)
    assert all(isinstance(element, tuple)
               and len(element) == 2
               and isinstance(element[0], Point)
               and isinstance(element[1], tuple)
               and all(isinstance(sub_coordinate, int)
                       and sub_coordinate >= 0
                       for sub_coordinate in element[1])
               and all_unique(element[1])
               for element in result)


@given(strategies.segments_lists)
def test_properties(segments_list: List[Segment]) -> None:
    result = sweep(segments_list)

    assert all(point in find_intersections(segments_list[first_index],
                                           segments_list[second_index])
               for point, (first_index, second_index) in result)
