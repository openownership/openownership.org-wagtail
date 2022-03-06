from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from taggit.models import TagBase
from wagtail.core import fields
from wagtail.core.models import Locale
from wagtail.admin.edit_handlers import (
    FieldPanel, ObjectList, MultiFieldPanel, StreamFieldPanel, TabbedInterface
)
from wagtail.core.models import Page

from modules.content.blocks import category_page_body_blocks, tag_page_body_blocks
from .pages import DummyPage


####################################################################################################
# One to Many Categories
####################################################################################################


class Category(models.Model):

    class Meta:
        abstract = True
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    # Child classes should set this to use get_url() and to_dummy_page()
    url_name = None

    name = models.CharField(blank=False, null=False, max_length=255)
    slug = AutoSlugField(populate_from='name')

    blurb = models.CharField(
        blank=True,
        max_length=255,
        help_text=_('Used when showing a card linking to this tag')
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('blurb'),
            # StreamFieldPanel('body')
        ], heading=_("Public fields")),
    ]

    def __str__(self):
        return self.name

    @cached_property
    def pages(self):
        """
        Returns all the Pages that have this Category.
        """

        # All the relationships to page models:
        rels = [rel for rel in dir(self) if rel.startswith('pages_')]

        # Get ALL of the Page IDs that have this category:
        all_ids = []
        for rel_name in rels:
            rel = getattr(self, rel_name)
            all_ids = all_ids + [page.id for page in rel.all()]

        # Filter those pages by Locale, live, etc:
        return (
            Page.objects
            .filter(id__in=all_ids)
            .live()
            .filter(locale=Locale.get_active())
            .order_by('-first_published_at')
            .specific()
        )

    def to_dummy_page(self, section_page):
        """
        Returns a DummyPage representing this category.
        Useful for passing to templates that expect a Page like object.
        section_page is the section page the category is within.
        e.g. 'insight'
        """
        page = DummyPage()
        page.title = self.name
        page.url = self.get_url(section_page)
        page.blurb = self.blurb
        return page


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
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

    # Child classes should set this to use get_url() and to_dummy_page()
    url_name = None

    objects = TagManager()

    blurb = models.CharField(
        blank=True,
        max_length=255,
        help_text=_('Used when showing a card linking to this tag')
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('blurb'),
            # StreamFieldPanel('body')
        ], heading=_("Public fields")),
    ]

    edit_handler = TabbedInterface([
        ObjectList(panels, heading=_('Tag')),
    ])

    def __str__(self):
        return self.name

    def to_dummy_page(self, section_page):
        """
        Returns a DummyPage representing this tag.
        Useful for passing to templates that expect a Page like object.
        section_page is the the section page the tag is within.
        e.g. 'insight'
        """
        page = DummyPage()
        page.title = self.name
        page.url = self.get_url(section_page)
        page.blurb = self.blurb
        return page

    # @property
    # def pages(self):
    #     rel = getattr(self, self.rel_name)
    #     ids = [item.content_object.id for item in rel.all()]
    #     pages = Page.objects.filter(
    #         id__in=ids).order_by('-first_published_at').specific().all()
    #     return pages

    # def latest(self, count=1):
    #     pages = self.pages[:count]
    #     return pages

    # @cached_property
    # def url(self):
    #     """Here we need to return the url for either a TopicPage if one exists for this tag,
    #     or the root tag view.
    #     """
    #     try:
    #         return self.topic_page.url
    #     except Exception:
    #         return reverse('tagged', kwargs={'slug': self.slug})
