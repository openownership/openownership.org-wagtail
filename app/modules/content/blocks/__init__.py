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
    # CardGroupBlock,
    # TextColumnsBlock,
    # NotificationBlock,
    # SocialMediaBlock,
    # IconListBlock,
    # NewsletterBlock,
    # VideoGalleryBlock,
    DisclosureBlock,
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
    ('latest_section_content', LatestSectionContentBlock()),
    # ('latest_by_focus_area', LatestFocusAreaBlock()),
    ('latest_by_publication_type', LatestPublicationTypeBlock()),
    ('latest_by_topic', LatestSectorBlock()),
    ('latest_by_section_tag', LatestSectionTagBlock()),
    ('latest_by_open_ownership_principle', LatestPrincipleTagBlock()),
]

section_page_blocks: list = [
    ('highlight_pages', HighlightPagesBlock()),
    # ('areas_of_focus_block', AreasOfFocusBlock()),
    ('topics_block', SectorsBlock()),
    ('latest_section_content', LatestSectionContentBlock()),
    ('publication_types', PublicationTypesBlock()),
    ('press_links', PressLinksBlock()),
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
