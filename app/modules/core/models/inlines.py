from django.conf import settings
from django.db import models
from wagtail.core.models import Orderable
from wagtail.admin.edit_handlers import PageChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel


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
