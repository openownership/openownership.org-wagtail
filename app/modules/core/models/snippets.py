from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django.utils.functional import cached_property

from modelcluster.models import ClusterableModel

from wagtail.core import fields
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.snippets.models import register_snippet
from wagtail.admin.edit_handlers import (
    FieldPanel, PageChooserPanel
)


@register_snippet
class PromoPanel(ClusterableModel):

    reference = models.CharField(
        max_length=255,
        help_text='Used internally to identify the purpose of this promo',
        null=True,
        blank=False
    )

    title = models.CharField(
        max_length=255,
        null=False,
        blank=False
    )

    body = fields.RichTextField(
        blank=True,
        null=True,
        features=['bold', 'italic', 'underline', 'small', 'link', 'document-link']
    )

    link_label = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    link_document = models.ForeignKey(
        settings.DOCUMENT_MODEL,
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL
    )

    link_url = models.URLField(
        max_length=255,
        null=False,
        blank=True
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('body'),
        FieldPanel('link_label'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
        FieldPanel('link_url')
    ]

    @cached_property
    def url(self):
        if self.link_page:
            return self.link_page.url_path.replace('/home', '', 1)
        if self.link_document:
            filename = self.link_document.file
            return reverse('wagtaildocs_serve', args=[self.link_document.id, filename])
        if self.link_url:
            return self.link_url

    def __str__(self):
        return self.reference
