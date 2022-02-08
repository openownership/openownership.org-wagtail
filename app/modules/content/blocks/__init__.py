from wagtail.core import blocks
from wagtail.contrib.table_block.blocks import TableBlock

from .generic import (
    ArticleImageBlock,
    CTABlock,
)

from .stream import (
    GlossaryItemBlock,
    EmbedBlock,
    StepsBlock,
    StatsBlock,
    PullQuoteBlock,
    BlockQuoteBlock,
    EmbedBannerBlock,
    LogoListBlock,
    BannerBlock,
    LatestNewsBlock,
    CardGroupBlock,
    TextColumnsBlock,
    NotificationBlock,
    SocialMediaBlock,
    IconListBlock,
    NewsletterBlock,
    VideoGalleryBlock,
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


home_page_blocks: list = landing_page_blocks + []

section_page_blocks: list = landing_page_blocks + []

additional_content_blocks: list = landing_page_blocks

contents_page_body_blocks: list = landing_page_blocks

article_page_body_blocks: list = [
    (
        "rich_text",
        blocks.RichTextBlock(
            features=[
                "h2", "h3", "h4", "h5", "h6", "bold",
                "italic", "small", "ol", "ul", "link", "document-link",
            ]
        ),
    ),
    ('embed', EmbedBlock()),
    ('table', TableBlock()),
    ('pull_quote', PullQuoteBlock()),
    ('block_quote', BlockQuoteBlock()),
    ('image', ArticleImageBlock()),
    ('cta_block_form', CTABlock()),
]
