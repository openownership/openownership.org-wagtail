import pytest
from modules.stats.redis import RedisViewCounts


@pytest.fixture
def stats_redis(settings):
    settings.STATS_USE_REDIS = True
    r = RedisViewCounts()
    r._purge()


@pytest.fixture
def stats_db(settings):
    settings.STATS_USE_REDIS = False
