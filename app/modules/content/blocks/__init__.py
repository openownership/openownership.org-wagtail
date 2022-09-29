# 3rd party
from django.conf import settings
from wagtail import blocks
from wagtail.contrib.table_block.blocks import TableBlock

# Module
from .stream import (
    EmbedBlock, SectorsBlock, PullQuoteBlock, DisclosureBlock, LatestBlogBlock, LatestNewsBlock,
    PressLinksBlock, SummaryBoxBlock, EditorsPicksBlock, LatestSectorBlock, LatestContentBlock,
    HighlightPagesBlock, SimilarContentBlock, LatestSectionTagBlock, PublicationTypesBlock,
    LatestPrincipleTagBlock, LatestPublicationsBlock, SearchLatestContentBlock,
    LatestSectionContentBlock, LatestPublicationTypeBlock
)
from .generic import CTABlock, ArticleImageBlock


LANDING_PAGE_BLOCKS: list = [

]


HOME_PAGE_BLOCKS: list = [
    ('highlight_pages', HighlightPagesBlock()),
    ('publication_types', PublicationTypesBlock(label='Content types')),
    ('latest_section_content', LatestSectionContentBlock()),
    ('latest_by_publication_type', LatestPublicationTypeBlock(label='Latest by content type')),
    ('latest_by_topic', LatestSectorBlock()),
    ('latest_by_section_tag', LatestSectionTagBlock()),
    ('latest_by_open_ownership_principle', LatestPrincipleTagBlock()),
    ('latest_from_the_blog', LatestBlogBlock()),
    ('latest_news', LatestNewsBlock()),
    ('latest_publications', LatestPublicationsBlock()),
    ('latest_content', LatestContentBlock()),
]

SECTION_PAGE_BLOCKS: list = [
    ('highlight_pages', HighlightPagesBlock()),
    ('topics_block', SectorsBlock(label="Topics")),
    ('latest_section_content', LatestSectionContentBlock()),
    ('publication_types', PublicationTypesBlock(label='Content types')),
    ('press_links', PressLinksBlock()),
    ('latest_from_the_blog', LatestBlogBlock()),
    ('latest_news', LatestNewsBlock()),
    ('latest_publications', LatestPublicationsBlock()),
]

ARTICLE_PAGE_BODY_BLOCKS: list = [
    (
        "rich_text",
        blocks.RichTextBlock(features=settings.RICHTEXT_BODY_FEATURES),
    ),
    ('embed', EmbedBlock()),
    ('table', TableBlock()),
    ('pull_quote', PullQuoteBlock()),
    ('summary_box', SummaryBoxBlock()),
    ('image', ArticleImageBlock()),
    ('cta_block_form', CTABlock()),
    ('disclosure', DisclosureBlock()),
    ('raw_html', blocks.RawHTMLBlock(label='Raw HTML')),
]

TEAM_PROFILE_PAGE_BODY_BLOCKS: list = ARTICLE_PAGE_BODY_BLOCKS

TAG_PAGE_BODY_BLOCKS: list = ARTICLE_PAGE_BODY_BLOCKS

CATEGORY_PAGE_BODY_BLOCKS: list = ARTICLE_PAGE_BODY_BLOCKS

ADDITIONAL_CONTENT_BLOCKS: list = [
    ('similar_content', SimilarContentBlock()),
    ('highlight_pages', HighlightPagesBlock()),
]

SEARCH_BLOCKS: list = [
    ('editors_picks', EditorsPicksBlock()),
    ('latest_content', SearchLatestContentBlock()),
]
