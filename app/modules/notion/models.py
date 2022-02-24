# 3rd party
from django.db import models
from django.conf import settings
from wagtail.core import fields
from taggit.models import ItemBase
from modelcluster.fields import ParentalKey
from wagtail.snippets.models import register_snippet
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalManyToManyField
from django_extensions.db.fields import AutoSlugField

from modules.taxonomy.models.core import BaseTag


class NotionModel(models.Model):

    class Meta:
        abstract = True

    notion_id = models.CharField(
        _("Notion ID"),
        blank=False,
        null=False,
        max_length=255,
        unique=True
    )
    notion_created = models.DateTimeField(  # created_time
        _("Notion Created"),
        blank=True,
        null=True,
    )
    notion_updated = models.DateTimeField(  # last_edited_time
        _("Notion Updated"),
        blank=True,
        null=True
    )
    archived = models.BooleanField(
        _("Archived"),
        blank=True,
        null=True
    )


@register_snippet
class Commitment(NotionModel):

    class Meta:
        verbose_name = _("Commitment")
        verbose_name_plural = _("Commitments")

    country = models.ForeignKey(
        "notion.CountryTag",
        related_name="commitments",
        to_field='notion_id',
        on_delete=models.CASCADE
    )

    date = models.DateField(
        _("Date"),
        blank=True,
        null=True
    )

    link = models.URLField(
        _("Link"),
        blank=True,
        null=True
    )

    # This field is going to be used to link to Snippets
    commitment_type_name = models.CharField(
        _("Commitment Type"),
        blank=True,
        null=True,
        max_length=255
    )

    central_register = models.BooleanField(
        _("Central Register"),
        blank=False,
        null=False,
        default=False
    )

    public_register = models.BooleanField(
        _("Public Register"),
        blank=False,
        null=False,
        default=False
    )

    summary_text = fields.RichTextField(
        _("Summary Text"),
        blank=True,
        null=True,
        features=settings.RICHTEXT_INLINE_FEATURES
    )


@register_snippet
class DisclosureRegime(NotionModel):

    class Meta:
        verbose_name = _("Disclosure Regime")
        verbose_name_plural = _("Disclosure Regimes")

    country = models.ForeignKey(
        "notion.CountryTag",
        related_name="disclosure_regimes",
        to_field='notion_id',
        on_delete=models.CASCADE
    )

    # Specified
    title = models.CharField(  # Title
        _("Title"),
        blank=True,
        null=True,
        max_length=255
    )

    definition_legislation_url = models.URLField(  # 1.1 Definition: Legislation URL
        _('Definition: Legislation URL'),
        blank=True,
        null=True
    )

    coverage_legislation_url = models.URLField(  # 2.3 Coverage: Legislation URL
        _('Coverage: Legislation URL'),
        blank=True,
        null=True
    )

    central_register = models.CharField(  # 4.1 Central register
        _("Central Register"),
        blank=True,
        null=True,
        max_length=255
    )

    public_access = models.CharField(  # 5.1 Public access
        _("Public Access"),
        blank=True,
        null=True,
        max_length=255
    )

    public_access_register_url = models.URLField(  # 5.1.1 Public access: Register URL
        _('Public Access Register URL'),
        blank=True,
        null=True
    )

    year_launched = models.CharField(  # 5.1.2 Year launched
        _("Year Launched"),
        blank=True,
        null=True,
        max_length=255
    )

    structured_data = models.CharField(  # 6.1 Structured data
        _("Structured data"),
        blank=True,
        null=True,
        max_length=255
    )

    api_available = models.CharField(  # 6.3 API available
        _("API available"),
        blank=True,
        null=True,
        max_length=255
    )

    data_in_bods = models.CharField(  # 6.4 Data published in BODS
        _("Data published in BODS"),
        blank=True,
        null=True,
        max_length=255
    )

    on_oo_register = models.BooleanField(  # 6.5 Data on OO Register
        _("On OO Register"),
        blank=False,
        null=False,
        default=False
    )

    legislation_url = models.URLField(  # 8.4 Legislation URL
        _('Legislation URL'),
        blank=True,
        null=True
    )

    coverage_scope = ParentalManyToManyField(
        'notion.CoverageScope',
        related_name="disclosure_regimes",
        blank=True
    )


@register_snippet
class CountryTag(NotionModel, BaseTag):

    free_tagging = False

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")

    icon = models.CharField(
        _("Icon"),
        blank=True,
        null=True,
        max_length=25
    )

    # Stuff from the Notion Properties dict
    oo_support = models.CharField(
        _("OO Support"),
        blank=True,
        null=True,
        max_length=255
    )


class CountryTaggedPage(ItemBase):
    tag = models.ForeignKey(
        "notion.CountryTag",
        related_name="country_related_pages",
        on_delete=models.CASCADE
    )
    content_object = ParentalKey(
        'wagtailcore.Page',
        on_delete=models.CASCADE,
        related_name="country_related_items"
    )


class CoverageScope(ClusterableModel):

    class Meta:
        verbose_name = _("Coverage Scope")
        verbose_name_plural = _("Coverage Scopes")

    name = models.CharField(blank=False, null=False, max_length=255)
    slug = AutoSlugField(populate_from='name')
