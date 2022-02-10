# -*- coding: utf-8 -*-

"""
    core.models
    ~~~~~~~~~~~
    We have to import stuff here because Django magic.
"""

from .pages import (  # NOQA
    ArticlePage,
    BlogArticlePage,
    BlogIndexPage,
    HomePage,
    JobPage,
    JobsIndexPage,
    NewsArticlePage,
    NewsIndexPage,
    SearchPage,
    SearchPageSuggestedSearch,
    SectionListingPage,
    SectionPage,
    UtilityPage,
)

from .inlines import (  # NOQA
    BlogArticleAuthorRelationship,
    NewsArticleAuthorRelationship,
)

from .snippets import Author  # NOQA

# from .taxonomy import NewsCategory  # NOQA
