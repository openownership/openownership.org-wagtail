"""Tests for looking a Notion page's properties up by column id."""

from modules.notion.schemas.columns import Column, Columns

DESCRIPTION = Column("title", "One sentence description (P)")
YEAR = Column("x%7B%5B%3C", "Year (P)")


####################################################################################################
# Helpers
####################################################################################################


def page(*properties) -> dict:
    """A page whose property names and ids are given as (name, id) pairs."""
    return {
        "properties": {
            name: {"id": column_id, "type": "rich_text"} for name, column_id in properties
        },
    }


####################################################################################################
# The lookup
####################################################################################################


def test_a_column_is_found_by_its_id():
    found = Columns(page(("One sentence description (P)", "title")))

    assert found[DESCRIPTION]["id"] == "title"


def test_a_renamed_column_is_still_found():
    """The whole point. Open Ownership rename tracker columns, and Notion keeps
    the id when they do.
    """
    found = Columns(page(("Description", "title")))

    assert found[DESCRIPTION]["id"] == "title"


def test_a_column_that_is_gone_reads_as_nothing():
    """Every `get_*` helper already treats `None` as an empty value, so a
    missing column decodes to a blank rather than raising.
    """
    found = Columns(page(("Year (P)", "x%7B%5B%3C")))

    assert found[DESCRIPTION] is None


def test_a_column_that_is_present_is_reported_as_present():
    found = Columns(page(("Anything at all", "title")))

    assert (DESCRIPTION in found) is True


def test_a_column_that_is_absent_is_reported_as_absent():
    found = Columns(page(("Year (P)", "x%7B%5B%3C")))

    assert (DESCRIPTION in found) is False


def test_a_page_with_no_properties_holds_no_columns():
    assert (DESCRIPTION in Columns({})) is False


def test_the_same_name_under_a_new_id_does_not_match():
    """A column deleted and recreated in Notion keeps its name but gets a new
    id. That is a real break, and it has to look like one.
    """
    found = Columns(page(("One sentence description (P)", "brand%3Dnew")))

    assert (DESCRIPTION in found) is False


####################################################################################################
# The column itself
####################################################################################################


def test_a_column_carries_the_human_name():
    """The name is what error messages and anyone reading the schema sees."""
    assert YEAR.name == "Year (P)"
