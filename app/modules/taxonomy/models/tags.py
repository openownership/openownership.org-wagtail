# 3rd party
from django.db import models
from django.conf import settings
from wagtail.core import fields
from taggit.models import ItemBase
from modelcluster.fields import ParentalKey
from wagtail.snippets.models import register_snippet
from django.utils.translation import gettext_lazy as _

from .core import BaseTag


####################################################################
# AREAS OF FOCUS

@register_snippet
class FocusAreaTag(BaseTag):

    free_tagging = False

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


####################################################################
# Country tags are defined in notion.models
####################################################################
