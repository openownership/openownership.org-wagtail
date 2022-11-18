# stdlib
import datetime
from typing import Optional

# 3rd party
import arrow
from consoler import console
from django.db import models
from django.conf import settings

# Module
from .redis import RedisViewCounts


class ViewCountManager(models.Manager):

    def __init__(self, *args, **kwargs):
        try:
            self.r = RedisViewCounts()
        except Exception as error:
            console.warn(error)

        super().__init__(*args, **kwargs)

    def hit(self, page_id: int, date: Optional[datetime.date] = None) -> int:
        """Records a hit for a page for ``date``

        Args:
            page_id (int): The page id to record the hit for
            date (datetime.date, optional): The date to record the hit for, today if not set

        Returns:
            View: Description
        """
        if settings.STATS_USE_REDIS:
            return self.r.hit(page_id)

        date = self._check_date(date)
        record = self.find(page_id=page_id, date=date)
        record.count = record.count + 1
        record.save()
        return record.count

    def popular_with_counts(
            self, days: Optional[int] = 7, limit: Optional[int] = 100) -> models.QuerySet:
        """Returns the ``count`` most popular pages from the last ``days`` days.
        We're limiting the number returned to 100 as a sane default.

        Args:
            days (int): The number of days to look back
            limit (int, optional): The number of records to return
        """
        if settings.STATS_USE_REDIS:
            return self.r.popular_with_counts(limit=limit)

        shift = days * -1
        date = arrow.now().shift(days=shift).datetime.date()
        q = self.filter(date__gt=date).order_by('-count').values('page_id', 'count')[:limit]
        return q

    def popular(self, days: Optional[int] = 7, limit: Optional[int] = 100) -> models.QuerySet:
        """Returns the ``count`` most popular pages from the last ``days`` days, but this time
        it's JUST a list of IDs as this is easier to build your page query out of.
        We're limiting the number returned to 100 as a sane default.

        Args:
            days (int): The number of days to look back
            limit (int, optional): The number of records to return
        """
        if settings.STATS_USE_REDIS:
            return self.r.popular(limit=limit)

        shift = days * -1
        date = arrow.now().shift(days=shift).datetime.date()
        q = self.filter(date__gt=date).order_by('-count').values_list('page_id', flat=True)[:limit]
        return q

    def find(self, page_id: int, date: Optional[datetime.date] = None) -> models.Model:
        """Finds or creates a record for ``page_id`` / ``date``

        Args:
            page_id (int): The page id
            date (datetime.date, optional): The date

        Returns:
            models.Model: a ViewCount instance
        """
        date = self._check_date(date)
        rv, created = self.get_or_create(page_id=page_id, date=date)
        return rv

    def _check_date(self, date: Optional[datetime.date] = None) -> datetime.date:
        """Default date thing.

        Args:
            date (datetime.date, optional): A date object or None

        Returns:
            datetime.date: A date object
        """
        if date is None:
            date = arrow.now().datetime
        return date


####################################################################################################
# ViewCount
####################################################################################################


class ViewCount(models.Model):

    class Meta:
        unique_together = ['page_id', 'date']

    objects = ViewCountManager()

    page_id = models.IntegerField()
    date = models.DateField()
    count = models.IntegerField(default=0)

    def __str__(self):
        return f'<{self.page_id}/{self.date}> ({self.count})'
