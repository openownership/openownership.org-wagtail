from .core import Category

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from wagtail.snippets.models import register_snippet


@register_snippet
class PublicationType(Category):
    """
    e.g. Case Study, Guidance, Job.

    Some Pages should be set to have a specific type ("Job").
    Others can choose, but from a specific selection of types.
    """

    url_name = "publicationtype-category"

    class Meta:
        verbose_name = _("Publication type")
        verbose_name_plural = _("Publication types")

    def get_url(self, section_slug):
        """Generate the URL to this tag's view
        section_slug is the Slug of the section page the tag is within.
        e.g. 'insight'
        """
        return reverse(
            self.url_name,
            kwargs={'section_slug': section_slug, 'tag_slug': self.slug}
        )
