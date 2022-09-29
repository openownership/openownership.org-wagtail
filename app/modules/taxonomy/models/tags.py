# 3rd party
from django.db import models
from taggit.models import ItemBase
from modelcluster.fields import ParentalKey
from wagtail.models import Locale
from wagtailmodelchooser import register_model_chooser
from django.utils.translation import gettext_lazy as _

# Module
from .core import BaseTag


####################################################################
# AREAS OF FOCUS


@register_model_chooser
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

    def get_url(self):
        "Generate the URL to this tag's TagPage."
        from modules.content.models import TagPage

        page = (
            TagPage.objects
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


@register_model_chooser
class SectorTag(BaseTag):

    free_tagging = False

    # Name of the URL for viewing things with this Tag.
    url_name = "sector-tag"

    # Name of the URL for viewing things with this Tag.
    url_slug = 'topics'

    # Convenient way of accessing the related_name that links to pages:
    related_pages_name = 'sector_related_pages'

    class Meta:
        verbose_name = _("Topic")
        verbose_name_plural = _("Topics")

    def get_url(self):
        "Generate the URL to this tag's TagPage."
        from modules.content.models import TagPage

        page = (
            TagPage.objects
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


####################################################################################################
# Section Tags
####################################################################################################


@register_model_chooser
class SectionTag(BaseTag):

    class Meta:
        verbose_name = _("Section")
        verbose_name_plural = _("Sections")

    free_tagging = False

    # Name of the URL for viewing things with this Tag.
    url_name = "section-tag"

    # Name of the URL for viewing things with this Tag.
    url_slug = 'section-tags'

    # Convenient way of accessing the related_name that links to pages:
    related_pages_name = 'section_tag_related_pages'

    def get_url(self):
        "Generate the URL to this tag's TagPage."
        from modules.content.models.pages import SectionPage

        page = (
            SectionPage.objects
            .live().public().filter(locale=Locale.get_active())
            .filter(title=self.name).first()
        )
        if page:
            return page.get_url()
        else:
            return ''


class SectionTaggedPage(ItemBase):
    tag = models.ForeignKey(
        "taxonomy.SectionTag",
        related_name="section_tag_related_pages",
        on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        'wagtailcore.Page',
        on_delete=models.CASCADE,
        related_name="section_tag_related_items"
    )


class SectionTaggedPressLink(ItemBase):
    tag = models.ForeignKey(
        "taxonomy.SectionTag",
        related_name="section_tag_press_links",
        on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        'content.PressLink',
        on_delete=models.CASCADE,
        related_name="section_tagged"
    )


####################################################################################################
# PrincipleTags
####################################################################################################


@register_model_chooser
class PrincipleTag(BaseTag):

    free_tagging = False

    # Name of the URL for viewing things with this Tag.
    url_name = "principle-tag"

    # Name of the URL for viewing things with this Tag.
    url_slug = 'principle-tags'

    # Convenient way of accessing the related_name that links to pages:
    related_pages_name = 'principle_tag_related_pages'

    class Meta:
        verbose_name = _("Open Ownership Principle")
        verbose_name_plural = _("Open Ownership Principles")

    def get_url(self):
        "Generate the URL to this tag's TagPage."
        from modules.content.models import TagPage

        page = (
            TagPage.objects
            .live().public().filter(locale=Locale.get_active())
            .filter(principle=self).first()
        )
        if page:
            return page.get_url()
        else:
            return ''


class PrincipleTaggedPage(ItemBase):
    tag = models.ForeignKey(
        "taxonomy.PrincipleTag",
        related_name="principle_tag_related_pages",
        on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        'wagtailcore.Page',
        on_delete=models.CASCADE,
        related_name="principle_tag_related_items"
    )


####################################################################
# Country tags are defined in notion.models
####################################################################
