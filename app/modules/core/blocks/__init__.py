from wagtail.core import blocks
from wagtail.contrib.table_block.blocks import TableBlock

from .generic import (
    ArticleImageBlock,
)

from .stream import (
    EmbedBlock
)


home_page_blocks: list = []
landing_page_blocks: list = []
article_page_additional_content_blocks: list = []
contents_page_body_blocks: list = []

article_page_body_blocks: list = [
    (
        "rich_text",
        blocks.RichTextBlock(
            features=[
                "h2", "h3", "h4", "h5", "h6", "bold",
                "italic", "underline", "small", "ol", "ul", "link", "document-link",
            ]
        ),
    ),
    ('embed', EmbedBlock()),
    ('table', TableBlock()),
    ('image', ArticleImageBlock()),
]
