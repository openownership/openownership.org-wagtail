from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from taggit.models import TagBase
from wagtail.admin.edit_handlers import (
    FieldPanel, ObjectList, MultiFieldPanel, TabbedInterface
)
from wagtail.core.models import Page


####################################################################################################
# One to Many Categories
####################################################################################################


class Category(models.Model):

    class Meta:
        abstract = True
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    name = models.CharField(blank=False, null=False, max_length=255)
    slug = AutoSlugField(populate_from='name')

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
        ], heading="Public fields"),
        # MultiFieldPanel([
        #     FieldPanel('slug'),
        # ], heading="Internal fields")
    ]

    def __str__(self):
        return self.name


####################################################################################################
# Manager
####################################################################################################


class TagManager(models.Manager):

    def as_dicts(self):
        fields = ['id', 'name', 'slug']
        qs = self.values(*fields)
        return list(qs)


####################################################################################################
# Base
####################################################################################################


class BaseTag(TagBase):

    class Meta:
        abstract = True
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    objects = TagManager()

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
        ], heading="Public fields"),
        # MultiFieldPanel([
        #     FieldPanel('slug'),
        # ], heading="Internal fields")
    ]

    edit_handler = TabbedInterface([
        ObjectList(panels, heading=_('Tag')),
    ])

    @property
    def pages(self):
        rel = getattr(self, self.rel_name)
        ids = [item.content_object.id for item in rel.all()]
        pages = Page.objects.filter(
            id__in=ids).order_by('-first_published_at').specific().all()
        return pages

    def latest(self, count=1):
        pages = self.pages[:count]
        return pages

    @cached_property
    def url(self):
        """Here we need to return the url for either a TopicPage if one exists for this tag,
        or the root tag view.
        """
        try:
            return self.topic_page.url
        except Exception:
            return reverse('tagged', kwargs={'slug': self.slug})
