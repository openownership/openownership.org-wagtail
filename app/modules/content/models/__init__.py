# -*- coding: utf-8 -*-

"""
    core.models
    ~~~~~~~~~~~
    We have to import stuff here because Django magic.
"""

from .pages import (  # NOQA
    HomePage, SearchPage, UtilityPage,
    SearchPageSuggestedSearch, NewsIndexPage, NewsArticlePage,
    IndexSectionPage, ArticlePage
)

from .inlines import FeaturedNewsArticle, PageFAQList  # NOQA

from .snippets import FAQList, FAQItem  # NOQA

from .taxonomy import NewsCategory  # NOQA
