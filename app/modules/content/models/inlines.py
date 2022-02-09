from django.conf import settings
from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.core.models import Orderable
from wagtail.admin.edit_handlers import InlinePanel, PageChooserPanel, FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel


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
        verbose_name = 'Page collection'
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
        verbose_name = 'Image collection'
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
        ImageChooserPanel('image')
    ]


# class FeaturedNewsArticle(Orderable):

#     news_index_page = ParentalKey(
#         'content.NewsIndexPage',
#         related_name='featured_articles',
#         null=True,
#         on_delete=models.CASCADE
#     )

#     link_page = models.ForeignKey(
#         'wagtailcore.Page',
#         null=True,
#         blank=False,
#         related_name='+',
#         on_delete=models.SET_NULL
#     )

#     panels = [
#         PageChooserPanel('link_page', page_type='content.NewsArticlePage')
#     ]
