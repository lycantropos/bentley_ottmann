import os
import platform

import pytest
from datetime import timedelta
from ground.base import (Context,
                         get_context)
from hypothesis import settings

is_pypy = platform.python_implementation() == 'PyPy'
on_ci = bool(os.getenv('CI', False))
max_examples = (-(-settings.default.max_examples // 4)
                if is_pypy and on_ci
                else settings.default.max_examples)
settings.register_profile('default',
                          deadline=(timedelta(hours=1) / max_examples
                                    if on_ci
                                    else None),
                          max_examples=max_examples)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session: pytest.Session,
                         exitstatus: pytest.ExitCode) -> None:
    if exitstatus == pytest.ExitCode.NO_TESTS_COLLECTED:
        session.exitstatus = pytest.ExitCode.OK


@pytest.fixture(scope='session')
def context() -> Context:
    return get_context()
