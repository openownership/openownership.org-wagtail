# -*- coding: utf-8 -*-

"""
    content.models.pages
    ~~~~~~~~~~~~~~~~~
    Site-wide page modules.
"""

from itertools import chain

# 3rd party
from django.conf import settings
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from wagtail.admin.edit_handlers import (
    FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel
)
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.core import fields
from wagtail.core.models import Orderable, Page
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.search.models import Query
from wagtail.snippets.edit_handlers import SnippetChooserPanel

# Project

from config.template import url_from_path
from modules.content.blocks import (
    article_page_body_blocks,
    home_page_blocks,
    section_page_blocks,
    team_profile_page_body_blocks,
)
from modules.content.blocks.stream import GlossaryItemBlock
from .mixins import PageAuthorsMixin, PageHeroMixin
from .page_types import BasePage, LandingPageType, ContentPageType, IndexPageType


####################################################################################################
# Landing type pages
####################################################################################################


class HomePage(PageHeroMixin, LandingPageType):

    class Meta:
        verbose_name = 'Home page'

    template: str = 'content/home.jinja'

    # Only allow at root level:
    parent_page_types: list = ['wagtailcore.Page']
    subpage_types: list = [
        "content.JobsIndexPage",
        "content.SectionPage",
        "content.SectionListingPage",
        "content.UtilityPage",
    ]
    max_count = 1

    search_fields: list = []

    body = fields.StreamField(home_page_blocks, blank=True)

    content_panels = BasePage.content_panels + [
        StreamFieldPanel('body')
    ]

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        context['body_classes'] = 'home-page'
        context['is_home'] = True
        return context

    def get_meta_title(self) -> str:
        meta_title = super().get_meta_title()
        if meta_title == 'Home':
            return settings.WAGTAIL_SITE_NAME
        return ""

    @classmethod
    def can_create_at(cls, parent) -> bool:
        return super().can_create_at(parent) and not cls.objects.exists()


class SectionPage(PageHeroMixin, LandingPageType):
    """For the top-level section pages, like Impact, Insight, Implement.
    """
    class Meta:
        verbose_name = 'Section page'

    template: str = 'content/section_page.jinja'

    parent_page_types: list = ['content.HomePage']
    subpage_types: list = [
        'content.ArticlePage',
        'content.BlogIndexPage',
        'content.GlossaryPage',
        'content.NewsIndexPage',
        'content.PublicationFrontPage',
    ]

    search_fields: list = []

    body = fields.StreamField(section_page_blocks, blank=True)

    content_panels = BasePage.content_panels + [
        StreamFieldPanel('body')
    ]


class SectionListingPage(SectionPage):
    """A top-level section page, but the body only lists its child
    pages - it has no other configurable body content.

    Used for the About section page.
    """

    template: str = 'content/section_listing_page.jinja'
    parent_page_types: list = ["content.HomePage"]
    subpage_types: list = [
        "content.ArticlePage",
        "content.PublicationFrontPage",
        "content.TeamPage",
    ]

    show_child_pages = models.BooleanField(
        default=True, help_text="Display cards linking to all the child pages"
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('show_child_pages'),
    ]

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        if self.show_child_pages:
            context['child_pages'] = self.get_children().live().public()
        else:
            context['child_pages'] = self.get_children().none()
        return context


####################################################################################################
# Content type pages
# All sharing the same kinds of tags etc.
####################################################################################################


class ArticlePage(ContentPageType):
    """Basic page of content, used for things like About pages.
    """
    template = 'content/article_page.jinja'

    parent_page_types: list = ['content.SectionListingPage']

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        context['menu_pages'] = self.get_parent().get_children().live().public()
        return context


class NewsArticlePage(PageAuthorsMixin, ContentPageType):
    """An article in the Insight > News section.
    """
    template = 'content/news_article_page.jinja'
    parent_page_types: list = ['content.NewsIndexPage']
    subpage_types: list = []

    # Also has:
    # author_relationships from NewsArticleAuthorRelationship
    # authors from PageAuthorsMixin


class BlogArticlePage(PageAuthorsMixin, ContentPageType):
    """An article in the Insight > Blog section.
    """
    template = 'content/blog_article_page.jinja'
    parent_page_types: list = ['content.BlogIndexPage']
    subpage_types: list = []

    # Also has:
    # author_relationships from BlogArticleAuthorRelationship
    # authors from PageAuthorsMixin

    class Meta:
        verbose_name = 'Blog post page'


class UtilityPage(ContentPageType):
    """Used, I think, for pages like Privacy, Terms, etc.
    """
    template = 'content/utility_page.jinja'

    parent_page_types: list = ['content.HomePage']
    subpage_types: list = []

    intro = fields.RichTextField(
        blank=True, null=True, features=settings.RICHTEXT_INLINE_FEATURES
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('intro')
    ] + ContentPageType.model_content_panels


class JobPage(ContentPageType):
    template = 'content/job_page.jinja'
    parent_page_types: list = ['content.JobsIndexPage']
    subpage_types: list = []

    application_url = models.URLField(
        blank=True,
        max_length=255,
        help_text="URL of the page where people can apply for the job",
        verbose_name="Application URL"
    )
    application_deadline = models.DateField(blank=True, null=True)

    content_panels = ContentPageType.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel('application_deadline'),
                FieldPanel('application_url')
            ],
            heading='Application details'
        )
    ]

    @cached_property
    def human_application_deadline(self):
        if self.application_deadline:
            return self.application_deadline.strftime('%d %B %Y')


####################################################################################################
# PublicationPages
####################################################################################################


class PublicationFrontPageForm(WagtailAdminPageForm):
    "So that we can re-name the default title field."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        title = self.fields['title']
        title.label = _('Publication title')
        title.help_text = _("The publication title as you'd like it to be seen by the public")


class PublicationFrontPage(PageAuthorsMixin, BasePage):
    """The front and main page of a Publication.

    This defines all the information about the Publication as a whole.
    Its child pages (PublicationInnerPage) contain any subsequent pages
    of content within it.
    """

    base_form_class = PublicationFrontPageForm

    template = 'content/publication_front_page.jinja'
    parent_page_types: list = ['content.SectionPage', 'content.SectionListingPage']
    subpage_types: list = ['content.PublicationInnerPage']

    page_title = models.CharField(
        max_length=255, blank=True, help_text="e.g. ‘Introduction’"
    )

    cover_image = models.ForeignKey(
        settings.IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    download_document = models.ForeignKey(
        settings.WAGTAILDOCS_DOCUMENT_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    summary = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_INLINE_FEATURES
    )

    outcomes = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_BODY_FEATURES,
        verbose_name="Key Learning Outcomes"
    )

    impact = fields.RichTextField(
        blank=True,
        null=True,
        features=settings.RICHTEXT_INLINE_FEATURES,
        verbose_name="Benefit / Impact"
    )

    # Also has:
    # author_relationships from PublicationAuthorRelationship
    # authors from PageAuthorsMixin

    content_panels = [
        MultiFieldPanel(
            [
                FieldPanel('title'),
                FieldPanel('page_title'),
            ],
            heading="Titles"
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('cover_image'),
                DocumentChooserPanel('download_document'),
            ],
            heading="Cover and document"
        ),
        MultiFieldPanel(
            [
                FieldPanel('summary'),
                FieldPanel('outcomes'),
                FieldPanel('impact'),
            ],
            heading='Content'
        )
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField('summary'),
        index.SearchField('outcomes'),
        index.SearchField('impact'),
    ]

    @property
    def date(self):
        return self.display_date

    @cached_property
    def human_display_date(self):
        if self.display_date:
            return self.display_date.strftime('%d %B %Y')

    @property
    def display_title(self):
        "Title of the publication"
        return self.title

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        # This seems odd, but it works.

        # We want to use the page title for the `title` in the menu, so:
        first_page = self
        first_page.title = first_page.specific.page_title
        context['menu_pages'] = [first_page] + list(self.get_children().live().public())

        return context


class PublicationInnerPageForm(WagtailAdminPageForm):
    "So that we can re-name the default title field."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        title = self.fields['title']
        title.label = _('Page title')
        title.help_text = _("Short title of this page within the publication e.g. 'Overview', 'Comprehensive coverage', etc.")


class PublicationInnerPage(ContentPageType):
    """A page within a Publication.

    A Publication has a PublicationFrontPage as its first page, which
    defines all the general info about the publication.
    """

    base_form_class = PublicationInnerPageForm

    template = 'content/publication_inner_page.jinja'
    parent_page_types: list = ['content.PublicationFrontPage']
    subpage_types: list = []

    content_panels = [
        FieldPanel('title'),
        StreamFieldPanel('body'),
    ]

    def __str__(self):
        return f"{self.get_parent().title}: {self.title}"

    @property
    def display_title(self):
        "Use the actual Publication title for display title"
        return self.get_parent().specific.title

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

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        # This seems odd, but it works.

        # We want to use the page title for the `title` in the menu, so:
        first_page = self.get_parent()
        first_page.title = first_page.specific.page_title
        context['menu_pages'] = [first_page] + list(first_page.get_children().live().public())

        return context


####################################################################################################
# TeamProfilePage
####################################################################################################


class TeamProfilePage(BasePage):

    template = 'content/team_profile_page.jinja'
    parent_page_types: list = ['content.TeamPage']
    subpage_types: list = []

    authorship = models.OneToOneField(
        'content.Author',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='team_profile',
        help_text='Link team member to their authorship of articles on the site'
    )

    role = models.CharField(max_length=255, blank=True)

    portrait_image = models.ForeignKey(
            settings.IMAGE_MODEL,
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name='+'
    )

    location = models.CharField(
        max_length=255, blank=True, help_text="e.g. ‘London, England’"
    )

    email_address = models.EmailField(blank=True)

    intro = fields.RichTextField(
        blank=True, null=True, features=settings.RICHTEXT_INLINE_FEATURES
    )

    body = fields.StreamField(team_profile_page_body_blocks, blank=True)

    content_panels = BasePage.content_panels + [
        FieldPanel('role'),
        ImageChooserPanel('portrait_image'),
        MultiFieldPanel(
            [
                FieldPanel('location'),
                FieldPanel('email_address'),
            ],
            heading="Details"
        ),
        SnippetChooserPanel('authorship'),
        FieldPanel('intro'),
        StreamFieldPanel('body'),
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField('role'),
        index.SearchField('intro'),
        index.SearchField('body'),
        index.SearchField('location'),
        index.SearchField('email_address'),
    ]


####################################################################################################
# Index type pages
# No heros, just a bit of content, then cards linking to child pages.
####################################################################################################


class JobsIndexPage(IndexPageType):
    """The one page that lists all of the jobs.
    """
    objects_model = JobPage

    template = 'content/jobs_index_page.jinja'
    parent_page_types: list = ['content.HomePage']
    subpage_types: list = ['content.JobPage']
    max_count = 1

    def get_context(self, request, *args, **kwargs) -> dict:
        context = super().get_context(request, *args, **kwargs)
        context['menu_pages'] = [self] + list(JobPage.objects.live().public())
        return context


class NewsIndexPage(IndexPageType):
    """The one page listing all NewsArticlePages"""

    objects_model = NewsArticlePage

    template = 'content/news_index_page.jinja'
    parent_page_types: list = ['content.SectionPage']
    subpage_types: list = ['content.NewsArticlePage']
    max_count = 1


class BlogIndexPage(IndexPageType):
    """The one page listing all BlogArticlePages (blog posts)"""

    objects_model = BlogArticlePage

    template = 'content/blog_index_page.jinja'
    parent_page_types: list = ['content.SectionPage']
    subpage_types: list = ['content.BlogArticlePage']
    max_count = 1


class ThemePage(IndexPageType):

    template = 'content/theme_page.jinja'
    parent_page_types: list = ['content.SectionPage']
    subpage_types: list = []


class TeamPage(IndexPageType):
    """The one page listing all TeamProfilePages"""

    objects_model = TeamProfilePage

    template = 'content/team_page.jinja'
    parent_page_types: list = ['content.SectionListingPage']
    subpage_types: list = ['content.TeamProfilePage']
    max_count = 1


####################################################################################################
# Other pages
####################################################################################################


class GlossaryPage(BasePage):
    """The one page that lists all of the Glossary items.
    """
    template = 'content/glossary_page.jinja'

    parent_page_types: list = ['content.SectionPage']
    subpage_types: list = []
    max_count = 1

    body = fields.StreamField(article_page_body_blocks, blank=True)

    glossary = fields.StreamField([
        ('glossary_item', GlossaryItemBlock()),
    ])

    content_panels = BasePage.content_panels + [
        StreamFieldPanel('body'),
        StreamFieldPanel('glossary')
    ]

    search_fields = BasePage.search_fields + [
        index.SearchField('body'),
        index.SearchField('glossary'),
    ]


####################################################################################################
# Search
####################################################################################################

class SearchPageSuggestedSearch(Orderable):

    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='suggested_for_search'
    )

    link_url = models.CharField(
        help_text='Link to an external URL',
        null=True,
        blank=True,
        max_length=255
    )

    text = models.CharField(
        null=True,
        blank=False,
        max_length=255
    )

    search_page = ParentalKey(
        'content.SearchPage',
        related_name='suggested_search_items',
        null=True,
        on_delete=models.CASCADE
    )

    panels = [
        FieldPanel('text'),
        PageChooserPanel('link_page'),
        FieldPanel('link_url'),
    ]


class SearchPage(BasePage):

    cache_control = 'no-cache'
    template = 'search.jinja'
    parent_page_types = ['content.HomePage', ]
    objects_per_page = 10

    suggested_searches_title = models.CharField(
        null=True,
        blank=False,
        max_length=255,
        default="People commonly search for"
    )

    content_panels = BasePage.content_panels + [
        FieldPanel('suggested_searches_title'),
        InlinePanel('suggested_search_items', heading="Suggested pages")
    ]

    @cached_property
    def suggested_searches(self):
        objs = []
        for obj in self.suggested_search_items.select_related('link_page'):
            if obj.link_page:
                objs.append({
                    'text': obj.text,
                    'url': url_from_path(obj.link_page.url_path)
                })

            if obj.link_url:
                objs.append({
                    'text': obj.text,
                    'url': obj.link_url
                })

        return objs

    def get_results(self, search_query=None, page=1):

        objs = []
        if search_query:
            query = Query.get(search_query)
            promoted_ids = query.editors_picks.values_list('page_id', flat=True)
            if promoted_ids:
                promoted_pages = Page.objects.filter(id__in=promoted_ids).live().specific()
            else:
                promoted_pages = Page.objects.none()

            pages = Page.objects\
                        .specific()\
                        .live()\
                        .select_related('thumbnail_image')\
                        .exclude(id__in=promoted_ids)\
                        .search(search_query)

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
        search_query = request.GET.get('q', None)
        page = request.GET.get('page', 1)

        results = self.get_results(search_query, page)

        context.update({
            'search_query': search_query,
            'show_search': True,
            'results': results
        })

        if not results:
            context.update({
                'suggested_searches': self.suggested_searches
            })

        return context

    @classmethod
    def can_create_at(cls, parent) -> bool:
        return super().can_create_at(parent) and not cls.objects.exists()
