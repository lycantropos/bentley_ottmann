import pytest
from ground.base import (Context,
                         get_context)
from hypothesis import (HealthCheck,
                        settings)

settings.register_profile('default',
                          deadline=None,
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])


@pytest.fixture(scope='session')
def context() -> Context:
    return get_context()
