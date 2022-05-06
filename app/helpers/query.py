import arrow
from django.db import models
from django.db.models.functions import Coalesce


DEFAULT_DATE = arrow.get('2021-03-23').datetime


def coalesce_and_sort(query):
    response = query.annotate(sort_date=Coalesce(
        'display_date', 'first_published_at', DEFAULT_DATE,
        output_field=models.DateField())).order_by('-sort_date')
    return response
