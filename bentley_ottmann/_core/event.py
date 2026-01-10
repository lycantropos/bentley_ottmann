from typing import NewType

from .utils import is_even

Event = NewType('Event', int)

is_event_left = is_even


def segment_id_to_left_event(segment_id: int, /) -> Event:
    return Event(2 * segment_id)


def segment_id_to_right_event(segment_id: int, /) -> Event:
    return Event(2 * segment_id + 1)
