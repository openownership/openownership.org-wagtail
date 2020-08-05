from django.db import models
from modules.stats.models import ViewCount


class Countable(models.Model):

    class Meta:
        abstract = True

    is_countable = True
