# -*- coding: utf-8 -*-

"""
content.models.pages
~~~~~~~~~~~~~~~~~
Site-wide page models.
"""

# stdlib
import copy
from itertools import chain

from bs4 import BeautifulSoup
from consoler import console
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

# 3rd party
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from wagtail import fields
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    PageChooserPanel,
)
from wagtail.blocks import StreamBlock
from wagtail.contrib.search_promotions.models import Query
from wagtail.models import Locale, Orderable, Page
from wagtail.search import index

# Project
from config.template import url_from_path
from modules.content.blocks import (
    ADDITIONAL_CONTENT_BLOCKS,
    ARTICLE_PAGE_BODY_BLOCKS,
    HOME_PAGE_BLOCKS,
    SECTION_PAGE_BLOCKS,
    TAG_PAGE_BODY_BLOCKS,
    TEAM_PROFILE_PAGE_BODY_BLOCKS,
    HighlightPagesBlock,
)
from modules.content.blocks.stream import FootnoteBlock, GlossaryItemBlock
from modules.feedback.models import FeedbackMixin
from modules.notion.helpers import countries_json, map_json
from modules.notion.models import CountryTag, Region
from modules.stats.mixins import Countable
from modules.taxonomy.edit_handlers import PublicationTypeFieldPanel
from modules.taxonomy.models import PublicationType

# Module
from .mixins import PageHeroMixin, TaggedAuthorsPageMixin, TaggedPageMixin
from .page_types import BasePage, ContentPageType, IndexPageType, LandingPageType

####################################################################################################
# Landing type pages
####################################################################################################


class HomePage(PageHeroMixin, LandingPageType):
    class Meta:
        verbose_name = _("Home page")

    template: str = "content/home.jinja"

    # Only allow at root level:
    parent_page_types: list = ["wagtailcore.Page"]
    subpage_types: list = [
        "content.JobsIndexPage",
        "content.SectionPage",
        "content.SectionListingPage",
        "content.UtilityPage",
        "content.NewsIndexPage",
        "content.BlogIndexPage",
        "content.MapPage",
        "content.TaxonomyPage",
        "content.PublicationsIndexPage",
        "content.PressLinksPage",
    ]
    max_count = 1

    search_fields: list = Page.search_fields + []

    body = fields.StreamField(HOME_PAGE_BLOCKS, blank=True, use_json_field=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
    ]

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        context["body_classes"] = "home-page"
        context["is_home"] = True
        return context

    def get_meta_title(self) -> str:
        meta_title = super().get_meta_title()
        if meta_title == "Home":
            return settings.WAGTAIL_SITE_NAME
        return meta_title

    @classmethod
    def can_create_at(cls, parent) -> bool:
        return super().can_create_at(parent) and not cls.objects.exists()


class SectionPage(PageHeroMixin, LandingPageType):
    """For the top-level section pages, like Impact, Resarch, Implement."""

    class Meta:
        verbose_name = _("Section (Impact, etc.)")

    template: str = "content/section_page.jinja"

    parent_page_types: list = ["content.HomePage"]
    subpage_types: list = [
        "content.ArticlePage",
        "content.GlossaryPage",
        "content.LatestSectionContentPage",
        "content.PressLinksPage",
        "content.UtilityPage",
    ]

    search_fields: list = BasePage.search_fields + [
        index.SearchField("body"),
    ]

    body = fields.StreamField(SECTION_PAGE_BLOCKS, blank=True, use_json_field=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
    ]

    @cached_property
    def press_links_page_url(self):
        """
        Get the URL for the PressLinksPage within this section, if any.
        I couldn't think how else to do this.
        """
        page = PressLinksPage.objects.filter(locale=Locale.get_active()).first()
        if page:
            return page.url
        return ""


class SectionListingPage(SectionPage):
    """A top-level section page, but the body only lists its child
    pages - it has no other configurable body content.

    Used for the About section page.
    """

    class Meta:
        verbose_name = _("Section listing (About)")

    search_fields: list = BasePage.search_fields + []

    template: str = "content/section_listing_page.jinja"
    parent_page_types: list = ["content.HomePage"]
    subpage_types: list = [
        "content.ArticlePage",
        "content.JobsIndexPage",
        "content.LatestSectionContentPage",
        "content.PressLinksPage",
        "content.TeamPage",
    ]

    show_child_pages = models.BooleanField(
        default=True,
        help_text=_("Display cards linking to all the child pages"),
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("show_child_pages"),
    ]

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        if self.show_child_pages:
            context["child_pages"] = self.get_children().live().public()
        else:
            context["child_pages"] = self.get_children().none()
        return context

    @cached_property
    def press_links_page_url(self):
        """
        Get the URL for the PressLinksPage within this section, if any.
        I couldn't think how else to do this.
        """
        page = PressLinksPage.objects.filter(locale=Locale.get_active()).first()
        if page:
            return page.url
        return ""


####################################################################################################
# Content type pages
# All sharing the same kinds of tags etc.
####################################################################################################


class ArticlePage(ContentPageType):
    """Basic page of content, used for things like About pages.

    Differs from all the other Content Pages in that, as it has no tags
    or authors, there's no point having the SimilarContentBlock.
    """

    template = "content/article_page.jinja"

    parent_page_types: list = ["content.SectionListingPage", "content.SectionPage"]
    subpage_types: list = []

    body = fields.StreamField(ARTICLE_PAGE_BODY_BLOCKS, blank=True, use_json_field=True)

    highlight_pages = fields.StreamField(
        StreamBlock(
            [
                ("highlight_pages", HighlightPagesBlock()),
            ],
            max_num=1,
        ),
        blank=True,
        use_json_field=True,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
        FieldPanel("highlight_pages"),
    ]


class NewsArticlePage(TaggedAuthorsPageMixin, Countable, ContentPageType):
    """An article in the Research > News section."""

    template = "content/blog_news_article_page.jinja"
    parent_page_types: list = ["content.NewsIndexPage"]
    subpage_types: list = []

    search_fields = ContentPageType.search_fields + TaggedAuthorsPageMixin.search_fields

    def get_publication_type_choices(self):
        """We now allow any publication type category on these pages."""
        return PublicationType.objects.all()

    @cached_property
    def page_type(self):
        return _("News article")

    @cached_property
    def index_link(self):
        try:
            p = self.get_parent()
            return p.url
        except Exception as e:
            console.warn(e)


class BlogArticlePage(TaggedAuthorsPageMixin, Countable, ContentPageType):
    """An article in the Research > Blog section."""

    template = "content/blog_news_article_page.jinja"
    parent_page_types: list = ["content.BlogIndexPage"]
    subpage_types: list = []

    search_fields = ContentPageType.search_fields + TaggedAuthorsPageMixin.search_fields

    # Also has:
    # author_relationships from BlogArticleAuthorRelationship
    # authors from AuthorsPageMixin

    class Meta:
        verbose_name = _("Blog post page")

    def get_publication_type_choices(self):
        """We now allow any publication type category on these pages."""
        return PublicationType.objects.all()

    @cached_property
    def page_type(self):
        return _("Blog post")

    @cached_property
    def index_link(self):
        try:
            p = self.get_parent()
            return p.url
        except Exception as e:
            console.warn(e)


class UtilityPage(ContentPageType):
    """Used, I think, for pages like Privacy, Terms, etc."""

    template = "content/utility_page.jinja"

    parent_page_types: list = ["content.HomePage", "content.SectionPage"]
    subpage_types: list = []

    intro = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_INLINE_FEATURES,
    )

    content_panels = (
        BasePage.content_panels
        + [
            FieldPanel("intro"),
        ]
        + ContentPageType.model_content_panels
    )

    @property
    def show_display_date_on_card(self):
        "Whether to show the date when displaying a card about this page."
        return False


class JobPage(TaggedPageMixin, ContentPageType):
    template = "content/job_page.jinja"
    parent_page_types: list = ["content.JobsIndexPage"]
    subpage_types: list = []

    search_fields: list = ContentPageType.search_fields + [
        index.SearchField("location"),
    ]

    application_url = models.URLField(
        blank=True,
        max_length=255,
        help_text="URL of the page where people can apply for the job",
        verbose_name="Application URL",
    )
    application_deadline = models.DateField(blank=True, null=True)

    location = models.CharField(max_length=255, blank=True)

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("application_deadline"),
                FieldPanel("application_url"),
                FieldPanel("location"),
            ],
            heading="Application details",
        ),
    ] + ContentPageType.content_panels

    # Does not use the countries that TaggedPageMixin has:
    about_panels = [
        PublicationTypeFieldPanel("publication_type", heading=_("Content type")),
        FieldPanel("areas_of_focus", heading=_("Areas of focus")),
        FieldPanel("sectors", heading=_("Topics")),
    ]

    @cached_property
    def human_application_deadline(self):
        if self.application_deadline:
            return self.application_deadline.strftime("%d %B %Y")

    def get_publication_type_choices(self):
        """We now allow any publication type category on these pages."""
        return PublicationType.objects.all()

    @cached_property
    def page_type(self):
        return _("Job")

    @cached_property
    def index_link(self):
        try:
            p = self.get_parent()
            return p.url
        except Exception as e:
            console.warn(e)


####################################################################################################
# PublicationPages
####################################################################################################


class PublicationFrontPageForm(WagtailAdminPageForm):
    "So that we can re-name the default title field."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        title = self.fields["title"]
        title.label = _("Publication title")
        title.help_text = _("The publication title as you'd like it to be seen by the public")


class PublicationFrontPage(TaggedAuthorsPageMixin, Countable, FeedbackMixin, BasePage):
    """The front and main page of a Publication.

    This defines all the information about the Publication as a whole.
    Its child pages (PublicationInnerPage) contain any subsequent pages
    of content within it.
    """

    base_form_class = PublicationFrontPageForm

    template = "content/publication_front_page.jinja"
    parent_page_types: list = ["content.PublicationsIndexPage"]
    subpage_types: list = ["content.PublicationInnerPage"]

    search_fields = ContentPageType.search_fields + TaggedAuthorsPageMixin.search_fields

    cached_title = ""

    page_title = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("e.g. ‘Introduction’"),
    )

    cover_image = models.ForeignKey(
        settings.IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    external_link = models.URLField(
        blank=True,
        null=True,
        help_text="Use document download OR external link",
    )

    download_document = models.ForeignKey(
        settings.WAGTAILDOCS_DOCUMENT_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    summary_title = models.CharField(
        max_length=255,
        blank=True,
        default=_("Summary"),
    )
    summary = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_BODY_FEATURES,
    )

    outcomes_title = models.CharField(
        max_length=255,
        blank=True,
        default=_("Key Learning Outcomes"),
    )
    outcomes = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_BODY_FEATURES,
        verbose_name=_("Key Learning Outcomes"),
    )

    impact_title = models.CharField(
        max_length=255,
        blank=True,
        default=_("Benefit / Impact"),
    )
    impact = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_BODY_FEATURES,
        verbose_name=_("Benefit / Impact"),
    )

    show_display_date = models.BooleanField(
        default=True,
        help_text=_("Should this date be displayed as the publication's date?"),
        verbose_name=_("Show Display Date?"),
    )

    additional_content = fields.StreamField(
        ADDITIONAL_CONTENT_BLOCKS,
        blank=True,
        use_json_field=True,
    )

    # Also has:
    # author_relationships from PublicationAuthorRelationship
    # authors from AuthorsPageMixin

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("page_title"),
            ],
            heading=_("Titles"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("cover_image"),
                FieldPanel("download_document"),
                FieldPanel("external_link"),
            ],
            heading=_("Cover and document"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("summary_title"),
                FieldPanel("summary"),
                FieldPanel("outcomes_title"),
                FieldPanel("outcomes"),
                FieldPanel("impact_title"),
                FieldPanel("impact"),
            ],
            heading=_("Content"),
        ),
        FieldPanel("additional_content"),
    ]

    settings_panels = [
        MultiFieldPanel(
            [
                FieldPanel("display_date"),
                FieldPanel("show_display_date"),
            ],
            heading=_("Display date"),
        ),
    ] + Page.settings_panels

    search_fields = BasePage.search_fields + [
        index.SearchField("summary"),
        index.SearchField("outcomes"),
        index.SearchField("impact"),
    ]

    @property
    def date(self):
        return self.display_date

    @cached_property
    def human_display_date(self):
        if self.display_date:
            return self.display_date.strftime("%d %B %Y")
        return ""

    @property
    def display_title(self):
        "Title of the publication"
        return self.title

    @property
    def show_display_date_on_card(self):
        "Whether to show the date when displaying a card about this page."
        return self.show_display_date

    @property
    def show_display_date_on_page(self):
        "Whether to show the date when displaying the page."
        return self.show_display_date

    @cached_property
    def page_type(self):
        return _("Publication")

    @cached_property
    def index_link(self):
        try:
            p = self.get_parent()
            return p.url
        except Exception as e:
            console.warn(e)

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        context["menu_pages"] = self._get_menu_pages()

        return context

    def get_publication_type_choices(self):
        """We now allow any publication type category on these pages."""
        return PublicationType.objects.all()

    def get_next_page(self):
        """Returns the first InnerPage in this publication
        Or None if there isn't one.
        """
        return self.get_children().live().public().first()

    def _get_menu_pages(self):
        # We want to use the page title for the `title` in the menu, so:
        # (Can't just use self, because if we change its title then that
        # new title gets used as the actual title in <h1> in the template!)
        first_page = copy.copy(self)
        first_page.cached_title = first_page.title
        first_page.title = first_page.specific.page_title

        menu_pages = [first_page]
        children = self.get_children().live().public().filter(locale=Locale.get_active())
        for child in children:
            menu_pages.append(child)
        return menu_pages


class PublicationInnerPageForm(WagtailAdminPageForm):
    "So that we can re-name the default title field."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        title = self.fields["title"]
        title.label = _("Page title")
        title.help_text = _(
            "Short title of this page within the publication e.g. "
            "'Overview', 'Comprehensive coverage', etc.",
        )


class PublicationInnerPage(ContentPageType):
    """A page within a Publication.

    A Publication has a PublicationFrontPage as its first page, which
    defines all the general info about the publication.
    """

    base_form_class = PublicationInnerPageForm

    template = "content/publication_inner_page.jinja"
    parent_page_types: list = ["content.PublicationFrontPage"]
    subpage_types: list = []

    # So we don't show display_date:
    settings_panels = Page.settings_panels

    # Override this to add footnotes
    BLOCKS = ARTICLE_PAGE_BODY_BLOCKS + [
        ("footnote", FootnoteBlock()),
    ]
    body = fields.StreamField(BLOCKS, blank=True, use_json_field=True)

    def __str__(self):
        try:
            return f"{self.get_parent().title}: {self.title}"
        except Exception:
            return "New publication inner page"

    def get_context(self, request, *args, **kwargs) -> dict:
        ctx = super().get_context(request, *args, **kwargs)
        self.footnotes = []
        stream_dict = self.body.get_prep_value()
        self._find_footnotes(stream_dict)
        self._rewrite_anchors(stream_dict)
        ctx["menu_pages"] = self._get_menu_pages()
        return ctx

    def _rewrite_anchors(self, stream) -> None:
        search_in = ["rich_text", "highlighted_content"]
        for block in stream:
            if block["type"] in search_in:
                self._rewrite_anchor(block)

    def _rewrite_anchor(self, block) -> None:
        soup = BeautifulSoup(block["value"], "html.parser")
        links = soup.findAll("a")
        for link in links:
            href = link.get("href", None)
            if href and href.startswith("#"):
                foot_num = self._footnote_index(link["href"]) + 1
                link.string = f"[{foot_num}]"
                link["name"] = f"source-{foot_num}"
                link.wrap(soup.new_tag("sup"))
                block["value"] = str(soup)

    def _footnote_index(self, href: str) -> int:
        """Takes an anchor href - ie: #test-anchor - and finds the index of that in self.footnotes

        Args:
            href (str): The anchor we're looking for

        Returns:
            int: The index
        """
        href = href.replace("#", "")
        for i, dic in enumerate(self.footnotes):
            if dic["anchor"] == href:
                return i
        return -1

    def _find_footnotes(self, stream: dict):
        """Find every footnote block, and collect their contents for use in page furniture."""
        footnotes = []
        for block in stream:
            if block.get("type", None) == "footnote":
                try:
                    footnotes.append(
                        {
                            "anchor": block["value"]["anchor"],
                            "body": block["value"]["body"],
                        },
                    )
                except Exception as e:
                    console.warn(e)

        self.footnotes = footnotes

    @property
    def display_title(self):
        "Use the actual Publication title for display title"
        return self.get_parent().specific.cached_title

    @property
    def authors(self):
        "Only the front page of the publication has the authors"
        return self.get_parent().specific.authors

    @property
    def date(self):
        "For consistency, use the front page's date"
        return self.get_parent().specific.date

    @cached_property
    def human_display_date(self):
        "For consistency, use the front page's date"
        return self.get_parent().specific.human_display_date

    @cached_property
    def breadcrumb_page(cls):
        """For pages that have a 'Back to ...' breadcrumb link, returns the page to
        go 'back' to. For most it's the parent, but some require going a bit higher;
        they can override this method.
        """
        return cls.section_page

    @cached_property
    def show_display_date_on_card(self):
        "Whether to show the date when displaying a card about this page."
        return self.get_parent().specific.show_display_date

    @cached_property
    def show_display_date_on_page(self):
        "Whether to show the date when displaying the page."
        return self.get_parent().specific.show_display_date

    def get_next_page(self):
        """Returns the next page, according to the order set in Admin.
        Or None if there is no next page.
        """
        return self.get_next_siblings().live().first()

    def get_previous_page(self):
        """Returns the previous page, according to the order set in Admin.
        If there is no previous sibling, it returns the parent, Front page.
        """
        prev = self.get_prev_siblings().live().first()
        if prev is None:
            return self.get_parent()
        return prev

    def _get_menu_pages(self):
        # We want to use the page title for the `title` in the menu, so:
        first_page = self.get_parent()
        first_page.cached_title = first_page.title
        first_page.title = first_page.specific.page_title

        menu_pages = [first_page]
        siblings = first_page.get_children().live().public().filter(locale=Locale.get_active())
        for sibling in siblings:
            menu_pages.append(sibling)
        return menu_pages


####################################################################################################
# TeamProfilePage
####################################################################################################


class TeamProfilePage(BasePage):
    """
    Although this has areas_of_focus and countries, we don't inherit from
    TaggedPageMixin because it doesn't use publication_type or sectors.
    And it labels areas_of_focus and countries differently.
    """

    def __init__(self, *args, **kwargs):
        self.page_num = 1
        super().__init__(*args, **kwargs)

    template = "content/team_profile_page.jinja"
    parent_page_types: list = ["content.TeamPage"]
    subpage_types: list = []

    authorship = models.OneToOneField(
        "content.Author",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="team_profile",
        help_text=_("Link team member to their authorship of articles on the site"),
    )

    role = models.CharField(max_length=255, blank=True)

    portrait_image = models.ForeignKey(
        settings.IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    countries = ClusterTaggableManager(
        through="notion.CountryTaggedPage",
        blank=True,
    )

    areas_of_focus = ClusterTaggableManager(
        through="taxonomy.FocusAreaTaggedPage",
        blank=True,
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("e.g. ‘London, England’"),
    )

    email_address = models.EmailField(blank=True)

    twitter_url = models.URLField(blank=True, verbose_name="Twitter URL")
    github_url = models.URLField(blank=True, verbose_name="GitHub URL")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")

    intro = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_INLINE_FEATURES,
    )

    body = fields.StreamField(TEAM_PROFILE_PAGE_BODY_BLOCKS, blank=True, use_json_field=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("role"),
        FieldPanel("portrait_image"),
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    about_panels = [
        FieldPanel("authorship"),
        FieldPanel("countries", heading=_("Regional experience")),
        FieldPanel("areas_of_focus", heading=_("Specialist area")),
        FieldPanel("location"),
        MultiFieldPanel(
            [
                FieldPanel("email_address"),
                FieldPanel("twitter_url"),
                FieldPanel("github_url"),
                FieldPanel("linkedin_url"),
            ],
            heading=_("Contact"),
        ),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("role"),
        index.SearchField("intro"),
        index.SearchField("body"),
        index.SearchField("location"),
        index.SearchField("email_address"),
    ]

    def get_context(self, request, *args, **kwargs):
        ctx = super().get_context(request, *args, **kwargs)
        try:
            self.page_num = int(request.GET["page"])
        except MultiValueDictKeyError:
            self.page_num = 1
        except Exception as e:
            console.error(e)

        try:
            authored_pages = self._authorship._authored_pages
            paginator = self._get_paginator(authored_pages)
            ctx["results"] = paginator
            ctx["page_obj"] = paginator
        except Exception as e:
            console.warn(e)
        return ctx

    @cached_property
    def card_blurb(self):
        "Display role instead of blurb on cards"
        return self.role

    @classmethod
    def get_admin_tabs(cls):
        """Add the about tab to the tabbed interface"""
        tabs = super().get_admin_tabs()
        tabs.insert(1, (cls.about_panels, _("About")))
        return tabs

    def _get_paginator(self, results):
        p = Paginator(results, 5)
        result_set = p.page(self.page_num)
        return result_set

    @cached_property
    def _authorship(self):
        """For some reason, translated versions have no authorship model, so we're returning
        the authorship from first locale version of this page that does have one. For an `en`
        page, that _should_ be self, so we check that first.
        """
        if self.authorship is not None:
            return self.authorship
        all_locales = Page.objects.filter(translation_key=self.translation_key).specific().all()
        for item in all_locales:
            if item.authorship is not None:
                return item.authorship


####################################################################################################
# Index type pages
# No heros, just a bit of content, then cards linking to child pages.
####################################################################################################


class JobsIndexPage(IndexPageType):
    """The one page that lists all of the jobs."""

    objects_model = JobPage

    template = "content/jobs_index_page.jinja"
    parent_page_types: list = ["content.SectionListingPage"]
    subpage_types: list = ["content.JobPage"]
    max_count = 1


class NewsIndexPage(IndexPageType):
    """The one page listing all NewsArticlePages"""

    objects_model = NewsArticlePage

    template = "content/blog_news_index_page.jinja"
    parent_page_types: list = ["content.HomePage"]
    subpage_types: list = ["content.NewsArticlePage"]
    max_count = 1


class PublicationsIndexPage(IndexPageType):
    """The one page listing all NewsArticlePages"""

    objects_model = PublicationFrontPage

    template = "content/blog_news_index_page.jinja"
    parent_page_types: list = ["content.HomePage"]
    subpage_types: list = ["content.PublicationFrontPage"]
    max_count = 1


class BlogIndexPage(IndexPageType):
    """The one page listing all BlogArticlePages (blog posts)"""

    objects_model = BlogArticlePage

    template = "content/blog_news_index_page.jinja"
    parent_page_types: list = ["content.HomePage"]
    subpage_types: list = ["content.BlogArticlePage"]
    max_count = 1


class ThemePage(IndexPageType):
    template = "content/theme_page.jinja"
    parent_page_types: list = ["content.SectionPage"]
    subpage_types: list = []


class TeamPage(IndexPageType):
    """The one page listing all TeamProfilePages"""

    # We don't want pagination but, at a certain point, we're going
    # to want pagination:
    objects_per_page = 50

    objects_model = TeamProfilePage

    template = "content/team_page.jinja"
    parent_page_types: list = ["content.SectionListingPage"]
    subpage_types: list = ["content.TeamProfilePage"]
    max_count = 1

    def get_queryset(self, request):
        """
        This returns the queryset needed to paginate the objects on the page. It pulls all the
        valid filters from get_filter_options and carries out the respective logic on the queryset.
        """
        query = self.base_queryset().distinct()
        pages = query.order_by("path")
        return pages

    def get_order_by(self):
        "Order by the order that's been set in Wagtail Admin"
        return ["path"]


####################################################################################################
# Other pages
####################################################################################################


class GlossaryPage(BasePage):
    """The one page that lists all of the Glossary items."""

    template = "content/glossary_page.jinja"

    parent_page_types: list = ["content.SectionPage"]
    subpage_types: list = []
    max_count = 1

    body = fields.StreamField(ARTICLE_PAGE_BODY_BLOCKS, blank=True, use_json_field=True)

    glossary = fields.StreamField(
        [
            ("glossary_item", GlossaryItemBlock()),
        ],
        use_json_field=True,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
        FieldPanel("glossary"),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("body"),
        index.SearchField("glossary"),
    ]


####################################################################################################
# Search
####################################################################################################


class SearchPageSuggestedSearch(Orderable):
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="suggested_for_search",
    )

    link_url = models.CharField(
        help_text=_("Link to an external URL"),
        null=True,
        blank=True,
        max_length=255,
    )

    text = models.CharField(
        null=True,
        blank=False,
        max_length=255,
    )

    search_page = ParentalKey(
        "content.SearchPage",
        related_name="suggested_search_items",
        null=True,
        on_delete=models.CASCADE,
    )

    panels = [
        FieldPanel("text"),
        PageChooserPanel("link_page"),
        FieldPanel("link_url"),
    ]


class SearchPage(BasePage):
    cache_control = "no-cache"
    template = "search.jinja"
    parent_page_types = ["content.HomePage"]
    objects_per_page = 10

    suggested_searches_title = models.CharField(
        null=True,
        blank=False,
        max_length=255,
        default=_("People commonly search for"),
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("suggested_searches_title"),
        InlinePanel("suggested_search_items", heading="Suggested pages"),
    ]

    @cached_property
    def suggested_searches(self):
        objs = []
        for obj in self.suggested_search_items.select_related("link_page"):
            if obj.link_page:
                objs.append(
                    {
                        "text": obj.text,
                        "url": url_from_path(obj.link_page.url_path),
                    },
                )

            if obj.link_url:
                objs.append(
                    {
                        "text": obj.text,
                        "url": obj.link_url,
                    },
                )

        return objs

    def get_results(self, search_query=None, page=1):
        objs = []
        if search_query:
            query = Query.get(search_query)
            promoted_ids = []
            try:
                query = Query.get(search_query)
                promoted_ids = query.editors_picks.values_list("page_id", flat=True)
            except Exception as err:
                console.warn(err)

            if promoted_ids:
                promoted_pages = Page.objects.filter(id__in=promoted_ids).live().specific()
            else:
                promoted_pages = Page.objects.none()

            pages = (
                Page.objects.specific()
                .live()
                .select_related("thumbnail_image")
                .exclude(id__in=promoted_ids)
                .search(search_query)
            )

            objs = list(chain(promoted_pages, pages))
            query.add_hit()

        paginator = Paginator(objs, self.objects_per_page)

        try:
            search_results = paginator.page(page)
        except PageNotAnInteger:
            search_results = paginator.page(1)
        except EmptyPage:
            search_results = paginator.page(paginator.num_pages)

        return search_results

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        search_query = request.GET.get("q", None)
        page = request.GET.get("page", 1)

        results = self.get_results(search_query, page)

        context.update(
            {
                "search_query": search_query,
                "show_search": True,
                "results": results,
            },
        )

        if not results:
            context.update(
                {
                    "suggested_searches": self.suggested_searches,
                },
            )

        return context

    @classmethod
    def can_create_at(cls, parent) -> bool:
        return super().can_create_at(parent) and not cls.objects.exists()


####################################################################################################
# TAXONOMIES
####################################################################################################


class TaxonomyPage(BasePage):
    """
    For listing all of the tags/categories within a taxonomy.
    """

    template = "content/taxonomy_detail.jinja"
    parent_page_types = ["content.HomePage"]
    subpage_types: list = ["content.TagPage"]

    intro = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_INLINE_FEATURES,
    )

    body = fields.StreamField(ARTICLE_PAGE_BODY_BLOCKS, blank=True, use_json_field=True)

    tags_title = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Will appear above the cards linking to each Tag Page"),
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro", heading=_("Intro")),
        FieldPanel("body", heading=_("Body")),
        FieldPanel("tags_title", heading=_("Tags title")),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField("intro"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # For listing all the child TagPages:
        context["pages"] = self.get_children().live().public().filter(locale=Locale.get_active())

        return context


class TagPageForm(WagtailAdminPageForm):
    "Adding custom validation"

    def clean(self):
        "Ensure 1, and only 1, tag is selected."
        cleaned_data = super().clean()

        tags = [
            # cleaned_data['focus_area'],
            cleaned_data["sector"],
            cleaned_data["publication_type"],
            cleaned_data["section"],
            cleaned_data["principle"],
        ]
        num_selected = len([t for t in tags if t])
        if num_selected == 0:
            self.add_error(
                "sector",
                f"Please choose a tag from one of the {len(tags)} taxonomies.",
            )
        elif num_selected > 1:
            self.add_error(
                "sector",
                f"Please only choose a single tag from the {len(tags)} taxonomies.",
            )

        return cleaned_data


class TagPage(IndexPageType):
    """
    For choosing a single tag/category, and listing all the Pages tagged with it
    in this Section.
    """

    base_form_class = TagPageForm
    template = "content/taxonomy_tag.jinja"
    parent_page_types = ["content.TaxonomyPage"]
    subpage_types: list = []

    # Allow for headings, per design:
    intro = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_BODY_FEATURES,
    )

    video = models.URLField(blank=True, null=True)

    body = fields.StreamField(TAG_PAGE_BODY_BLOCKS, blank=True, use_json_field=True)

    focus_area = models.ForeignKey(
        "taxonomy.FocusAreaTag",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="tagpages",
    )

    sector = models.ForeignKey(
        "taxonomy.SectorTag",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="tagpages",
    )

    publication_type = models.ForeignKey(
        "taxonomy.PublicationType",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="tagpages",
    )

    section = models.ForeignKey(
        "taxonomy.SectionTag",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="tagpages",
    )

    principle = models.ForeignKey(
        "taxonomy.PrincipleTag",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="tagpages",
    )

    content_panels = BasePage.content_panels + [
        MultiFieldPanel(
            [
                # FieldPanel('focus_area'),
                FieldPanel("sector", heading=_("Topic")),
                FieldPanel("publication_type"),
                FieldPanel("section"),
                FieldPanel("principle"),
            ],
            heading=_("Tag"),
        ),
        FieldPanel("body"),
        FieldPanel("video"),
        FieldPanel("intro"),
    ]

    def get_order_by(self):
        return ["-first_published_at"]

    def base_queryset(self):
        """
        Get pages that are in the chosen category, or tagged with the
        chosen tag. Passes the query to IndexPageType
        """
        tag = None
        category = None

        # Work out which tag/category this page is for:
        if self.focus_area:
            tag = self.focus_area
        elif self.sector:
            tag = self.sector
        elif self.section:
            tag = self.section
        elif self.principle:
            tag = self.principle
        elif self.publication_type:
            category = self.publication_type

        if category:
            return category.pages

        if tag:
            related_pages = getattr(tag, tag.__class__.related_pages_name)
            page_ids = related_pages.values_list("content_object__id", flat=True)

            query = (
                Page.objects.live()
                .public()
                .specific()
                .filter(locale=Locale.get_active())
                .filter(id__in=page_ids)
                .select_related("thumbnail")
            )
            return query
        # Shouldn't get here.
        return Page.objects.none()

    def get_context(self, request, *args, **kwargs) -> dict:
        """Extending this to add in the video embed"""
        ctx = super().get_context(request, *args, **kwargs)
        from wagtail.embeds import embeds

        if self.video:
            try:
                embed = embeds.get_embed(self.video, max_width=100, max_height=100)
                html = str(embed.html)

                console.info(html)
                html.replace('width="200"', "")
                html.replace('height="150"', "")
                console.info(html)
                ctx["video_embed"] = html
            except Exception as e:
                console.warn(e)
                ctx["video_embed"] = self.video

        return ctx

    @classmethod
    def can_create_at(cls, parent) -> bool:
        "Override IndexPageType, which only lets us create 1"
        can_create = cls.is_creatable and cls.can_exist_under(parent)

        return can_create


class LatestSectionContentPage(IndexPageType):
    """
    For displaying the latest content within a section
    """

    template = "content/latest_content.jinja"
    parent_page_types = ["content.SectionPage", "content.SectionListingPage"]
    subpage_types: list = []

    def get_order_by(self):
        return ["-last_published_at"]

    def base_queryset(self):
        from modules.content.models import content_page_models

        return (
            self.section_page.get_descendants()
            .live()
            .public()
            .exact_type(*content_page_models)
            .filter(locale=Locale.get_active())
            .specific()
            .select_related("thumbnail")
        )


class PressLinksPage(IndexPageType):
    """
    For displaying PressLink snippets within a section.
    """

    template = "content/press_links.jinja"
    parent_page_types = ["content.HomePage"]
    subpage_types: list = []

    def get_order_by(self):
        return ["-first_published_at"]

    def base_queryset(self):
        from modules.content.models import PressLink

        # return PressLink.objects.filter(section_page=self.section_page)
        return PressLink.objects


class MapPage(BasePage):
    """The page that displays the international impact map.

    For the OO global map, the designs call for a count in the map key of the number of countries
    committed to a central register/public register as well as those who have implemented a central
    register/public register.
    So the number of countries satisfying the conditions laid out in the comment above also needs
    to be tallied up.

    """

    template = "content/map_page.jinja"

    parent_page_types: list = ["content.HomePage"]
    subpage_types: list = []

    intro = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_INLINE_FEATURES,
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        context["countries_json"] = countries_json()
        context["map_json"] = map_json()
        context["country_counts"] = self._country_counts
        context["regions"] = Region.objects.all()
        context["oo_engaged_values"] = list(CountryTag.OO_ENGAGED_VALUES)

        return context

    @cached_property
    def _country_counts(self):
        """Get counts for number of countries in each category.

        These use cached_properties on the country models so we can't do
        a nice SQL / ORM query to tally them, so we're doing this instead.
        """
        counts = {}

        countries = CountryTag.objects.all()
        for country in countries:
            if country.category is not None:
                if country.category in counts:
                    counts[country.category] += 1
                else:
                    counts[country.category] = 1

        # Number of countries in which OO is engaged:
        counts["engaged"] = CountryTag.objects.filter(
            oo_support__in=CountryTag.OO_ENGAGED_VALUES,
        ).count()

        return counts
