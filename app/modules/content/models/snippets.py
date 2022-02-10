from django.db import models

from wagtail.admin.edit_handlers import FieldPanel
from wagtail.snippets.models import register_snippet


@register_snippet
class Author(models.Model):
    """
    An Author is someone who wrote something on this site.
    """
    name = models.CharField(max_length=255, blank=False)

    panels = [
        FieldPanel('name'),
    ]

    # Also:
    # blog_articles from BlogArticleAuthorRelationship
    # news_articles from NewsArticleAuthorRelationship
    # team_profile from TeamProfilePage

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
