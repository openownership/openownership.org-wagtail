# 3rd party
from consoler import console
from django.conf import settings
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.shortcuts import reverse
from django.utils.functional import cached_property
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _
from django_extensions.db.fields import AutoSlugField
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.models import ClusterableModel
from taggit.models import ItemBase
from wagtail import fields
from wagtail.admin.panels import (
    FieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
)
from wagtail.models import Locale, Page

from config.template import commitment_summary

# Project
from modules.content.blocks import TAG_PAGE_BODY_BLOCKS
from modules.notion.data import CAPITALS
from modules.taxonomy.models.core import BaseTag


class NotionModel(models.Model):
    class Meta:
        abstract = True

    notion_id = models.CharField(
        _("Notion ID"),
        blank=False,
        null=False,
        max_length=255,
        unique=True,
    )
    notion_created = models.DateTimeField(  # created_time
        _("Notion Created"),
        blank=True,
        null=True,
    )
    notion_updated = models.DateTimeField(  # last_edited_time
        _("Notion Updated"),
        blank=True,
        null=True,
    )
    archived = models.BooleanField(
        _("Archived"),
        blank=True,
        null=True,
    )

    deleted = models.BooleanField(
        _("Soft deleted"),
        blank=False,
        null=False,
        default=False,
    )


class Commitment(NotionModel):
    class Meta:
        verbose_name = _("Commitment")
        verbose_name_plural = _("Commitments")

    country = models.ForeignKey(
        "notion.CountryTag",
        related_name="commitments",
        to_field="notion_id",
        on_delete=models.CASCADE,
    )

    date = models.DateField(
        _("Date"),
        blank=True,
        null=True,
    )

    link = models.URLField(
        _("Link"),
        blank=True,
        default="",
        max_length=1000,
    )

    # This field is going to be used to link to Snippets
    commitment_type_name = models.CharField(
        _("Commitment Type"),
        blank=True,
        default="",
        max_length=255,
    )

    central_register = models.BooleanField(
        _("Central Register"),
        blank=False,
        null=False,
        default=False,
    )

    public_register = models.BooleanField(
        _("Public Register"),
        blank=False,
        null=False,
        default=False,
    )

    all_sectors = models.BooleanField(  # All sectors
        _("All sectors"),
        blank=False,
        null=False,
        default=False,
    )

    summary_text = fields.RichTextField(
        _("Summary Text"),
        blank=True,
        null=True,
        features=settings.RICHTEXT_INLINE_FEATURES,
    )

    @cached_property
    def display_summary(self):
        """
        Replaces this in the template
            {% if commitment.summary_text %}
                {% set summary = commitment.summary_text %}
            {% else %}
                {% set summary = commitment_summary(commitment.commitment_type_name, country) %}
            {% endif %}
        """
        if self.summary_text:
            return self.summary_text
        return commitment_summary(self.commitment_type_name, self.country)

    def __str__(self):
        return f"Commitment {self.id}"


class DisclosureRegime(NotionModel):
    class Meta:
        verbose_name = _("Disclosure Regime")
        verbose_name_plural = _("Disclosure Regimes")

    country = models.ForeignKey(
        "notion.CountryTag",
        related_name="disclosure_regimes",
        to_field="notion_id",
        on_delete=models.CASCADE,
    )

    # Specified
    title = models.CharField(  # Title
        _("Title"),
        blank=True,
        default="",
        max_length=255,
    )

    stage = models.CharField(  # 0 Stage (now Implementation stage)
        _("Stage"),
        blank=True,
        default="",
        max_length=255,
    )

    # 1.1 Definition: Legislation URL
    definition_legislation_url = models.TextField(
        _("Definition: Legislation URL"),
        blank=True,
        default="",
        max_length=10000,
    )

    # 2.3 Coverage: Legislation URL
    coverage_legislation_url = models.TextField(
        _("Coverage: Legislation URL"),
        blank=True,
        default="",
        max_length=10000,
    )

    # 3.1 Sufficient detail: Legislation URL
    sufficient_detail_legislation_url = models.TextField(
        _("Sufficient detail: Legislation URL"),
        blank=True,
        default="",
        max_length=10000,
    )

    # 5.4.1 Public access: Protection regime URL
    public_access_protection_regime_url = models.TextField(
        _("Public access: Protection regime URL"),
        blank=True,
        default="",
        max_length=10000,
    )

    # 5.5 Public access: Legal basis URL
    public_access_legal_basis_url = models.TextField(
        _("Public access: Legal basis URL"),
        blank=True,
        default="",
        max_length=10000,
    )

    # 9 Sanctions and enforcement: Legislation URL
    sanctions_enforcement_legislation_url = models.TextField(
        _("Public access: Legal basis URL"),
        blank=True,
        default="",
        max_length=10000,
    )

    central_register = models.CharField(  # 4.1 Central register
        _("Central Register"),
        blank=True,
        default="",
        max_length=255,
    )

    public_access = models.CharField(  # 5.1 Public access
        _("Public Access"),
        blank=True,
        default="",
        max_length=255,
    )

    public_access_register_url = (
        models.URLField(  # 5.1.1 Public access: Register URL (now Register URL)  # noqa: E501
            _("Public Access Register URL"),
            blank=True,
            default="",
            max_length=1000,
        )
    )

    year_launched = models.CharField(  # 5.1.2 Year launched
        _("Launch date"),
        blank=True,
        default="",
        max_length=255,
    )

    structured_data = models.BooleanField(  # 6.1 Structured data
        _("Structured data"),
        blank=True,
        null=True,
    )

    api_available = models.BooleanField(  # API available
        _("API available"),
        blank=True,
        null=True,
    )

    bulk_data_available = models.BooleanField(  # Bulk data available
        _("Bulk data available"),
        blank=True,
        null=True,
    )

    data_in_bods = models.BooleanField(  # 6.4 Data published in BODS
        _("Data published in BODS"),
        blank=True,
        null=True,
    )

    on_oo_register = models.BooleanField(  # 6.5 Data on OO Register
        _("On OO Register"),
        blank=True,
        null=True,
    )

    legislation_url = models.TextField(  # 8.4 Legislation URL
        _("Legislation URL"),
        blank=True,
        default="",
        max_length=10000,
    )

    coverage_scope = ParentalManyToManyField(
        "notion.CoverageScope",
        related_name="disclosure_regimes",
        blank=True,
    )

    who_can_access = ParentalManyToManyField(
        "notion.AccessTag",
        related_name="disclosure_regimes",
        blank=True,
    )

    # New fields needed as of 21/03/22

    threshold = models.DecimalField(  # 1.2 Threshold (a percentage)
        _("Threshold"),
        blank=True,
        null=True,
        max_digits=5,
        decimal_places=2,
    )

    # New fields needed as of 23/07/24

    responsible_agency = models.CharField(
        _("Responsible agency"),
        blank=True,
        default="",
        max_length=255,
    )

    agency_type = models.CharField(
        _("Agency type"),
        blank=True,
        default="",
        max_length=255,
    )

    @cached_property
    def display(self) -> bool:
        """Should this regime be displayed on the country page or included in the downloadable
        csv data?

        Returns:
            bool: Whether to include it or not
        """
        if self.implementation_stage and "Publish" in self.implementation_stage:  # noqa: SIM102
            if self.display_scope and "Subnational" not in self.display_scope:
                return True
        return False

    @cached_property
    def implementation_central(self) -> bool:
        """Best way to judge central now is to check if the 'Scope' field has the
        Full-economy tag present.
        """
        scopes = self.coverage_scope.values_list("slug", flat=True)
        return "full-economy" in scopes

    @cached_property
    def implementation_public(self) -> bool:
        """Best way to judge public now is to check if the 'Who can access'
        has the General public tag present
        """
        access = self.who_can_access.values_list("slug", flat=True)
        return "general-public" in access

    @cached_property
    def display_scope(self):
        try:
            return ", ".join([item.name for item in self.coverage_scope.all()])
        except Exception as e:
            console.warn(e)
            console.warn(f"No scope for {self.name}")
            return None

    @cached_property
    def display_register_launched(self):
        try:
            return self.year_launched
        except Exception as e:
            console.warn(e)
            console.warn(f"No year_launched for {self.name}")
            return None

    @cached_property
    def implementation_stage(self):
        try:
            if self.stage:
                return self.stage
            return ""
        except Exception as e:
            console.warn(e)
            console.warn(f"No stage for {self.name}")
            return ""

    @cached_property
    def display_structured_data(self):
        return self.structured_data

    @cached_property
    def display_data_in_bods(self):
        return self.data_in_bods

    @cached_property
    def display_api(self):
        return self.api_available

    @cached_property
    def display_oo_register(self):
        return self.on_oo_register

    @cached_property
    def display_central_register(self):
        try:
            return self.central_register
        except Exception as e:
            console.warn(e)
            console.warn(f"No central_register for {self.name}")
            return None

    @cached_property
    def implementation_title(self):
        try:
            return self.title
        except Exception as e:
            console.warn(e)
            console.warn(f"No title for {self.name}")
            return None

    @cached_property
    def implementation_title_link(self):
        try:
            return self.public_access_register_url
        except Exception as e:
            console.warn(e)
            console.warn(f"No public_access_register_url for {self.name}")
            return None

    @cached_property
    def display_threshold(self):
        if self.threshold is None:
            return ""
        value = self.threshold.normalize()
        if value == value.to_integral_value():
            return f"{value:.0f}%"
        return f"{value}%"

    def __str__(self):
        return self.title


class CountryTag(NotionModel, BaseTag):
    # Values for oo_support that count as OO being "engaged" in that country:
    OO_ENGAGED_VALUES = (
        "High",
        "Medium",
        "Standard",
        "Past engagement",
    )

    free_tagging = False

    class Meta:
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")

    body = fields.StreamField(TAG_PAGE_BODY_BLOCKS, blank=True, use_json_field=True)

    blurb = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_INLINE_FEATURES,
    )

    oo_ongoing_work_title = models.CharField(
        _("Open Ownership Ongoing Work Title"),
        blank=True,
        default="",
        max_length=255,
    )

    oo_ongoing_work_body = fields.RichTextField(
        _("Open Ownership Ongoing Work Body"),
        blank=True,
        null=True,
        features=settings.RICHTEXT_INLINE_FEATURES,
    )

    map_image = models.ForeignKey(
        settings.IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    icon = models.CharField(
        _("Icon"),
        blank=True,
        default="",
        max_length=25,
    )

    regions = models.ManyToManyField(
        "notion.Region",
        related_name="countries",
        blank=True,
    )

    consultant = models.ForeignKey(
        "content.TeamProfilePage",
        related_name="consultant_countries",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    # Stuff from the Notion Properties dict
    oo_support = models.CharField(
        _("OO Support"),
        blank=True,
        default="",
        max_length=255,
    )

    iso2 = models.CharField(
        _("ISO2"),
        blank=True,
        default="",
        max_length=10,
    )

    main_panels = [
        FieldPanel("name"),
        FieldPanel("blurb"),
        FieldPanel("oo_ongoing_work_title"),
        FieldPanel("oo_ongoing_work_body"),
        FieldPanel("map_image"),
        FieldPanel("regions", widget=CheckboxSelectMultiple),
        PageChooserPanel("consultant"),
        # FieldPanel('blurb'),
        # FieldPanel('body')
    ]

    notion_panels = [
        FieldPanel("oo_support"),
        # InlinePanel('disclosure_regimes'),
    ]

    base_tabs = [
        ObjectList(main_panels, heading="Content"),
        ObjectList(notion_panels, heading="Notion"),
    ]

    edit_handler = TabbedInterface(base_tabs)

    @cached_property
    def last_updated(self):
        dates = [self.notion_updated]
        for item in self.regimes:
            if item is not None and item.notion_updated is not None:
                dates.append(item.notion_updated)  # noqa: PERF401
        for item in self.all_commitments:
            if item is not None and item.notion_updated is not None:
                dates.append(item.notion_updated)  # noqa: PERF401
        return max(dates)

    @cached_property
    def committed(self):
        return bool(len(self.all_commitments))

    @cached_property
    def involved(self):
        VALID = [
            "Standard",
            "Medium",
            "High",
            "Past engagement",
        ]
        return self.oo_support in VALID

    @cached_property
    def involvement(self):
        if not self.involved:
            return "None"

        value = self.oo_support
        if value == "Past engagement":
            return "Historic"
        return "Current"

    @cached_property
    def combined_commitments(self):
        """Adapted from the OG csv generator

        Returns:
            dict: Some stuff in a dict ¯\\_(ツ)_/¯
        """
        central_register = any(commitment.central_register for commitment in self.all_commitments)
        public_register = any(commitment.public_register for commitment in self.all_commitments)
        all_sectors = any(commitment.all_sectors for commitment in self.all_commitments)
        score = 0
        level = 0

        if central_register:
            score += 1
        if public_register:
            score += 1
        if all_sectors:
            score += 1

        # We map to a 0-1-2 scale, where you have to make 2/3 of central, public
        # and all sectors to get 1, or all three to get 2.
        if score == 2:
            level = 1
        if score == 3:
            level = 2

        return {
            "central": central_register,
            "public": public_register,
            "all_sectors": all_sectors,
            "level": level,
            "html": self._commitments_summary_html,
        }

    @cached_property
    def _commitments_summary_html(self):
        commitments = self.all_commitments
        html = "<ul>"
        for commitment in commitments:
            html += f"<li>{commitment.display_summary}</li>"
        html += "</ul>"
        return html

    @cached_property
    def category(self):
        """
        Returns a string or None:

        - "liveregister": Has any implmentations where stage is publish
        - "implementing": Has any implementations where stage is not publish
        - "planned": Only has commitments, no implementations
        - None: Has no commitments and no implementations
        """
        category = None

        subnational = CoverageScope.objects.get(name="Subnational")
        disclosure_regimes = self.disclosure_regimes.all()

        # Any "publish" implementations at all?
        for item in disclosure_regimes:
            if item.stage and "Publish" in item.stage:  # noqa: SIM102
                if subnational not in item.coverage_scope.all():
                    category = "liveregister"
                    break

        if category is None:
            # There were no "publish" implementations, so:
            if disclosure_regimes:
                # There are some non-publish implementations
                category = "implementing"
            elif self.commitments.count() > 0:
                # It has commitments but no implementations
                category = "planned"

        return category

    @cached_property
    def category_display(self):
        "Returns a friendly version of the category string."
        labels = {
            "implementing": _("Implementing"),
            "liveregister": _("Live register"),
            "planned": _("Planned"),
        }
        if self.category in labels:
            return labels[self.category]
        return ""

    @cached_property
    def committed_central(self):
        """The behaviour we'd like to see is that the 'Commitment to BOT/Central register'
        field is ticked for a country if the Central register field in any commitments
        for that country listed on the Commitment tracker = ticked.
        """
        return any(item.central_register is True for item in self.commitments.all())

    @cached_property
    def committed_public(self):
        """The behaviour we'd like to see is that the 'Commitment to BOT/Central register'
        field is ticked for a country if the Central register field in any commitments
        for that country listed on the Commitment tracker = ticked.
        """
        return any(item.public_register is True for item in self.commitments.all())

    @cached_property
    def implementation_central(self):
        """For the Implementation of BOT tab, you'll need to aggregate implementations
        for a country and then tick 'Implementation of BOT/Central register' where any
        implementations listed in the Disclosure regimes tracker have the '4 Central'
        field = Yes plus the 0 Stage field = Publish.
        """
        subnational = CoverageScope.objects.get(name="Subnational")
        for item in self.disclosure_regimes.all():
            if item.central_register == "Yes" and item.stage and "Publish" in item.stage:  # noqa: SIM102
                if subnational not in item.coverage_scope.all():
                    return True
        return False

    @cached_property
    def implementation_public(self):
        """'Implementation of BOT/Public register' tick box, this should be ticked for a
        country page where any implementations listed where the
        '5.1 Public access' field = Yes plus the 0 Stage field = Publish.
        """
        subnational = CoverageScope.objects.get(name="Subnational")
        for item in self.disclosure_regimes.all():
            if item.public_access == "Yes" and item.stage and "Publish" in item.stage:  # noqa: SIM102
                if subnational not in item.coverage_scope.all():
                    return True
        return False

    @cached_property
    def lat(self):
        try:
            return CAPITALS[self.iso2]["lat"]
        except Exception as e:
            console.warn(e)

    @cached_property
    def lon(self):
        try:
            return CAPITALS[self.iso2]["lon"]
        except Exception as e:
            console.warn(e)

    @cached_property
    def commitment(self):
        try:
            return self.commitments.first()
        except Exception as e:
            console.warn(e)
            console.warn(f"No commitment found for {self.name}")
            return None

    @cached_property
    def all_commitments(self):
        try:
            return self.commitments.filter(deleted=False).all()
        except Exception as e:
            console.warn(e)
            console.warn(f"No commitments found for {self.name}")
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
    def regimes(self):
        try:
            return self.disclosure_regimes.all()
        except Exception as e:
            console.warn(e)
            console.warn(f"No disclosure regimes found for {self.name}")
            return None

    @cached_property
    def first_public_regime_with_url(self):
        """Find the first regime that has a value for both
        public_access_register_url and title, and `stage` contains 'Publish'
        """
        rv = {}
        for item in self.regimes.filter(stage__icontains="Publish"):
            scope_names = [scope.name for scope in item.coverage_scope.all()]
            if "Subnational" not in scope_names:  # noqa: SIM102
                if item.title and item.public_access_register_url:
                    rv["title"] = item.title
                    rv["url"] = item.public_access_register_url
                    return rv
        return ""

    @cached_property
    def first_central_regime(self):
        """Find the first regime that has...
        * YES for central_register
        * a title
        * `stage` contains 'Publish'
        * COVERAGE SCOPE
        """
        rv = {}
        for item in self.regimes.filter(stage__icontains="Publish", central_register="Yes"):
            try:
                scope_names = [scope.name for scope in item.coverage_scope.all()]
                if "Subnational" not in scope_names:
                    if item.title:
                        rv["title"] = item.title

                    if item.public_access_register_url:
                        rv["url"] = item.public_access_register_url
            except Exception as e:
                console.warn(e)

        return rv

    @cached_property
    def display_date_related_pages(self):
        """Try to return related pages ordered by display date."""
        try:
            page_ids = [item.content_object_id for item in self.country_related_pages.all()]
            pages = (
                Page.objects.filter(
                    id__in=page_ids,
                    locale=Locale.get_active(),
                )
                .specific()
                .live()
                .public()
            )
            pages = sorted(pages, key=lambda x: x.display_date, reverse=True)
        except Exception as e:
            console.warn(e)
            console.warn(f"No related pages found for {self.name}")
            return self.related_pages
        else:
            return pages

    @cached_property
    def related_pages(self):
        try:
            page_ids = [item.content_object_id for item in self.country_related_pages.all()]
            pages = (
                Page.objects.filter(
                    id__in=page_ids,
                    locale=Locale.get_active(),
                )
                .specific()
                .live()
                .public()
                .order_by("-first_published_at")
            )
        except Exception as e:
            console.warn(e)
            console.warn(f"No related pages found for {self.name}")
            return []
        else:
            return pages

    def latest_related(self, count):  # noqa: ARG002
        if self.display_date_related_pages:
            try:
                return self.display_date_related_pages[:3]
            except Exception as e:
                console.warn(e)

        return []

    @cached_property
    def url(self):
        try:
            return reverse("country-tag", args=(self.slug,))
        except Exception as e:
            console.warn(e)
            return "#"

    @cached_property
    def data_export_url(self):
        try:
            return reverse("country-export", args=(self.slug,))
        except Exception as e:
            console.warn(e)
            return "#"

    @cached_property
    def is_engaged(self):
        return self.oo_support in self.OO_ENGAGED_VALUES

    def __str__(self):
        return self.name


class CountryTaggedPage(ItemBase):
    tag = models.ForeignKey(
        CountryTag,
        related_name="country_related_pages",
        on_delete=models.CASCADE,
    )
    content_object = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="country_related_items",
    )


class CoverageScope(ClusterableModel):
    class Meta:
        verbose_name = _("Coverage Scope")
        verbose_name_plural = _("Coverage Scopes")

    name = models.CharField(blank=False, null=False, max_length=255)
    slug = AutoSlugField(populate_from="name")

    def __str__(self):
        return self.name


class AccessTag(ClusterableModel):
    class Meta:
        verbose_name = _("Access Tag")
        verbose_name_plural = _("Access Tags")

    name = models.CharField(blank=False, null=False, max_length=255)
    slug = AutoSlugField(populate_from="name")

    def __str__(self):
        return self.name


class Region(ClusterableModel):
    class Meta:
        verbose_name = _("Region")
        verbose_name_plural = _("Regions")

    name = models.CharField(blank=False, null=False, max_length=255)
    slug = AutoSlugField(populate_from="name")

    blurb = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_INLINE_FEATURES,
    )

    def __str__(self):
        return self.name


####################################################################################################
# BOT impact tracker vocabularies
####################################################################################################


class ImpactTagBase(ClusterableModel):
    """Shared shape for the tracker's multi-select vocabularies.

    Options are created from whatever Notion sends, so the option lists on this
    side are only ever as tidy as the ones in the source database.
    """

    class Meta:
        abstract = True
        ordering = ("name",)

    name = models.CharField(blank=False, null=False, max_length=255, unique=True)
    slug = AutoSlugField(populate_from="name")

    def __str__(self):
        return self.name


class DataUserTag(ImpactTagBase):
    class Meta(ImpactTagBase.Meta):
        verbose_name = _("Data User")
        verbose_name_plural = _("Data Users")


class UsabilityThemeTag(ImpactTagBase):
    class Meta(ImpactTagBase.Meta):
        verbose_name = _("Usability Theme")
        verbose_name_plural = _("Usability Themes")


class ImpactTypeTag(ImpactTagBase):
    class Meta(ImpactTagBase.Meta):
        verbose_name = _("Impact Type")
        verbose_name_plural = _("Impact Types")


class ResourceTypeTag(ImpactTagBase):
    class Meta(ImpactTagBase.Meta):
        verbose_name = _("Resource Type")
        verbose_name_plural = _("Resource Types")


class PolicyAreaTag(ImpactTagBase):
    class Meta(ImpactTagBase.Meta):
        verbose_name = _("Policy Area")
        verbose_name_plural = _("Policy Areas")


####################################################################################################
# BOT impact tracker
####################################################################################################


class ImpactEntryQuerySet(models.QuerySet):
    def publishable(self):
        """Entries that may appear publicly.

        Three conditions: Open Ownership cleared it, it still exists in Notion,
        and it has a link. Open Ownership asked for records with no link to be
        left out entirely, since the point of a record is to send a reader to
        its source.
        """
        return self.filter(publish=True, deleted=False).exclude(source_url="")

    def withheld_for_no_link(self):
        """Cleared for publication, but with nothing to point a reader at."""
        return self.filter(publish=True, deleted=False, source_url="")


class ImpactEntry(NotionModel):
    """A single recorded use or impact of beneficial ownership data.

    Sourced from the `BOT impact tracker` Notion database. Only entries with
    `publish` set are cleared by Open Ownership for display on the site; the
    rest are synced so the record stays complete but should stay hidden.
    """

    objects = ImpactEntryQuerySet.as_manager()

    # Open Ownership aim for summaries of about this length. Notion cannot
    # enforce it, so it is applied here at display time rather than relied on.
    SUMMARY_WORDS = 50

    class Meta:
        verbose_name = _("Impact Entry")
        verbose_name_plural = _("Impact Entries")
        ordering = ("-year", "description")

    description = models.TextField(  # One sentence description (P)
        _("Description"),
        blank=False,
        default="",
    )

    summary = models.TextField(  # Short summary (P)
        _("Short summary"),
        blank=True,
        default="",
    )

    lessons = models.TextField(  # Lessons
        _("Lessons"),
        blank=True,
        default="",
    )

    oo_outputs_used_in = models.TextField(  # OO outputs used in
        _("OO outputs used in"),
        blank=True,
        default="",
    )

    presentations_used_in = models.TextField(  # Presentations/slide decks used in
        _("Presentations used in"),
        blank=True,
        default="",
    )

    source_url = models.URLField(  # Source URL (P)
        _("Source URL"),
        blank=True,
        default="",
        max_length=1000,
    )

    year = models.PositiveIntegerField(  # Year (P)
        _("Year"),
        blank=True,
        null=True,
    )

    publish = models.BooleanField(  # Publish?
        _("Cleared for publication"),
        blank=False,
        null=False,
        default=False,
    )

    oo_influence = models.BooleanField(  # OO's influence
        _("OO influence"),
        blank=False,
        null=False,
        default=False,
    )

    tangible_impact = models.BooleanField(  # Tangible impact
        _("Tangible impact"),
        blank=False,
        null=False,
        default=False,
    )

    international = models.BooleanField(  # International
        _("International"),
        blank=False,
        null=False,
        default=False,
    )

    # Housekeeping flags Open Ownership use while they tidy the tracker. Synced
    # so the record matches Notion, but nothing on this side acts on them.
    source_archived = models.BooleanField(  # Archive
        _("Archived in Notion"),
        blank=False,
        null=False,
        default=False,
    )

    source_marked_old = models.BooleanField(  # [TEMP] Old?
        _("Marked old in Notion"),
        blank=False,
        null=False,
        default=False,
    )

    archived_types = models.CharField(  # [Archive]
        _("Archived types"),
        blank=True,
        default="",
        max_length=1000,
    )

    countries = models.ManyToManyField(  # Jurisdiction(s) (P)
        "notion.CountryTag",
        related_name="impact_entries",
        blank=True,
    )

    regimes = models.ManyToManyField(  # Disclosure regime(s)
        "notion.DisclosureRegime",
        related_name="impact_entries",
        blank=True,
    )

    data_users = models.ManyToManyField(  # Data user
        "notion.DataUserTag",
        related_name="impact_entries",
        blank=True,
    )

    usability_themes = models.ManyToManyField(  # Usability theme(s)
        "notion.UsabilityThemeTag",
        related_name="impact_entries",
        blank=True,
    )

    impact_types = models.ManyToManyField(  # Type
        "notion.ImpactTypeTag",
        related_name="impact_entries",
        blank=True,
    )

    resource_types = models.ManyToManyField(  # Type of resource (P)
        "notion.ResourceTypeTag",
        related_name="impact_entries",
        blank=True,
    )

    policy_areas = models.ManyToManyField(  # Policy area (P)
        "notion.PolicyAreaTag",
        related_name="impact_entries",
        blank=True,
    )

    def __str__(self):
        return self.description[:100]

    def get_absolute_url(self) -> str:
        """The record's own page.

        Keyed on the Notion id because a record has no title to build a slug
        from. It is a UUID, so one record's URL gives no clue to the next.
        """
        return reverse("evidence-detail", kwargs={"notion_id": self.notion_id})

    @cached_property
    def display_summary(self) -> str:
        """The summary cut to a card-sized length.

        Trimmed on words rather than characters: a character count behaves
        differently at every font width, so it is not something an editor can
        write to.
        """
        return Truncator(self.summary).words(self.SUMMARY_WORDS, truncate="…")

    @cached_property
    def display_regions(self) -> list:
        """Region names, reached through the entry's jurisdictions.

        An entry has no region of its own. Several jurisdictions can share one,
        so the names are deduplicated before display.
        """
        names = set()
        for country in self.countries.all():
            names.update(country.regions.values_list("name", flat=True))
        return sorted(name for name in names if name)

    @cached_property
    def display_attachments(self):
        """Attachments worth showing: anything we hold or can link to."""
        return [item for item in self.attachments.all() if item.is_resolved]


class ImpactAttachment(models.Model):
    """One item from an impact entry's Notion files column.

    A single entry can carry several attachments of mixed types, so each one is
    its own row rather than a field on the entry. `fingerprint` is what makes a
    re-sync idempotent: Notion re-signs its file URLs on every fetch, so the
    query string changes each time while the path stays put.
    """

    class Meta:
        verbose_name = _("Impact Attachment")
        verbose_name_plural = _("Impact Attachments")
        ordering = ("sort_order", "pk")
        constraints = [
            models.UniqueConstraint(
                fields=["entry", "fingerprint"],
                name="unique_attachment_per_entry",
            ),
        ]

    KIND_DOCUMENT = "document"
    KIND_IMAGE = "image"
    KIND_LINK = "link"
    KIND_CHOICES = [
        (KIND_DOCUMENT, _("Document")),
        (KIND_IMAGE, _("Image")),
        (KIND_LINK, _("Link")),
    ]

    entry = models.ForeignKey(
        "notion.ImpactEntry",
        related_name="attachments",
        on_delete=models.CASCADE,
    )

    sort_order = models.PositiveIntegerField(
        _("Sort order"),
        blank=False,
        null=False,
        default=0,
    )

    kind = models.CharField(
        _("Kind"),
        blank=False,
        null=False,
        max_length=20,
        choices=KIND_CHOICES,
    )

    # Notion's own label for the item. Usually a filename or a URL, but authors
    # sometimes type a human label instead, so it is never assumed to be either.
    label = models.CharField(
        _("Label"),
        blank=True,
        default="",
        max_length=500,
    )

    fingerprint = models.CharField(
        _("Fingerprint"),
        blank=False,
        null=False,
        max_length=1000,
    )

    url = models.URLField(
        _("URL"),
        blank=True,
        default="",
        max_length=2000,
    )

    document = models.ForeignKey(
        settings.WAGTAILDOCS_DOCUMENT_MODEL,
        related_name="impact_attachments",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    image = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        related_name="impact_attachments",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    fetch_error = models.TextField(
        _("Fetch error"),
        blank=True,
        default="",
    )

    def __str__(self):
        return self.label or self.url or self.fingerprint

    @property
    def is_resolved(self) -> bool:
        """Whether this attachment has something we can actually show."""
        if self.kind == self.KIND_DOCUMENT:
            return self.document_id is not None
        if self.kind == self.KIND_IMAGE:
            return self.image_id is not None
        return bool(self.url)

    @property
    def display_label(self) -> str:
        """A label safe to put in front of a reader."""
        if self.label and not self.label.startswith(("http://", "https://")):
            return self.label
        if self.kind == self.KIND_DOCUMENT and self.document_id:
            return self.document.title
        if self.kind == self.KIND_IMAGE and self.image_id:
            return self.image.title
        return self.label or self.url
