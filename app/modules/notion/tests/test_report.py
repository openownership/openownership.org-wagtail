# stdlib
import json

# 3rd party
import pytest
from pydantic import ValidationError

# Module
from modules.notion import report
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


####################################################################################################
# Storing a report
####################################################################################################

# A run is written to the database as JSON, so this is a persisted format. The
# tests below pin the two things that matter about one: it survives a real JSON
# round trip, and it can still be read after the shape of a result changes.


def stored(result: SyncResult) -> SyncResult:
    """A result put through JSON exactly as the database would."""
    return SyncResult.from_dict(json.loads(json.dumps(result.as_dict())))


def test_every_counter_survives_the_round_trip():
    result = SyncResult(
        name="impact",
        fetched=237,
        created=4,
        updated=9,
        skipped=220,
        missing_parent=1,
        deleted=2,
        validated=3,
        excluded=1,
    )

    assert stored(result) == result


def test_a_failure_survives_the_round_trip_as_a_pair():
    """JSON has no tuples, so these come back as lists unless they are rebuilt."""
    result = SyncResult(name="impact")
    result.add_invalid(NOTION_ID, blank_description_error())

    restored = stored(result)

    assert restored.invalid == result.invalid
    assert isinstance(restored.invalid[0], tuple)


def test_a_missing_column_survives_the_round_trip():
    result = SyncResult(name="countries", missing_properties=["Country", "ISO2"])

    assert stored(result).missing_properties == ["Country", "ISO2"]


def test_a_counter_added_since_a_run_was_stored_reads_as_zero():
    """Backward compatibility. A run stored before a counter existed still has
    to render rather than raise.
    """
    result = SyncResult.from_dict({"name": "impact", "fetched": 10})

    assert result.fetched == 10
    assert result.created == 0
    assert result.excluded == 0


def test_a_counter_removed_since_a_run_was_stored_is_ignored():
    """Forward compatibility, for the same reason in the other direction."""
    result = SyncResult.from_dict({"name": "impact", "fetched": 10, "gone_away": 4})

    assert result.fetched == 10
    assert not hasattr(result, "gone_away")


def test_a_result_with_no_name_still_loads():
    assert SyncResult.from_dict({}).name == ""


####################################################################################################
# Capping what is stored
####################################################################################################


def test_a_catastrophic_run_does_not_store_every_failure():
    """A column deleted in Notion fails every row. Storing thousands of messages
    per run would put megabytes of JSON in the database for no extra insight.
    """
    result = SyncResult(name="impact")
    for index in range(report.MAX_STORED_INVALID + 50):
        result.invalid.append((f"id-{index}", "boom"))

    stored_result = result.as_dict()

    assert len(stored_result["invalid"]) == report.MAX_STORED_INVALID
    assert stored_result["invalid_dropped"] == 50


def test_the_true_failure_count_is_kept_even_when_the_detail_is_capped():
    result = SyncResult(name="impact")
    for index in range(report.MAX_STORED_INVALID + 50):
        result.invalid.append((f"id-{index}", "boom"))

    assert result.as_dict()["invalid_count"] == report.MAX_STORED_INVALID + 50


def test_nothing_is_dropped_from_an_ordinary_run():
    result = SyncResult(name="impact")
    result.invalid.append(("id-1", "boom"))

    assert result.as_dict()["invalid_dropped"] == 0


####################################################################################################
# Totals across a run
####################################################################################################


def test_totals_add_up_across_every_database():
    report_ = SyncReport()
    report_.add(SyncResult(name="countries", fetched=211, created=1, deleted=2))
    report_.add(SyncResult(name="impact", fetched=237, created=4, deleted=0))

    totals = report_.totals()

    assert totals["fetched"] == 448
    assert totals["created"] == 5
    assert totals["deleted"] == 2


def test_totals_count_failures_and_missing_columns():
    report_ = SyncReport()
    countries = SyncResult(name="countries", missing_properties=["Country"])
    impact = SyncResult(name="impact")
    impact.invalid.append(("id-1", "boom"))
    impact.invalid.append(("id-2", "boom"))
    report_.add(countries)
    report_.add(impact)

    totals = report_.totals()

    assert totals["invalid_count"] == 2
    assert totals["missing_column_count"] == 1


def test_totals_of_an_empty_report_are_all_zero():
    assert set(SyncReport().totals().values()) == {0}


def test_a_whole_report_survives_the_round_trip():
    report_ = SyncReport()
    report_.add(SyncResult(name="countries", fetched=211))
    report_.add(SyncResult(name="impact", fetched=237))

    restored = SyncReport.from_dict(json.loads(json.dumps(report_.as_dict())))

    assert [r.name for r in restored.results] == ["countries", "impact"]
    assert restored.totals() == report_.totals()


def test_a_report_stored_with_no_results_loads_as_empty():
    assert SyncReport.from_dict({}).results == []
