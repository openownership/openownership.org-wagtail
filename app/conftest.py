# -*- coding: utf-8 -*-

"""
    conftest
    ~~~~~~~~
    Pytest config.
"""

import pytest
from consoler import console  # NOQA
from cacheops import invalidate_all

try:
    import envkey  # NOQA
except Exception:
    pass


from tests.init import setup
from tests.fixtures import *  # NOQA
from modules.content.tests.fixtures import *  # NOQA


pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    invalidate_all()
    with django_db_blocker.unblock():
        setup()
    invalidate_all()
