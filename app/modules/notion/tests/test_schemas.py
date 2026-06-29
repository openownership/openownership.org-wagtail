# stdlib
import datetime as dt
from decimal import Decimal

# 3rd party
import pytest
from pydantic import ValidationError

# Module
from modules.notion.samples.commitments import COMMITMENTS
from modules.notion.samples.countries import COUNTRIES
from modules.notion.samples.regimes import REGIMES
from modules.notion.samples.regimes_sub import REGIMES_SUB
from modules.notion.schemas.rows import (
    CommitmentRow,
    CountryRow,
    RegimeRow,
    RegimeSubRow,
)


####################################################################################################
# Helpers
####################################################################################################


def make_page(properties: dict, **overrides) -> dict:
    page = {
        "id": "11111111-1111-1111-1111-111111111111",
        "created_time": "2023-11-17T08:56:00.000Z",
        "last_edited_time": "2023-11-21T12:29:00.000Z",
        "archived": False,
        "properties": properties,
    }
    page.update(overrides)
    return page


def title(text: str) -> dict:
    return {"type": "title", "title": [{"type": "text", "plain_text": text}]}


def relation(*ids: str) -> dict:
    return {"type": "relation", "relation": [{"id": i} for i in ids]}


def select(name) -> dict:
    return {"type": "select", "select": {"name": name} if name is not None else None}


def multi_select(*names: str) -> dict:
    return {"type": "multi_select", "multi_select": [{"name": n} for n in names]}


def checkbox(value: bool) -> dict:
    return {"type": "checkbox", "checkbox": value}


####################################################################################################
# CountryRow
####################################################################################################


def test_country_row_valid():
    page = make_page(
        {
            "Country": title("Afghanistan"),
            "OO Support": select("Medium"),
            "ISO2": {"type": "rich_text", "rich_text": [{"plain_text": "AF"}]},
        },
        icon={"type": "emoji", "emoji": "🇦🇫"},
    )
    row = CountryRow.from_page(page)
    assert row.name == "Afghanistan"
    assert row.oo_support == "Medium"
    assert row.iso2 == "AF"
    assert row.icon == "🇦🇫"
    assert row.notion_created == dt.datetime(2023, 11, 17, 8, 56, tzinfo=dt.timezone.utc)


def test_country_row_missing_name_is_invalid():
    page = make_page({"Country": title(""), "OO Support": select("Medium")})
    with pytest.raises(ValidationError):
        CountryRow.from_page(page)


def test_country_row_blank_select_defaults_empty():
    page = make_page({"Country": title("Brazil"), "OO Support": select(None)})
    row = CountryRow.from_page(page)
    assert row.oo_support == ""


####################################################################################################
# CommitmentRow
####################################################################################################


def test_commitment_row_valid():
    page = make_page(
        {
            "Country": relation("country-abc"),
            "Date": {"type": "date", "date": {"start": "2022-02-04"}},
            "Link": {"type": "url", "url": "https://example.com"},
            "Commitment type": {"type": "rich_text", "rich_text": [{"plain_text": "Other"}]},
            "Central register": checkbox(True),
            "Public register": checkbox(False),
            "All sectors": checkbox(True),
            "Summary Text": {"type": "rich_text", "rich_text": [{"plain_text": "Hi"}]},
        }
    )
    row = CommitmentRow.from_page(page)
    assert row.country_id == "country-abc"
    assert row.date == dt.date(2022, 2, 4)
    assert row.central_register is True
    assert row.public_register is False
    assert row.all_sectors is True


def test_commitment_row_without_country_is_invalid():
    page = make_page({"Country": relation(), "Central register": checkbox(True)})
    with pytest.raises(ValidationError):
        CommitmentRow.from_page(page)


####################################################################################################
# RegimeRow
####################################################################################################


def test_regime_row_valid():
    page = make_page(
        {
            "Country": relation("country-abc"),
            "Register name": title("Register of Beneficial Owners"),
            "Implementation stage": multi_select("Systems", "Publish"),
            "Register URL": {"type": "url", "url": "https://reg.example"},
            "Launch date": select("2020"),
            "Threshold (%)": {"type": "number", "number": 25},
            "Responsible agency": {"type": "rich_text", "rich_text": [{"plain_text": "Registrar"}]},
            "Agency type": select("Government"),
            "Scope": multi_select("Full-economy"),
            "Who can access": multi_select("General public", "Registrar"),
        }
    )
    row = RegimeRow.from_page(page)
    assert row.country_id == "country-abc"
    assert row.title == "Register of Beneficial Owners"
    assert row.stage == "Systems, Publish"
    assert row.year_launched == "2020"
    assert row.threshold == Decimal("25")
    assert row.coverage_scope == ["Full-economy"]
    assert row.who_can_access == ["General public", "Registrar"]


def test_regime_row_without_country_is_invalid():
    page = make_page({"Country": relation(), "Register name": title("X")})
    with pytest.raises(ValidationError):
        RegimeRow.from_page(page)


def test_regime_row_blank_threshold_is_none():
    page = make_page(
        {
            "Country": relation("country-abc"),
            "Threshold (%)": {"type": "number", "number": None},
        }
    )
    row = RegimeRow.from_page(page)
    assert row.threshold is None


####################################################################################################
# RegimeSubRow
####################################################################################################


def test_regime_sub_row_tri_state():
    page = make_page(
        {
            "Disclosure regime": relation("regime-abc"),
            "API available": select("Yes"),
            "Bulk data available": select("No"),
            "Data on OO Register": select(None),
            "Data published in BODS": select("No"),
            "Structured data": select("Yes"),
        }
    )
    row = RegimeSubRow.from_page(page)
    assert row.api_available is True
    assert row.bulk_data_available is False
    assert row.on_oo_register is None
    assert row.data_in_bods is False
    assert row.structured_data is True


def test_regime_sub_row_without_regime_is_invalid():
    page = make_page({"Disclosure regime": relation(), "API available": select("Yes")})
    with pytest.raises(ValidationError):
        RegimeSubRow.from_page(page)


####################################################################################################
# Smoke test against the real sample dumps
####################################################################################################


@pytest.mark.parametrize(
    ("schema", "dataset", "minimum"),
    [
        (CountryRow, COUNTRIES, 190),
        (CommitmentRow, COMMITMENTS, 250),
        (RegimeRow, REGIMES, 95),
        (RegimeSubRow, REGIMES_SUB, 30),
    ],
)
def test_samples_parse(schema, dataset, minimum):
    """Every real row should either validate cleanly or fail only with a
    `ValidationError`. A healthy majority must validate, proving the schema
    handles the live data shape.
    """
    valid = 0
    for page in dataset["results"]:
        try:
            schema.from_page(page)
        except ValidationError:
            continue
        valid += 1
    assert valid >= minimum
