from django.db import models

from modelcluster.fields import ParentalKey
from taggit.models import ItemBase
from wagtail.snippets.models import register_snippet

from .core import BaseTag


####################################################################
# AREAS OF FOCUS

@register_snippet
class FocusAreaTag(BaseTag):

    free_tagging = False

    class Meta:
        verbose_name = "Area of Focus"
        verbose_name_plural = "Areas of Focus"


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

    class Meta:
        verbose_name = "Sector"
        verbose_name_plural = "Sectors"


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