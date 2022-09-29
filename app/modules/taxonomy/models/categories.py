# 3rd party
from consoler import console
from wagtail.models import Locale
from wagtailmodelchooser import register_model_chooser
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

# Module
from .core import Category


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

        if self.name == "News article":
            return self.news_index

        if self.name == "Blog post":
            return self.blog_index

        qs = TagPage.objects

        page = (
            qs.live().public().filter(locale=Locale.get_active())
            .filter(publication_type=self).first()
        )
        if page:
            return page.get_url()
        else:
            return ''

    @cached_property
    def news_index(self):
        from modules.content.models import NewsIndexPage
        try:
            indx = NewsIndexPage.objects.filter(
                locale=Locale.get_active()
            ).live().public().first()
        except Exception as e:
            console.info(e)
            indx = NewsIndexPage.objects.live().public().first()
        if indx:
            return indx.url

    @cached_property
    def blog_index(self):
        from modules.content.models import BlogIndexPage
        try:
            indx = BlogIndexPage.objects.filter(
                locale=Locale.get_active()
            ).live().public().first()
        except Exception as e:
            console.info(e)
            indx = BlogIndexPage.objects.live().public().first()
        if indx:
            return indx.url
