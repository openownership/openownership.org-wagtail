from wagtail.core import blocks
from wagtail.contrib.table_block.blocks import TableBlock

from .generic import (
    ArticleImageBlock,
)

from .stream import (
    EmbedBlock,
    StepsBlock,
    QuoteBlock,
    VideoPanelBlock,
    LogoListBlock,
    BannerBlock,
    LatestNewsBlock,
    CardGroupBlock,
    CTAGroupBlock,
    TextColumnsBlock,
    NotificationBlock
)

landing_page_blocks: list = [
    ('steps', StepsBlock()),
    ('video_panel', VideoPanelBlock()),
    ('logo_list', LogoListBlock()),
    ('slim_banner', BannerBlock()),
    ('latest_news', LatestNewsBlock()),
    ('card_group', CardGroupBlock()),
    ('cta_group', CTAGroupBlock()),
    ('text_columns', TextColumnsBlock()),
    ('notification', NotificationBlock())
]


home_page_blocks: list = landing_page_blocks + []

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
    ('quote', QuoteBlock()),
    ('image', ArticleImageBlock()),
]
