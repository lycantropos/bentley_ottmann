import os
import sys
import time
from datetime import timedelta

import pytest
from ground.base import (Context,
                         get_context)
from hypothesis import (HealthCheck,
                        settings)

is_pypy = sys.implementation.name == 'pypy'
on_ci = bool(os.getenv('CI', False))
max_examples = (-(-settings.default.max_examples // 4)
                if is_pypy and on_ci
                else settings.default.max_examples)
settings.register_profile('default',
                          deadline=None,
                          max_examples=max_examples,
                          suppress_health_check=[HealthCheck.too_slow])

if on_ci:
    time_left = timedelta(hours=1)


    @pytest.hookimpl(tryfirst=True)
    def pytest_runtest_call(item: pytest.Item) -> None:
        set_deadline = settings(deadline=time_left / max_examples)
        item.obj = set_deadline(item.obj)


    @pytest.fixture(scope='function', autouse=True)
    def time_function_call() -> None:
        start = time.monotonic()
        try:
            yield
        finally:
            duration = timedelta(seconds=time.monotonic() - start)
            global time_left
            time_left = max(duration, time_left) - duration


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session,
                         exitstatus: pytest.ExitCode) -> None:
    if exitstatus == pytest.ExitCode.NO_TESTS_COLLECTED:
        session.exitstatus = pytest.ExitCode.OK


@pytest.fixture(scope='session')
def context() -> Context:
    return get_context()
