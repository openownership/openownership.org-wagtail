from django.conf import settings

from wagtail.core import blocks
from wagtail.contrib.table_block.blocks import TableBlock

from .generic import (
    ArticleImageBlock,
    CTABlock,
)

from .stream import (
    GlossaryItemBlock,
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
    ('latest_by_focus_area', LatestFocusAreaBlock()),
    ('latest_by_publication_type', LatestPublicationTypeBlock()),
    ('latest_by_sector', LatestSectorBlock()),
]

section_page_blocks: list = [
    ('highlight_pages', HighlightPagesBlock()),
    ('areas_of_focus_block', AreasOfFocusBlock()),
    ('sectors_block', SectorsBlock()),
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
]

team_profile_page_body_blocks: list = article_page_body_blocks

tag_page_body_blocks: list = article_page_body_blocks

category_page_body_blocks: list = article_page_body_blocks
