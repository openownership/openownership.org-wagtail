"""
notion.schemas.properties

Pure extractor functions that decode a single Notion property envelope into a
plain Python value. Each function accepts the property dict found at
`page['properties'][name]` and tolerates `None` (a missing property) by
returning that type's empty default.

Decoding the Notion envelope shape lives here; type validation lives on the
Pydantic row schemas that consume these values.
"""

# stdlib
from typing import Optional, Union

Number = Union[int, float]


####################################################################################################
# Title and rich text
####################################################################################################


def get_title(prop: Optional[dict]) -> str:
    """Join the `plain_text` of every segment in a `title` property."""
    if not prop:
        return ""
    return "".join(segment.get("plain_text", "") for segment in prop.get("title", []))


def get_rich_text(prop: Optional[dict]) -> str:
    """Join the `plain_text` of every segment in a `rich_text` property."""
    if not prop:
        return ""
    return "".join(segment.get("plain_text", "") for segment in prop.get("rich_text", []))


def get_rich_text_html(prop: Optional[dict]) -> str:
    """Reconstruct a `rich_text` property as HTML, wrapping linked segments in anchors.

    Notion splits a paragraph into segments; a segment carrying a `text.link`
    becomes an `<a>` while plain segments are emitted as-is.
    """
    if not prop:
        return ""
    result = ""
    for segment in prop.get("rich_text", []):
        if segment.get("type") != "text":
            continue
        text = segment.get("text", {})
        content = text.get("content", "")
        link = text.get("link")
        if link:
            result += f'<a href="{link["url"]}">{content}</a>'
        else:
            result += content
    return result


####################################################################################################
# Select and multi-select
####################################################################################################


def get_select(prop: Optional[dict]) -> Optional[str]:
    """Return the selected option `name`, or `None` when nothing is selected."""
    if not prop:
        return None
    selected = prop.get("select")
    if not selected:
        return None
    return selected.get("name")


def get_multi_select(prop: Optional[dict]) -> list[str]:
    """Return the list of selected option names, in order."""
    if not prop:
        return []
    return [item["name"] for item in prop.get("multi_select", [])]


####################################################################################################
# Relation
####################################################################################################


def get_relation_ids(prop: Optional[dict]) -> list[str]:
    """Return every related page id in a `relation` property."""
    if not prop:
        return []
    return [item["id"] for item in prop.get("relation", [])]


def get_first_relation_id(prop: Optional[dict]) -> Optional[str]:
    """Return the first related page id, or `None` when the relation is empty."""
    ids = get_relation_ids(prop)
    return ids[0] if ids else None


####################################################################################################
# Scalars
####################################################################################################


def get_number(prop: Optional[dict]) -> Optional[Number]:
    """Return the value of a `number` property, or `None` when unset."""
    if not prop:
        return None
    return prop.get("number")


def get_checkbox(prop: Optional[dict]) -> bool:
    """Return the value of a `checkbox` property, defaulting to `False`."""
    if not prop:
        return False
    return bool(prop.get("checkbox"))


def get_url(prop: Optional[dict]) -> Optional[str]:
    """Return the value of a `url` property, or `None` when unset."""
    if not prop:
        return None
    return prop.get("url") or None


def get_date(prop: Optional[dict]) -> Optional[str]:
    """Return the ISO `start` of a `date` property, or `None` when unset."""
    if not prop:
        return None
    date = prop.get("date")
    if not date:
        return None
    return date.get("start")
