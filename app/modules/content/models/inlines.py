# 3rd party
from django.db import models
from django.conf import settings
from modelcluster.fields import ParentalKey
from wagtail.models import Orderable
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import InlinePanel, PageChooserPanel, FieldPanel


class NestedInlinePanel(InlinePanel):
    def widget_overrides(self):
        widgets = {}
        child_edit_handler = self.get_child_edit_handler()
        for handler_class in child_edit_handler.children:
            widgets.update(handler_class.widget_overrides())
        widget_overrides = {self.relation_name: widgets}
        return widget_overrides


class InlinePageManager(models.Manager):

    def get_pages(self):
        pages = []
        objs = self.all()

        for obj in objs:
            pages.append(obj.link_page.specific)

        return pages


class InlinePage(models.Model):

    class Meta:
        abstract = True
        verbose_name = _('Page collection')
        ordering = ['sort_order']

    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    objects = InlinePageManager()

    panels = [
        PageChooserPanel('link_page')
    ]

    @property
    def link(self):
        return self.link_page.url


class InlineImageManager(models.Manager):

    def get_images(self):
        objects = []
        objs = self.prefetch_related('image').all()

        for obj in objs:
            objects.append(obj.image)

        return objects


class ImageLink(Orderable):

    class Meta:
        abstract = True
        verbose_name = _('Image collection')
        ordering = ['sort_order']

    image = models.ForeignKey(
        settings.IMAGE_MODEL,
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    objects = InlineImageManager()

    panels = [
        FieldPanel('image')
    ]


####################################################################################################
# Authors
####################################################################################################


class BlogArticleAuthorRelationship(Orderable, models.Model):
    """
    Linking BlogArticlePage with one or more Authors.
    """
    page = ParentalKey(
        'content.BlogArticlePage',
        on_delete=models.CASCADE,
        related_name='author_relationships'
    )
    author = models.ForeignKey(
        'content.Author',
        on_delete=models.CASCADE,
        related_name='blog_articles'
    )

    class Meta(Orderable.Meta):
        verbose_name = _('Post author')
        verbose_name_plural = _('Post authors')

    panels = [
        FieldPanel('author'),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.author.name


class NewsArticleAuthorRelationship(Orderable, models.Model):
    """
    Linking NewsArticlePage with one or more Authors.
    """
    page = ParentalKey(
        'content.NewsArticlePage',
        on_delete=models.CASCADE,
        related_name='author_relationships'
    )
    author = models.ForeignKey(
        'content.Author',
        on_delete=models.CASCADE,
        related_name='news_articles'
    )

    class Meta(Orderable.Meta):
        verbose_name = _('Article author')
        verbose_name_plural = _('Article authors')

    panels = [
        FieldPanel('author'),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.author.name


class PublicationAuthorRelationship(Orderable, models.Model):
    """
    Linking PublicationFrontPage with one or more Authors.
    """
    page = ParentalKey(
        'content.PublicationFrontPage',
        on_delete=models.CASCADE,
        related_name='author_relationships'
    )
    author = models.ForeignKey(
        'content.Author',
        on_delete=models.CASCADE,
        related_name='publications'
    )

    class Meta(Orderable.Meta):
        verbose_name = _('Publication author')
        verbose_name_plural = _('Publication authors')

    panels = [
        FieldPanel('author'),
    ]

    def __str__(self):
        return self.page.title + " -> " + self.author.name


class PressLinkAuthorRelationship(Orderable, models.Model):

    snippet = ParentalKey(
        'content.PressLink',
        on_delete=models.CASCADE,
        related_name='author_relationships'
    )
    author = models.ForeignKey(
        'content.Author',
        on_delete=models.CASCADE,
        related_name='press_links'
    )

    class Meta(Orderable.Meta):
        verbose_name = _('Press link author')
        verbose_name_plural = _('Press link authors')

    panels = [
        FieldPanel('author'),
    ]

    def __str__(self):
        return self.presslink.title + " -> " + self.author.name
