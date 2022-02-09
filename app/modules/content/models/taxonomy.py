from django.db import models
from django_extensions.db.fields import AutoSlugField

from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import FieldPanel

from modules.content.models.mixins import TaxonomyObjectMixin


# class NewsCategory(TaxonomyObjectMixin):
#     class Meta():
#         ordering = ['name', ]
#         verbose_name = 'Category'
#         verbose_name_plural = 'Categories'
