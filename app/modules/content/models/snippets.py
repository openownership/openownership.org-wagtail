from django.db import models
from django_extensions.db.fields import AutoSlugField

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.core import fields
from wagtail.core.models import Orderable
from wagtail.admin.edit_handlers import InlinePanel
from wagtail.admin.edit_handlers import (
    FieldPanel
)


class FAQList(ClusterableModel):

    class Meta:
        verbose_name = 'FAQ List'

    name = models.CharField(
        max_length=255,
        null=True,
        blank=False,
        verbose_name="List name"
    )

    slug = AutoSlugField('Slug', populate_from='name', unique=True, db_index=True)

    panels = [
        FieldPanel('name'),
        InlinePanel('faqs', heading="Items")
    ]

    def __str__(self):
        return self.name


class FAQItem(ClusterableModel, Orderable):

    faq_list = ParentalKey(
        FAQList,
        related_name='faqs',
        null=True,
        on_delete=models.CASCADE,
        verbose_name="FAQ List"
    )

    question = models.CharField(
        max_length=255,
        null=True,
        blank=False,
        verbose_name="Question"
    )

    answer = fields.RichTextField(
        blank=False,
        null=True,
        features=['bold', 'italic', 'underline', 'link', 'document-link'],
    )
