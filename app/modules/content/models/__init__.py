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
    PublicationFrontPage,
    PublicationInnerPage,
    SearchPage,
    SearchPageSuggestedSearch,
    SectionListingPage,
    SectionPage,
    TeamPage,
    TeamProfilePage,
    UtilityPage,
)

from .inlines import (  # NOQA
    BlogArticleAuthorRelationship,
    NewsArticleAuthorRelationship,
    PublicationAuthorRelationship,
)

from .snippets import Author  # NOQA
