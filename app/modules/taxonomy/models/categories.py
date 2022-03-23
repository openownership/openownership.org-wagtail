from .core import Category

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from wagtailmodelchooser import register_model_chooser
from wagtail.core.models import Locale


@register_model_chooser
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
        verbose_name = _("Content type")
        verbose_name_plural = _("Content types")

    def get_url(self):
        """Generate the URL to this category's TagPage.
        """
        from modules.content.models import TagPage

        qs = TagPage.objects

        page = (
            qs.live().public().filter(locale=Locale.get_active())
            .filter(publication_type=self).first()
        )
        if page:
            return page.get_url()
        else:
            return ''
