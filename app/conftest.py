# -*- coding: utf-8 -*-

"""
conftest
~~~~~~~~
Pytest config.
"""

import pytest
from cacheops import invalidate_all
from consoler import console  # NOQA

from modules.content.tests.fixtures import *  # NOQA
from modules.settings.tests.fixtures import *  # NOQA
from modules.stats.redis import RedisViewCounts
from modules.stats.tests.fixtures import *  # NOQA
from tests.fixtures import *  # NOQA
from tests.init import setup

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):  # noqa: ARG001
    stats_redis = RedisViewCounts()
    stats_redis._purge()
    invalidate_all()
    with django_db_blocker.unblock():
        setup()
    invalidate_all()
    stats_redis._purge()
