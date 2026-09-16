"""
notion.schemas.columns

Notion columns, named for people and matched by id.

Open Ownership rename tracker columns as their own thinking moves on. Notion
keeps a column's id when that happens, so keying the sync off ids means a rename
costs nothing. The human name travels alongside the id purely so the schemas
stay readable and the failure messages stay useful; it can go stale without
anything breaking.

An id is not a complete defence. A column deleted and recreated in Notion keeps
its name but gets a new id, which the sync sees as the column having gone. That
is the case `manpy notion_columns` exists to diagnose.
"""

from typing import NamedTuple, Optional


class Column(NamedTuple):
    """One column of a Notion database.

    Attributes:
        id: Notion's own identifier, which survives a rename. What the sync
            matches on.
        name: The column's name in the tracker, for people reading this code
            and for the messages the sync prints.
    """

    id: str
    name: str


class Columns:
    """One page's property values, addressed by `Column` rather than by name.

    Notion keys its `properties` object by column name, so the values are
    reindexed here by the id each one carries.
    """

    def __init__(self, page: dict):
        properties = page.get("properties") or {}
        self._by_id = {
            value.get("id"): value for value in properties.values() if isinstance(value, dict)
        }

    def __getitem__(self, column: Column) -> Optional[dict]:
        """The value for a column, or `None` if the page does not carry it."""
        return self._by_id.get(column.id)

    def __contains__(self, column: Column) -> bool:
        return column.id in self._by_id
