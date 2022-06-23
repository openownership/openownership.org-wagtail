from django.conf import settings

from wagtail.core import blocks
from wagtail.contrib.table_block.blocks import TableBlock

from .generic import (
    ArticleImageBlock,
    CTABlock,
)

from .stream import (
    GlossaryItemBlock,
    SimilarContentBlock,
    EmbedBlock,
    # StepsBlock,
    # StatsBlock,
    PullQuoteBlock,
    # BlockQuoteBlock,
    SummaryBoxBlock,
    # EmbedBannerBlock,
    # LogoListBlock,
    # BannerBlock,
    # LatestNewsBlock,
    HighlightPagesBlock,
    LatestSectionContentBlock,
    AreasOfFocusBlock,
    SectorsBlock,
    PublicationTypesBlock,
    LatestFocusAreaBlock,
    LatestPublicationTypeBlock,
    LatestSectorBlock,
    LatestSectionTagBlock,
    LatestPrincipleTagBlock,
    PressLinksBlock,
    LatestBlogBlock,
    LatestNewsBlock,
    LatestPublicationsBlock,
    LatestContentBlock,
    # CardGroupBlock,
    # TextColumnsBlock,
    # NotificationBlock,
    # SocialMediaBlock,
    # IconListBlock,
    # NewsletterBlock,
    # VideoGalleryBlock,
    DisclosureBlock,
    EditorsPicksBlock,
    SearchLatestContentBlock,
)

landing_page_blocks: list = [
    # ('steps', StepsBlock()),
    # ('stats', StatsBlock()),
    # ('embed_banner', EmbedBannerBlock()),
    # ('logo_list', LogoListBlock()),
    # ('slim_banner', BannerBlock()),
    # ('latest_news', LatestNewsBlock()),
    # ('card_group', CardGroupBlock()),
    # ('text_columns', TextColumnsBlock()),
    # ('notification', NotificationBlock()),
    # ('social_media', SocialMediaBlock()),
    # ('icon_list', IconListBlock()),
    # ('newsletter', NewsletterBlock()),
    # ('video_gallery', VideoGalleryBlock()),
]


home_page_blocks: list = [
    ('highlight_pages', HighlightPagesBlock()),
    ('publication_types', PublicationTypesBlock(label='Content types')),
    ('latest_section_content', LatestSectionContentBlock()),
    # ('latest_by_focus_area', LatestFocusAreaBlock()),
    ('latest_by_publication_type', LatestPublicationTypeBlock(label='Latest by content type')),
    ('latest_by_topic', LatestSectorBlock()),
    ('latest_by_section_tag', LatestSectionTagBlock()),
    ('latest_by_open_ownership_principle', LatestPrincipleTagBlock()),
    ('latest_from_the_blog', LatestBlogBlock()),
    ('latest_news', LatestNewsBlock()),
    ('latest_publications', LatestPublicationsBlock()),
    ('latest_content', LatestContentBlock()),
]

section_page_blocks: list = [
    ('highlight_pages', HighlightPagesBlock()),
    # ('areas_of_focus_block', AreasOfFocusBlock()),
    ('topics_block', SectorsBlock(label="Topics")),
    ('latest_section_content', LatestSectionContentBlock()),
    ('publication_types', PublicationTypesBlock(label='Content types')),
    ('press_links', PressLinksBlock()),
    ('latest_from_the_blog', LatestBlogBlock()),
    ('latest_news', LatestNewsBlock()),
    ('latest_publications', LatestPublicationsBlock()),
]

article_page_body_blocks: list = [
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

team_profile_page_body_blocks: list = article_page_body_blocks

tag_page_body_blocks: list = article_page_body_blocks

category_page_body_blocks: list = article_page_body_blocks

additional_content_blocks: list = [
    ('similar_content', SimilarContentBlock()),
    ('highlight_pages', HighlightPagesBlock()),
]

SEARCH_BLOCKS: list = [
    ('editors_picks', EditorsPicksBlock()),
    ('latest_content', SearchLatestContentBlock()),
]
