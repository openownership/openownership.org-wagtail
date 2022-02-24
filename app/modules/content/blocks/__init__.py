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
    BlockQuoteBlock,
    # EmbedBannerBlock,
    # LogoListBlock,
    # BannerBlock,
    # LatestNewsBlock,
    LatestSectionContentBlock,
    AreasOfFocusBlock,
    SectorsBlock,
    # CardGroupBlock,
    # TextColumnsBlock,
    # NotificationBlock,
    # SocialMediaBlock,
    # IconListBlock,
    # NewsletterBlock,
    # VideoGalleryBlock,
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
    ('latest_section_content', LatestSectionContentBlock()),
]

section_page_blocks: list = [
    ('areas_of_focus_block', AreasOfFocusBlock()),
    ('sectors_block', SectorsBlock()),
    ('latest_section_content', LatestSectionContentBlock()),
]

article_page_body_blocks: list = [
    (
        "rich_text",
        blocks.RichTextBlock(features=settings.RICHTEXT_BODY_FEATURES),
    ),
    ('embed', EmbedBlock()),
    ('table', TableBlock()),
    ('pull_quote', PullQuoteBlock()),
    ('block_quote', BlockQuoteBlock()),
    ('image', ArticleImageBlock()),
    ('cta_block_form', CTABlock()),
]

team_profile_page_body_blocks: list = article_page_body_blocks

tag_page_body_blocks: list = article_page_body_blocks

category_page_body_blocks: list = article_page_body_blocks
