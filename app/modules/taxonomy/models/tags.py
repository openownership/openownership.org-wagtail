# 3rd party
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from taggit.models import ItemBase
from wagtail.core.models import Locale

from .core import BaseTag


####################################################################
# AREAS OF FOCUS

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

    def get_url(self, section_page):
        """Generate the URL to this tag's TagPage in a specific section.
        section_page is the page the TagPage is within.  e.g. 'impact'
        """
        from modules.content.models import TagPage

        page = (
            TagPage.objects.descendant_of(section_page)
            .live().public().filter(locale=Locale.get_active())
            .filter(focus_area=self).first()
        )
        if page:
            return page.get_url()
        else:
            return ''


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

    def get_url(self, section_page):
        """Generate the URL to this tag's TagPage in a specific section.
        section_page is the page the TagPage is within.  e.g. 'impact'
        """
        from modules.content.models import TagPage

        page = (
            TagPage.objects.descendant_of(section_page)
            .live().public().filter(locale=Locale.get_active())
            .filter(sector=self).first()
        )
        if page:
            return page.get_url()
        else:
            return ''


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
