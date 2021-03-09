from django.db import models
from django_extensions.db.fields import AutoSlugField

from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import FieldPanel


class TaxonomyObjectMixin(ClusterableModel):

    class Meta():
        ordering = ['name', ]
        abstract = True

    name = models.CharField('Name', max_length=255)
    slug = AutoSlugField('Slug', populate_from='name')
    autocomplete_search_field = 'name'

    panels = [
        FieldPanel('name'),
    ]

    def __str__(self):
        return self.name

    def autocomplete_label(self):
        return self.name


class NewsCategory(TaxonomyObjectMixin):
    class Meta():
        ordering = ['name', ]
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
