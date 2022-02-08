# -*- coding: utf-8 -*-

"""
    core.models
    ~~~~~~~~~~~
    We have to import stuff here because Django magic.
"""

from .pages import (  # NOQA
    ArticlePage,
    HomePage,
    JobPage,
    JobsIndexPage,
    SearchPage,
    SearchPageSuggestedSearch,
    SectionListingPage,
    UtilityPage,
)

from .inlines import PageFAQList  # NOQA

from .snippets import FAQList, FAQItem  # NOQA

from .taxonomy import NewsCategory  # NOQA
