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

    # Name of the URL for viewing things with this Tag.
    url_slug = 'focus-areas'

    # Convenient way of accessing the related_name that links to pages:
    related_pages_name = 'focusarea_related_pages'

    class Meta:
        verbose_name = _("Area of Focus")
        verbose_name_plural = _("Areas of Focus")


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

    # Name of the URL for viewing things with this Tag.
    url_slug = 'sectors'

    # Convenient way of accessing the related_name that links to pages:
    related_pages_name = 'sector_related_pages'

    class Meta:
        verbose_name = _("Sector")
        verbose_name_plural = _("Sectors")


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
