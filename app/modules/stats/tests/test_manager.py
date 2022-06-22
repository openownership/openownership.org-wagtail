import arrow
import pytest

pytestmark = pytest.mark.django_db

from modules.stats.models import ViewCount


####################################################################################################
# DB Version
####################################################################################################


def test_hit_method(stats_db):
    count = ViewCount.objects.hit(1)

    assert count == 1

    record = ViewCount.objects.find(1)
    assert record is not None
    assert record.date == arrow.now().datetime.date()
    assert record.count == 1


def test_many_hits(stats_db):
    for i in range(0, 100):
        count = ViewCount.objects.hit(1)

    assert count == 100

    record = ViewCount.objects.find(1)
    assert record is not None
    assert record.date == arrow.now().datetime.date()
    assert record.count == 100


def test_hit_method_with_older_records(stats_db):
    old = arrow.now().shift(days=-10).datetime.date()
    for i in range(0, 10):
        ViewCount.objects.hit(1, old)

    record = ViewCount.objects.find(1, old)
    assert record is not None
    assert record.date == old
    assert record.count == 10

    count = ViewCount.objects.hit(1)
    record = ViewCount.objects.find(1)
    assert count == 1
    assert record is not None
    assert record.date == arrow.now().datetime.date()
    assert record.count == 1


def test_popular(stats_db):
    for i in range(0, 10):
        date = arrow.now().shift(days=i * -1).datetime.date()
        ViewCount.objects.hit(i, date)

    # We should have records for going back 10 days, but also we only want
    # popular in the last 7 days, so this should return 7 I think.
    result = ViewCount.objects.popular_with_counts(7)
    assert result.count() == 7


def test_popular_returns_most_visited(stats_db):
    for i in range(0, 10):
        date = arrow.now().shift(days=i * -1).datetime.date()
        ViewCount.objects.hit(i, date)

    result = ViewCount.objects.popular_with_counts(7)
    assert result.count() == 7

    for i in range(0, 4):
        date = arrow.now().shift(days=i * -1).datetime.date()
        ViewCount.objects.hit(i, date)

    # our first 4 returned records should now have a count of 2
    assert result[0]['count'] == 2
    assert result[1]['count'] == 2
    assert result[2]['count'] == 2
    assert result[3]['count'] == 2
    assert result[4]['count'] == 1


####################################################################################################
# DB Version
####################################################################################################


def test_hit_method_redis(stats_redis):
    count = ViewCount.objects.hit(1)
    assert count == 1


def test_many_hits_redis(stats_redis):
    for i in range(0, 100):
        count = ViewCount.objects.hit(2)

    assert count == 100


def test_popular_redis(stats_redis):
    for i in range(0, 10):
        ViewCount.objects.hit(i + 10)

    result = ViewCount.objects.popular_with_counts(limit=7)
    assert len(result) == 7


def test_popular_returns_most_visited_redis(stats_redis):
    for i in range(0, 10):
        ViewCount.objects.hit(i)

    result = ViewCount.objects.popular_with_counts(limit=7)
    assert len(result) == 7

    for i in range(0, 4):
        ViewCount.objects.hit(i)

    result = ViewCount.objects.popular_with_counts(limit=7)
    # our first 4 returned records should now have a count of 2
    assert result[0][1] == 2
    assert result[1][1] == 2
    assert result[2][1] == 2
    assert result[3][1] == 2
    assert result[4][1] == 1
