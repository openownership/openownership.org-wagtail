from .core import Category

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from wagtail.snippets.models import register_snippet


class PublicationType(Category):
    """
    e.g. Case Study, Guidance, Job.

    Some Pages should be set to have a specific type ("Job").
    Others can choose, but from a specific selection of types.
    """

    # Name of the URL for viewing things with this Tag.
    url_name = "publicationtype-category"

    # Slug used in URLs for this taxonomy:
    url_slug = 'types'

    class Meta:
        verbose_name = _("Publication type")
        verbose_name_plural = _("Publication types")
