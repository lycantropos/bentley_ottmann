import os
import platform

import pytest
from ground.base import (Context,
                         get_context)
from hypothesis import (HealthCheck,
                        settings)

on_azure_pipelines = bool(os.getenv('TF_BUILD', False))
is_pypy = platform.python_implementation() == 'PyPy'
settings.register_profile('default',
                          max_examples=(settings.default.max_examples
                                        // (1 + 3 * is_pypy)
                                        if on_azure_pipelines
                                        else settings.default.max_examples),
                          suppress_health_check=[HealthCheck.filter_too_much,
                                                 HealthCheck.too_slow])


@pytest.fixture(scope='session')
def context() -> Context:
    return get_context()
