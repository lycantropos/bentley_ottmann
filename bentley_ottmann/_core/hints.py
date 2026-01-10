from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from ground import hints
from ground.enums import Orientation
from typing_extensions import Protocol

_Key = TypeVar('_Key', contravariant=True)
_Value = TypeVar('_Value', covariant=True)


class Map(Protocol[_Key, _Value]):
    def __getitem__(self, key: _Key, /) -> _Value: ...


ScalarT = TypeVar('ScalarT', bound=hints.Scalar)
Orienteer = Callable[
    [hints.Point[ScalarT], hints.Point[ScalarT], hints.Point[ScalarT]],
    Orientation,
]
SegmentsIntersector = Callable[
    [
        hints.Point[ScalarT],
        hints.Point[ScalarT],
        hints.Point[ScalarT],
        hints.Point[ScalarT],
    ],
    hints.Point[ScalarT],
]
