import os

import pytest
from ground.linear import (to_segment_containment_checker,
                           to_segments_intersector,
                           to_segments_relater)
from hypothesis import (HealthCheck,
                        settings)

from tests.hints import (SegmentContainmentChecker,
                         SegmentsIntersector,
                         SegmentsRelater)

on_travis_ci = os.getenv('CI', False)
on_azure_pipelines = os.getenv('TF_BUILD', False)
settings.register_profile('default',
                          max_examples=(settings.default.max_examples
                                        if on_travis_ci or on_azure_pipelines
                                        else settings.default.max_examples),
                          deadline=None,
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])


@pytest.fixture(scope='session')
def segment_containment_checker() -> SegmentContainmentChecker:
    return to_segment_containment_checker()


@pytest.fixture(scope='session')
def segments_intersector() -> SegmentsIntersector:
    return to_segments_intersector()


@pytest.fixture(scope='session')
def segments_relater() -> SegmentsRelater:
    return to_segments_relater()
