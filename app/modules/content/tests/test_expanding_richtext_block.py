"""Tests for the expanding rich text block.

The block holds two rich text fields and shows the second only when the reader
asks for it. It is built on `details`, so the reveal is the browser's own and
works with JavaScript off.
"""

# 3rd party
import pytest

# Module
from modules.content.blocks import HYBRID_PAGE_BLOCKS
from modules.content.blocks.stream import ExpandingRichTextBlock

pytestmark = pytest.mark.django_db


def render(intro="<p>The opening paragraph.</p>", extra="<p>The rest of it.</p>"):
    block = ExpandingRichTextBlock()
    return block.render(block.to_python({"intro": intro, "extra": extra}))


####################################################################################################
# What a reader gets
####################################################################################################


def test_the_intro_is_always_shown():
    html = render()

    assert "The opening paragraph." in html
    assert html.index("The opening paragraph.") < html.index("<details")


def test_the_rest_is_inside_the_disclosure():
    """Which is what hides it until the reader opens it, without JavaScript."""
    html = render()

    disclosure = html[html.index("<details") : html.index("</details>")]
    assert "The rest of it." in disclosure


def test_the_control_carries_both_of_its_labels():
    """`details` gives no way to change the summary when it opens, so both words
    are in the markup and CSS shows one of them.
    """
    html = render()

    assert "Read more" in html
    assert "Show less" in html


def test_the_disclosure_is_open_to_nothing_else():
    """The block's own class, so the site's plain `details` styling elsewhere is
    not disturbed by this one.
    """
    html = render()

    assert "expanding-richtext" in html


####################################################################################################
# Where an editor can use it
####################################################################################################


def test_the_block_is_offered_on_hybrid_pages():
    """The only list it belongs to. Nothing else offers it."""
    offered = [
        name
        for name, block in HYBRID_PAGE_BLOCKS
        if isinstance(block, ExpandingRichTextBlock)
    ]

    assert offered == ["expanding_rich_text"]
