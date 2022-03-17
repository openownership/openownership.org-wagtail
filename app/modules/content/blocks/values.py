"""
    StructValues
"""

import arrow
from django.db import models
from typing import Optional
from consoler import console
from django.utils.functional import cached_property
from wagtail.core.models import Page, Locale
from wagtail.core import blocks
from django.utils.translation import gettext_lazy as _


class LatestBlogValue(blocks.StructValue):

    @property
    def section_tag(self):
        tag = self.get('section')
        return tag

    @property
    def pages(self):
        from modules.content.models import BlogArticlePage
        qs = BlogArticlePage.objects.live().public().filter(locale=Locale.get_active())
        if self.section_tag:
            related_pages = self.section_tag.section_tag_related_pages.all()
            ids = [item.content_object_id for item in related_pages]
            qs = qs.filter(id__in=ids)

        qs = qs.order_by('-display_date')
        try:
            return qs.all()[:3]
        except Exception as e:
            console.warn(e)
            return []
