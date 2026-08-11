# 3rd party
import pytest
from pydantic import ValidationError

# Module
from modules.notion.report import SyncReport, SyncResult, notion_url
from modules.notion.schemas.rows import ImpactRow

NOTION_ID = "3b2880fb-edf9-819e-8609-cba946cbd3e7"


def blank_description_error() -> ValidationError:
    page = {
        "id": NOTION_ID,
        "created_time": "2026-08-04T16:18:00.000Z",
        "last_edited_time": "2026-08-10T10:22:00.000Z",
        "properties": {"One sentence description (P)": {"type": "title", "title": []}},
    }
    with pytest.raises(ValidationError) as caught:
        ImpactRow.from_page(page)
    return caught.value


####################################################################################################
# Describing a failure
####################################################################################################


def test_a_validation_error_names_the_field_and_the_problem():
    result = SyncResult("impact")
    result.add_invalid(NOTION_ID, blank_description_error())

    _, message = result.invalid[0]
    assert message.startswith("description: ")
    assert "at least 1 character" in message


def test_a_validation_error_is_one_line():
    result = SyncResult("impact")
    result.add_invalid(NOTION_ID, blank_description_error())

    assert "\n" not in result.invalid[0][1]


def test_several_bad_fields_are_all_named():
    page = {
        "id": NOTION_ID,
        "created_time": "not a date",
        "last_edited_time": "2026-08-10T10:22:00.000Z",
        "properties": {"One sentence description (P)": {"type": "title", "title": []}},
    }
    with pytest.raises(ValidationError) as caught:
        ImpactRow.from_page(page)

    result = SyncResult("impact")
    result.add_invalid(NOTION_ID, caught.value)

    message = result.invalid[0][1]
    assert "description" in message
    assert "notion_created" in message


def test_an_ordinary_exception_keeps_its_type_and_message():
    result = SyncResult("impact")
    result.add_invalid(NOTION_ID, ValueError("file is too big"))

    assert result.invalid[0][1] == "ValueError: file is too big"


####################################################################################################
# Linking back to Notion
####################################################################################################


def test_notion_url_drops_the_dashes():
    assert notion_url(NOTION_ID) == "https://www.notion.so/3b2880fbedf9819e8609cba946cbd3e7"


def test_notion_url_without_an_id():
    assert notion_url("") == "?"


####################################################################################################
# Details
####################################################################################################


def test_details_names_the_syncer_the_row_and_the_problem():
    result = SyncResult("impact")
    result.add_invalid(NOTION_ID, ValueError("file is too big"))

    details = result.details()
    assert "impact" in details
    assert notion_url(NOTION_ID) in details
    assert "file is too big" in details


def test_details_is_empty_when_nothing_failed():
    assert SyncResult("impact").details() == ""


def test_details_has_one_line_per_bad_row():
    result = SyncResult("impact")
    result.add_invalid(NOTION_ID, ValueError("one"))
    result.add_invalid(NOTION_ID, ValueError("two"))

    assert len(result.details().splitlines()) == 2


def test_report_details_gathers_every_syncer():
    countries = SyncResult("countries")
    countries.add_invalid("c1", ValueError("bad country"))
    impact = SyncResult("impact")
    impact.add_invalid("i1", ValueError("bad entry"))

    report = SyncReport()
    report.add(countries)
    report.add(SyncResult("commitments"))
    report.add(impact)

    details = report.details()
    assert "bad country" in details
    assert "bad entry" in details
    assert len(details.splitlines()) == 2


def test_report_details_is_empty_on_a_clean_run():
    report = SyncReport()
    report.add(SyncResult("impact"))

    assert report.details() == ""
    assert report.has_failures is False
