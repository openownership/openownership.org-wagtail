"""
notion.icons

Topic icons, mapped in code rather than driven from Notion.

Open Ownership asked whether the tracker could carry an icon per topic (A-S8 in
the sprint brief). Holding the map here instead keeps the icon set consistent and
means an editor cannot break the visuals from Notion. The trade-off they accepted
is that a topic added or renamed in the tracker needs a small change here to get
its own icon; until then it gets `FALLBACK`, which is drawn to look deliberate
rather than broken.

The icon is always shown next to the topic's name, never instead of it, so a
generic icon costs a reader nothing.
"""

from typing import Optional

ICON_DIR = "svg/bot"

# Any topic not named here. Deliberately a real icon rather than a blank.
FALLBACK = f"{ICON_DIR}/fallback.svg"

# Topic name in Notion, lowercased, to its icon file. Lowercased because a
# rename that only changes case should not silently drop the icon.
#
# `aml-cft`, `natural-resources` and `organised-crime` are placeholders drawn to
# match `FALLBACK` while Open Ownership supply the real artwork. Replacing those
# three files is the whole job; nothing here changes.
TOPIC_ICONS = {
    "aml/cft": "aml-cft.svg",
    "business environment": "business-environment.svg",
    "corruption": "corruption.svg",
    "national security": "national-security.svg",
    "natural resources": "natural-resources.svg",
    "organised crime": "organised-crime.svg",
    "public procurement": "public-procurement.svg",
    "real estate and property": "real-estate-and-property.svg",
    "tax": "tax.svg",
    "transparency and oversight": "transparency-and-oversight.svg",
}


def topic_icon(name: Optional[str]) -> str:
    """The template path of a topic's icon.

    Args:
        name: The topic's name as it appears in Notion.

    Returns:
        A path suitable for `include`, falling back to a generic icon for any
        topic not mapped above.
    """
    if not name:
        return FALLBACK

    icon = TOPIC_ICONS.get(name.strip().lower())
    if not icon:
        return FALLBACK

    return f"{ICON_DIR}/{icon}"
