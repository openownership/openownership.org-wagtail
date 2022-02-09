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

from modelcluster.fields import ParentalKey, ParentalManyToManyField

from wagtail.admin.edit_handlers import (
    FieldPanel, InlinePanel, MultiFieldPanel, PageChooserPanel, StreamFieldPanel
)
from wagtail.core import fields
from wagtail.core.models import Orderable, Page
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

    class Meta:
        verbose_name = 'Section listing page'

    template: str = 'content/section_listing_page.jinja'

    parent_page_types: list = ["content.HomePage"]
    subpage_types: list = ["content.ArticlePage", "content.TeamPage"]

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
        blank=True,
        null=True,
        features=["bold", "italic", "small", "ol", "ul", "link", "document-link"],
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
        blank=True,
        null=True,
        features=["bold", "italic", "small", "ol", "ul", "link", "document-link"],
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
