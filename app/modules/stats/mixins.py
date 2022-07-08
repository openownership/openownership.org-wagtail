from django.db import models


class Countable(models.Model):

    class Meta:
        abstract = True

    is_countable = True
