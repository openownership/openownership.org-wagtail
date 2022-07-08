# -*- coding: utf-8 -*-

"""
    core.models
    ~~~~~~~~~~~
    We have to import stuff here because Django magic.
"""

# Module
from .pages import (  # NOQA
    JobPage, MapPage, TagPage, HomePage, TeamPage, SearchPage, ArticlePage, SectionPage,
    UtilityPage, GlossaryPage, TaxonomyPage, BlogIndexPage, JobsIndexPage, NewsIndexPage,
    BlogArticlePage, NewsArticlePage, TeamProfilePage, SectionListingPage, PublicationFrontPage,
    PublicationInnerPage, SearchPageSuggestedSearch
)
from .inlines import (  # NOQA
    PressLinkAuthorRelationship, BlogArticleAuthorRelationship, NewsArticleAuthorRelationship,
    PublicationAuthorRelationship
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
