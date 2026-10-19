"""Blocks that list chosen pages must cope with a chosen page that no longer exists.

A chooser value becomes `None` when the page is deleted, or when a preview is
rendered before the editor picks a page.
"""

import pytest

from modules.content.blocks.stream import EditorsPicksBlock, HighlightPagesBlock

pytestmark = pytest.mark.django_db

MISSING_PAGE_ID = 999999


def test_highlight_pages_skips_a_missing_page():
    block = HighlightPagesBlock()
    value = block.to_python(
        {"pages": [{"page": MISSING_PAGE_ID, "card_format": "landscape", "embed": None}]},
    )

    assert block.get_context(value)["pages"] == []


def test_editors_picks_skips_a_missing_page():
    block = EditorsPicksBlock()
    value = block.to_python({"pages": [{"page": MISSING_PAGE_ID}]})

    assert block.get_context(value)["pages"] == []
