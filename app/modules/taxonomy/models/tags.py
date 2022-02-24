# 3rd party
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from taggit.models import ItemBase
from wagtail.snippets.models import register_snippet

from .core import BaseTag


####################################################################
# AREAS OF FOCUS

@register_snippet
class FocusAreaTag(BaseTag):

    free_tagging = False

    # Name of the URL for viewing things with this Tag.
    url_name = "focusarea-tag"

    class Meta:
        verbose_name = _("Area of Focus")
        verbose_name_plural = _("Areas of Focus")

    def get_url(self, section_slug):
        """Generate the URL to this tag's view
        section_slug is the Slug of the section page the tag is within.
        e.g. 'insight'
        """
        return reverse(
            self.url_name,
            kwargs={'section_slug': section_slug, 'tag_slug': self.slug}
        )


class FocusAreaTaggedPage(ItemBase):
    tag = models.ForeignKey(
        "taxonomy.FocusAreaTag",
        related_name="focusarea_related_pages",
        on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        'wagtailcore.Page',
        on_delete=models.CASCADE,
        related_name="focusarea_related_items"
    )


####################################################################
# SECTORS

@register_snippet
class SectorTag(BaseTag):

    free_tagging = False

    # Name of the URL for viewing things with this Tag.
    url_name = "sector-tag"

    class Meta:
        verbose_name = _("Sector")
        verbose_name_plural = _("Sectors")

    def get_url(self, section_slug):
        """Generate the URL to this tag's view
        section_slug is the Slug of the section page the tag is within.
        e.g. 'insight'
        """
        return reverse(
            self.url_name,
            kwargs={'section_slug': section_slug, 'tag_slug': self.slug}
        )


class SectorTaggedPage(ItemBase):
    tag = models.ForeignKey(
        "taxonomy.SectorTag",
        related_name="sector_related_pages",
        on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        'wagtailcore.Page',
        on_delete=models.CASCADE,
        related_name="sector_related_items"
    )


####################################################################
# Country tags are defined in notion.models
####################################################################
