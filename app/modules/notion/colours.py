"""
notion.colours

Region colours, taken from Open Ownership's secondary brand palette.

Open Ownership asked whether regions could be colour-coded to tell records apart
(A-S8 in the sprint brief). Their secondary palette holds exactly six colours and
the site had exactly six regions, so each region took one.

The listing now groups records by the impact tracker's own regions, which are a
different list, so most records reach `region_colour` under a name this map does
not hold and show no colour at all. Removing the colours is a separate piece of
work, so no seventh colour has been invented in the meantime. The palette's own
meaning is the six stages of implementing beneficial ownership transparency,
which has nothing to do with regions, so the pairing is arbitrary: regions in
alphabetical order against the palette in the order it is printed. Reproducible
and easy to explain, which is the most that can be said for any assignment.

**These colours are never put behind text.** Measured against white and against
the site's body colour, five of the six only reach AA one way round and
`#DB00C9` reaches it neither way (4.33 and 3.59, against the 4.5 AA needs). They
are used as a bar down the card and as a dot beside the region's name, so the
colour is decoration next to a word rather than the only thing carrying meaning.
That is also what was promised on accessibility grounds when this was agreed.
"""

from typing import Optional

# Region name, lowercased, to its colour. The comment names the palette entry it
# comes from, so a change to the brand guidelines can be traced back.
#
# Open Ownership's guidelines print `RGB 245, 245, 245` beside `Hex #1BB0A7` on
# the last swatch. Those are two different colours; the hex matches the printed
# swatch and is what is used here.
REGION_COLOURS = {
    "africa": "#DB00C9",  # Consider
    "asia": "#7F12E0",  # Commit
    "europe": "#009BFE",  # Legal
    "north america": "#00C7E2",  # Systems
    "oceania": "#1EC16F",  # Data
    "south america": "#1BB0A7",  # Publish
}


def region_colour(name: Optional[str]) -> Optional[str]:
    """The colour for a region, or `None` if it has none.

    Args:
        name: The region's name as it appears in Notion.

    Returns:
        A hex colour, or `None` for an unknown region so the caller can leave
        the decoration off rather than invent a colour.
    """
    if not name:
        return None
    return REGION_COLOURS.get(name.strip().lower())


def region_bar(names) -> str:
    """A CSS background for the bar down the side of a record's card.

    A record can span more than one region: fourteen do, mostly Asia and Europe.
    Rather than pick one and mislead, the bar is split evenly between them with
    hard stops, so a two-region record reads as two regions.

    Args:
        names: The region names on the record, in the order they should appear.

    Returns:
        A CSS background value, or an empty string for a record with no region
        we hold a colour for, which leaves the bar off entirely.
    """
    colours = [colour for colour in (region_colour(name) for name in names) if colour]

    if not colours:
        return ""

    if len(colours) == 1:
        return colours[0]

    step = 100 / len(colours)
    stops = [
        f"{colour} {index * step:.4g}% {(index + 1) * step:.4g}%"
        for index, colour in enumerate(colours)
    ]
    return f"linear-gradient(to bottom, {', '.join(stops)})"
