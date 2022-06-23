import pytest
from django.conf import settings as dsettings


def test_stats_redis(settings, stats_redis):
    assert settings.STATS_USE_REDIS is True
    assert dsettings.STATS_USE_REDIS is True


@pytest.fixture
def stats_db(settings, stats_db):
    assert settings.STATS_USE_REDIS is False
    assert dsettings.STATS_USE_REDIS is False
