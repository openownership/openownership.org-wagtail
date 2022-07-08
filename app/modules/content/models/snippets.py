# 3rd party
from django.db import models
from django.conf import settings
from wagtail.search import index
from modelcluster.models import ClusterableModel
from wagtail.snippets.models import register_snippet
from django.utils.translation import gettext_lazy as _
from modelcluster.contrib.taggit import ClusterTaggableManager
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


@register_snippet
class Author(index.Indexed, models.Model):
    """
    An Author is someone who wrote something on this site.
    """
    name = models.CharField(max_length=255, blank=False)

    panels = [
        FieldPanel('name'),
    ]

    # Also has:
    # blog_articles from BlogArticleAuthorRelationship
    # news_articles from NewsArticleAuthorRelationship
    # publications from PublicationAuthorRelationship
    # press_links from PressLinkAuthorRelationship
    # team_profile from TeamProfilePage

    search_fields = [
        index.SearchField('name', partial_match=True),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

    def get_blog_articles(self, num=5):
        """Return the num most recent BlogArticlePages by this author
        sorted by display_date descending.
        """
        articles = (
            self.blog_articles
                .filter(page__live=True)
                .order_by('-page__first_published_at')[:num]
        )
        return [a.page for a in articles]

    def get_news_articles(self, num=5):
        """Return the num most recent NewsArticlePages by this author
        sorted by display_date descending.
        """
        articles = (
            self.news_articles
                .filter(page__live=True)
                .order_by('-page__first_published_at')[:num]
        )
        return [a.page for a in articles]

    def get_publications(self, num=5):
        """Return the num most recent PublicationFrontPages by this author
        sorted by display_date descending.
        """
        publications = (
            self.publications
                .filter(page__live=True)
                .order_by('-page__first_published_at')[:num]
        )
        return [a.page for a in publications]

    def get_content_pages(self, num=5):
        """Returns a list of num Blog Articles and News Articles by
        this author sorted by display_date descending.
        """
        content = (
            self.get_blog_articles(num) +
            self.get_news_articles(num) +
            self.get_publications(num)
        )
        return sorted(
            content, key=lambda x: x.first_published_at, reverse=True
        )[:num]


@register_snippet
class PressLink(index.Indexed, ClusterableModel):
    """
    For linking to a page on another website.
    Can appear as cards on section pages or on a theme listing page.
    """

    # PressLinks need to be "within" a section so that we only display
    # the correct ones in the section taxonomy/theme listing pages
    # and on front section pages.
    section_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Section'),
    )

    sections = ClusterTaggableManager(
        through='taxonomy.SectionTaggedPressLink', blank=True
    )

    url = models.URLField(verbose_name=_('URL'), blank=False)

    title = models.CharField(max_length=255, blank=False)

    blurb = models.CharField(max_length=255, blank=True)

    thumbnail = models.ForeignKey(
        settings.IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name=_('Logo'),
    )

    first_published_at = models.DateTimeField(auto_now_add=True, db_index=True)

    # Also has:
    # author_relationships from PressLinkAuthorRelationship

    search_fields = [
        index.SearchField('title', partial_match=True),
        index.SearchField('blurb', partial_match=True),
    ]

    panels = [
        # PageChooserPanel('section_page', 'content.SectionPage'),
        FieldPanel('url'),
        ImageChooserPanel('thumbnail'),
        FieldPanel('title'),
        FieldPanel('blurb'),
        FieldPanel('sections', _('Sections')),
        MultiFieldPanel(
            [InlinePanel('author_relationships', label=_('Authors'))], heading=_('Authors')
        )
    ]

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-first_published_at']
        verbose_name = "Press Link"
        verbose_name_plural = "Press Links"

    @property
    def authors(self):
        """Returns a list of Author objects associated with this article.
        """
        authors = self.author_relationships.all().order_by("sort_order")
        return [a.author for a in authors]

    @property
    def is_press_link(self):
        "So it can be differentiated from Pages in templates"
        return True

    # Methods/properties to make it behave a bit like a Page in templates:

    def get_url(self):
        return self.url

    @property
    def specific(self):
        return self

    @property
    def display_date(self):
        return self.first_published_at

    @property
    def human_display_date(self):
        return self.display_date.strftime('%d %B %Y')
