"""
    StructValues
"""
# 3rd party
from consoler import console
from wagtail import blocks
from wagtail.models import Page, Locale


class SectionLatestValue(blocks.StructValue):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def section_tag(self):
        tag = self.get('section')
        return tag

    @property
    def pages(self):
        if hasattr(self, 'model') and not hasattr(self, 'models'):
            qs = self.model.objects.live().public().filter(locale=Locale.get_active())

        if hasattr(self, 'models') and not hasattr(self, 'model'):
            qs = Page.objects.live().public().specific().filter(
                locale=Locale.get_active()).type(self.models)

        if self.section_tag:
            related_pages = self.section_tag.section_tag_related_pages.all()
            ids = [item.content_object_id for item in related_pages]
            qs = qs.filter(id__in=ids)

        try:
            qs = qs.order_by('-display_date')
        except Exception:
            qs = qs.order_by('-first_published_at')
        try:
            return qs.all()[:3]
        except Exception as e:
            console.warn(e)
            return []


class LatestBlogValue(SectionLatestValue):

    def __init__(self, *args, **kwargs):
        from modules.content.models import BlogArticlePage
        self.model = BlogArticlePage
        super().__init__(*args, **kwargs)


class LatestNewsValue(SectionLatestValue):

    def __init__(self, *args, **kwargs):
        from modules.content.models import NewsArticlePage
        self.model = NewsArticlePage
        super().__init__(*args, **kwargs)


class LatestPublicationsValue(SectionLatestValue):

    def __init__(self, *args, **kwargs):
        from modules.content.models import PublicationFrontPage
        self.model = PublicationFrontPage
        super().__init__(*args, **kwargs)


class LatestContentValue(SectionLatestValue):

    def __init__(self, *args, **kwargs):
        """
            • News article
            • Blog post
            • Event ? doesn't actually exist
            • Job
        """
        from modules.content.models import NewsArticlePage, BlogArticlePage, JobPage
        self.models = (NewsArticlePage, BlogArticlePage, JobPage, )
        super().__init__(*args, **kwargs)
