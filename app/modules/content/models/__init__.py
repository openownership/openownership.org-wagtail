# -*- coding: utf-8 -*-

"""
    core.models
    ~~~~~~~~~~~
    We have to import stuff here because Django magic.
"""

from .pages import (  # NOQA
    HomePage, SearchPage, UtilityPage,
    SearchPageSuggestedSearch,
    SectionListingPage, ArticlePage
)

from .inlines import PageFAQList  # NOQA

from .snippets import FAQList, FAQItem  # NOQA

from .taxonomy import NewsCategory  # NOQA
