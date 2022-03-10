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
    GlossaryPage,
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
    TagPage,
    TaxonomyPage,
    TeamPage,
    TeamProfilePage,
    UtilityPage,
    MapPage
)

from .inlines import (  # NOQA
    BlogArticleAuthorRelationship,
    NewsArticleAuthorRelationship,
    PublicationAuthorRelationship,
    PressLinkAuthorRelationship,
)

from .snippets import Author, PressLink  # NOQA


# When we want to get a bunch of Pages that are all "content" - like
# the "latest content" within a section, or "all content tagged with x"
# then which Pages count as "content"? These pages:
content_page_models: list = (  # NOQA
    ArticlePage,
    BlogArticlePage,
    JobPage,
    NewsArticlePage,
    PublicationFrontPage,
)
