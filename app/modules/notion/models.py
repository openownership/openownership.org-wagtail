# 3rd party
from consoler import console
from django.db import models
from django.conf import settings
from wagtail.core import fields
from django.shortcuts import reverse
from taggit.models import ItemBase
from django.forms import CheckboxSelectMultiple
from wagtail.core.models import Locale, Page
from modelcluster.fields import ParentalKey
from wagtail.snippets.models import register_snippet
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalManyToManyField
from django_extensions.db.fields import AutoSlugField
from wagtail.images.edit_handlers import ImageChooserPanel
from django.utils.functional import cached_property
from wagtail.admin.edit_handlers import (
    FieldPanel, ObjectList, MultiFieldPanel, StreamFieldPanel, TabbedInterface, InlinePanel
)

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
        null=True,
        max_length=1000
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

    stage = models.CharField(  # 0 Stage
        _("Stage"),
        blank=True,
        null=True,
        max_length=255
    )

    definition_legislation_url = models.URLField(  # 1.1 Definition: Legislation URL
        _('Definition: Legislation URL'),
        blank=True,
        null=True,
        max_length=1000
    )

    coverage_legislation_url = models.URLField(  # 2.3 Coverage: Legislation URL
        _('Coverage: Legislation URL'),
        blank=True,
        null=True,
        max_length=1000
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
        null=True,
        max_length=1000
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
        null=True,
        max_length=1000
    )

    coverage_scope = ParentalManyToManyField(
        'notion.CoverageScope',
        related_name="disclosure_regimes",
        blank=True
    )


class CountryTag(NotionModel, BaseTag):

    free_tagging = False

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")

    map_image = models.ForeignKey(
        settings.IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    icon = models.CharField(
        _("Icon"),
        blank=True,
        null=True,
        max_length=25
    )

    regions = ParentalManyToManyField(
        'notion.Region',
        related_name="countries",
        blank=True
    )

    consultant = models.ForeignKey(
        'content.TeamProfilePage',
        related_name="consultant_countries",
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )

    # Stuff from the Notion Properties dict
    oo_support = models.CharField(
        _("OO Support"),
        blank=True,
        null=True,
        max_length=255
    )

    main_panels = [
        FieldPanel('name'),
        ImageChooserPanel('map_image'),
        FieldPanel('regions', widget=CheckboxSelectMultiple),
        FieldPanel('consultant', widget=CheckboxSelectMultiple),
        # FieldPanel('blurb'),
        # StreamFieldPanel('body')
    ]

    notion_panels = [
        FieldPanel('oo_support'),
        # InlinePanel('disclosure_regimes'),
    ]

    base_tabs = [
        ObjectList(main_panels, heading='Content'),
        ObjectList(notion_panels, heading='Notion'),
    ]

    edit_handler = TabbedInterface(base_tabs)

    @cached_property
    def committed_central(self):
        """The behaviour we'd like to see is that the 'Commitment to BOT/Central register'
        field is ticked for a country if the Central register field in any commitments
        for that country listed on the Commitment tracker = ticked.
        """
        for item in self.commitments.all():
            if item.central_register is True:
                return True
        return False

    @cached_property
    def committed_public(self):
        """The behaviour we'd like to see is that the 'Commitment to BOT/Central register'
        field is ticked for a country if the Central register field in any commitments
        for that country listed on the Commitment tracker = ticked.
        """
        for item in self.commitments.all():
            if item.public_register is True:
                return True
        return False

    @cached_property
    def implementation_central(self):
        """For the Implementation of BOT tab, you'll need to aggregate implementations
        for a country and then tick 'Implementation of BOT/Central register' where any
        implementations listed in the Disclosure regimes tracker have the '4 Central'
        field = Yes plus the 0 Stage field = Publish.
        """
        for item in self.disclosure_regimes.all():
            if item.central_register == "Yes" and 'Publish' in item.stage:
                return True
        return False

    @cached_property
    def implementation_public(self):
        """'Implementation of BOT/Public register' tick box, this should be ticked for a
        country page where any implementations listed where the
        '5.1 Public access' field = Yes plus the 0 Stage field = Publish.
        """
        for item in self.disclosure_regimes.all():
            if item.public_access == "Yes" and 'Publish' in item.stage:
                return True
        return False

    @cached_property
    def commitment(self):
        try:
            return self.commitments.first()
        except Exception as e:
            console.warn(e)
            console.warn(f"No commitment found for {self.name}")
            return None

    @cached_property
    def regime(self):
        try:
            return self.disclosure_regimes.first()
        except Exception as e:
            console.warn(e)
            console.warn(f"No disclosure regime found for {self.name}")
            return None

    @cached_property
    def related_pages(self):
        try:
            page_ids = [item.content_object_id for item in self.country_related_pages.all()]
            pages = Page.objects.filter(
                id__in=page_ids,
                locale=Locale.get_active()
            ).specific().live().public().order_by('-first_published_at')
        except Exception as e:
            console.warn(e)
            console.warn(f"No related pages found for {self.name}")
            return None
        else:
            return pages

    def latest_related(self, count):
        if self.related_pages is not None:
            try:
                return self.related_pages[:3]
            except Exception as e:
                console.warn(e)

        return []

    @cached_property
    def url(self):
        try:
            return reverse('country-tag', args=(self.slug, ))
        except Exception as e:
            console.warn(e)
            return "#"


class CountryTaggedPage(ItemBase):
    tag = models.ForeignKey(
        CountryTag,
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

    def __str__(self):
        return self.name


class Region(ClusterableModel):

    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")

    name = models.CharField(blank=False, null=False, max_length=255)
    slug = AutoSlugField(populate_from='name')

    def __str__(self):
        return self.name
