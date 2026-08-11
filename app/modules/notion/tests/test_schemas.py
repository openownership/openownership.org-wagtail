# stdlib
import datetime as dt
from decimal import Decimal

# 3rd party
import pytest
from pydantic import ValidationError

# Module
from modules.notion.samples.commitments import COMMITMENTS
from modules.notion.samples.countries import COUNTRIES
from modules.notion.samples.impact import IMPACT
from modules.notion.samples.regimes import REGIMES
from modules.notion.samples.regimes_sub import REGIMES_SUB
from modules.notion.schemas.rows import (
    CommitmentRow,
    CountryRow,
    ImpactRow,
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


def rich_text(text: str) -> dict:
    return {"type": "rich_text", "rich_text": [{"type": "text", "plain_text": text}]}


def url(value) -> dict:
    return {"type": "url", "url": value}


def number(value) -> dict:
    return {"type": "number", "number": value}


def files(*entries) -> dict:
    """Build a `files` property from `(label, url, hosted)` triples."""
    items = []
    for label, href, hosted in entries:
        kind = "file" if hosted else "external"
        items.append({"name": label, "type": kind, kind: {"url": href}})
    return {"type": "files", "files": items}


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
        (ImpactRow, IMPACT, 230),
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


####################################################################################################
# BOT impact tracker
####################################################################################################


def impact_page(**overrides):
    props = {
        "One sentence description (P)": title("Kenyan FIU used BO data in an investigation"),
        "Short summary (P)": rich_text("A longer summary."),
        "Lessons": rich_text("What we learned."),
        "OO outputs used in": rich_text("Briefing note"),
        "Presentations/slide decks used in": rich_text("Lagos workshop"),
        "Source URL (P)": url("https://example.com/story"),
        "Year (P)": number(2024),
        "Publish?": checkbox(True),
        "OO's influence": checkbox(False),
        "Tangible impact": checkbox(True),
        "International": checkbox(False),
        "Archive": checkbox(False),
        "[TEMP] Old?": checkbox(False),
        "[Archive]": multi_select("Data use"),
        "Jurisdiction(s) (P)": relation("country-1", "country-2"),
        "Disclosure regime(s)": relation("regime-1"),
        "Data user": multi_select("Government: FIU"),
        "Usability theme(s)": multi_select("Identifiers", "Search by person"),
        "Type": multi_select("Data use"),
        "Type of resource (P)": multi_select("Public sector"),
        "Policy area (P)": multi_select("AML/CFT", "Corruption"),
        "Attach source/supporting documentation if possible": files(),
    }
    props.update(overrides)
    return make_page(props)


def test_impact_row_extracts_scalars():
    row = ImpactRow.from_page(impact_page())
    assert row.description == "Kenyan FIU used BO data in an investigation"
    assert row.summary == "A longer summary."
    assert row.lessons == "What we learned."
    assert row.oo_outputs_used_in == "Briefing note"
    assert row.presentations_used_in == "Lagos workshop"
    assert row.source_url == "https://example.com/story"
    assert row.year == 2024
    assert row.publish is True
    assert row.tangible_impact is True
    assert row.oo_influence is False
    assert row.international is False


def test_impact_row_extracts_housekeeping_flags():
    row = ImpactRow.from_page(impact_page())
    assert row.source_archived is False
    assert row.source_marked_old is False
    assert row.archived_types == "Data use"


def test_impact_row_extracts_relations():
    row = ImpactRow.from_page(impact_page())
    assert row.country_ids == ["country-1", "country-2"]
    assert row.regime_ids == ["regime-1"]


def test_impact_row_extracts_vocabularies():
    row = ImpactRow.from_page(impact_page())
    assert row.data_users == ["Government: FIU"]
    assert row.usability_themes == ["Identifiers", "Search by person"]
    assert row.impact_types == ["Data use"]
    assert row.resource_types == ["Public sector"]
    assert row.policy_areas == ["AML/CFT", "Corruption"]


def test_impact_row_without_a_description_is_invalid():
    with pytest.raises(ValidationError):
        ImpactRow.from_page(impact_page(**{"One sentence description (P)": title("")}))


def test_impact_row_without_relations_is_valid():
    page = impact_page(
        **{"Jurisdiction(s) (P)": relation(), "Disclosure regime(s)": relation()},
    )
    row = ImpactRow.from_page(page)
    assert row.country_ids == []
    assert row.regime_ids == []


def test_impact_row_year_may_be_missing():
    row = ImpactRow.from_page(impact_page(**{"Year (P)": number(None)}))
    assert row.year is None


####################################################################################################
# Attachments on an impact row
####################################################################################################


HOSTED_PDF = "https://prod-files-secure.s3.us-west-2.amazonaws.com/ws/id/gao.pdf?X-Amz-Signature=x"
HOSTED_JPG = "https://prod-files-secure.s3.us-west-2.amazonaws.com/ws/id/IMG%205547.JPG?sig=y"


def attachment_page(*entries):
    return impact_page(
        **{"Attach source/supporting documentation if possible": files(*entries)},
    )


def test_hosted_pdf_is_a_document():
    row = ImpactRow.from_page(attachment_page(("gao.pdf", HOSTED_PDF, True)))
    assert row.attachments[0].kind == "document"


def test_hosted_image_is_an_image():
    row = ImpactRow.from_page(attachment_page(("IMG_5547.JPG", HOSTED_JPG, True)))
    assert row.attachments[0].kind == "image"


def test_external_url_is_a_link_whatever_its_extension():
    entry = ("State_of_Competition.pdf", "https://gov.uk/media/State_of_Competition.pdf", False)
    row = ImpactRow.from_page(attachment_page(entry))
    assert row.attachments[0].kind == "link"


def test_hosted_fingerprint_drops_the_expiring_signature():
    row = ImpactRow.from_page(attachment_page(("gao.pdf", HOSTED_PDF, True)))
    assert row.attachments[0].fingerprint == (
        "https://prod-files-secure.s3.us-west-2.amazonaws.com/ws/id/gao.pdf"
    )


def test_external_fingerprint_is_the_whole_url():
    entry = ("Article 2", "https://media.am/hy/newsroom/2023/02/22/35108/", False)
    row = ImpactRow.from_page(attachment_page(entry))
    assert row.attachments[0].fingerprint == "https://media.am/hy/newsroom/2023/02/22/35108/"


def test_filename_is_decoded_from_the_url_path():
    row = ImpactRow.from_page(attachment_page(("IMG_5547.JPG", HOSTED_JPG, True)))
    assert row.attachments[0].filename == "IMG 5547.JPG"


def test_attachment_keeps_its_notion_label():
    row = ImpactRow.from_page(attachment_page(("Article 2", "https://media.am/x", False)))
    assert row.attachments[0].label == "Article 2"


def test_attachments_keep_their_order():
    row = ImpactRow.from_page(
        attachment_page(
            ("one.pdf", "https://s3.example.com/a/one.pdf", True),
            ("two.png", "https://s3.example.com/a/two.png", True),
            ("three", "https://example.com/three", False),
        ),
    )
    assert [item.kind for item in row.attachments] == ["document", "image", "link"]


def test_impact_row_with_no_attachments():
    assert ImpactRow.from_page(impact_page()).attachments == []


####################################################################################################
# The declared columns match what Notion actually sends
####################################################################################################


@pytest.mark.parametrize(
    ("schema", "dataset"),
    [
        (CountryRow, COUNTRIES),
        (CommitmentRow, COMMITMENTS),
        (RegimeRow, REGIMES),
        (RegimeSubRow, REGIMES_SUB),
        (ImpactRow, IMPACT),
    ],
)
def test_declared_properties_exist_in_the_real_data(schema, dataset):
    """A typo here would disarm the rename guard without anyone noticing."""
    present = set(dataset["results"][0]["properties"])
    missing = [name for name in schema.PROPERTIES if name not in present]

    assert missing == []


@pytest.mark.parametrize(
    ("schema", "dataset"),
    [
        (CountryRow, COUNTRIES),
        (CommitmentRow, COMMITMENTS),
        (RegimeRow, REGIMES),
        (RegimeSubRow, REGIMES_SUB),
        (ImpactRow, IMPACT),
    ],
)
def test_every_property_the_schema_reads_is_declared(schema, dataset):
    """Whatever `extract` reads has to be declared, or the guard misses it."""
    page = dataset["results"][0]
    declared = set(schema.PROPERTIES)
    read = {name for name in page["properties"] if _is_read_by(schema, name)}

    assert read - declared == set()


def _is_read_by(schema, property_name: str) -> bool:
    """Whether `extract` mentions this column by name."""
    import inspect

    return f'"{property_name}"' in inspect.getsource(schema.extract)
