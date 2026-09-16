# stdlib
import datetime as dt
import re
from decimal import Decimal

# 3rd party
import pytest
from pydantic import ValidationError

# Module
from modules.notion.samples.columns import SCHEMAS
from modules.notion.samples.commitments import COMMITMENTS
from modules.notion.samples.countries import COUNTRIES
from modules.notion.samples.impact import IMPACT
from modules.notion.samples.regimes import REGIMES
from modules.notion.samples.regimes_sub import REGIMES_SUB
from modules.notion.schemas import rows
from modules.notion.schemas.columns import Column
from modules.notion.schemas.rows import (
    BotCols,
    CommitmentCols,
    CommitmentRow,
    CountryCols,
    CountryRow,
    ImpactRow,
    RegimeCols,
    RegimeRow,
    RegimeSubCols,
    RegimeSubRow,
)


####################################################################################################
# Helpers
####################################################################################################


def make_page(properties: dict, **overrides) -> dict:
    """A Notion page whose properties are keyed by `Column`.

    Real responses key `properties` by name and carry the column id inside each
    value, which is what the sync matches on. Naming the column here rather than
    the string means a test cannot accidentally aim at the same column name in a
    different tracker.
    """
    page = {
        "id": "11111111-1111-1111-1111-111111111111",
        "created_time": "2023-11-17T08:56:00.000Z",
        "last_edited_time": "2023-11-21T12:29:00.000Z",
        "archived": False,
        "properties": {
            column.name: {**value, "id": column.id} for column, value in properties.items()
        },
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
            CountryCols.NAME: title("Afghanistan"),
            CountryCols.OO_SUPPORT: select("Medium"),
            CountryCols.ISO2: {"type": "rich_text", "rich_text": [{"plain_text": "AF"}]},
            CountryCols.REGION: select("South Asia"),
        },
        icon={"type": "emoji", "emoji": "🇦🇫"},
    )
    row = CountryRow.from_page(page)
    assert row.name == "Afghanistan"
    assert row.oo_support == "Medium"
    assert row.iso2 == "AF"
    assert row.region == "South Asia"
    assert row.icon == "🇦🇫"
    assert row.notion_created == dt.datetime(2023, 11, 17, 8, 56, tzinfo=dt.timezone.utc)


def test_country_row_missing_name_is_invalid():
    page = make_page({CountryCols.NAME: title(""), CountryCols.OO_SUPPORT: select("Medium")})
    with pytest.raises(ValidationError):
        CountryRow.from_page(page)


def test_country_row_blank_select_defaults_empty():
    page = make_page({CountryCols.NAME: title("Brazil"), CountryCols.OO_SUPPORT: select(None)})
    row = CountryRow.from_page(page)
    assert row.oo_support == ""


def test_country_row_without_a_region_defaults_empty():
    """Not every row in the country tracker carries a region."""
    page = make_page({CountryCols.NAME: title("Brazil"), CountryCols.REGION: select(None)})
    row = CountryRow.from_page(page)
    assert row.region == ""


####################################################################################################
# CommitmentRow
####################################################################################################


def test_commitment_row_valid():
    page = make_page(
        {
            CommitmentCols.COUNTRY: relation("country-abc"),
            CommitmentCols.DATE: {"type": "date", "date": {"start": "2022-02-04"}},
            CommitmentCols.LINK: {"type": "url", "url": "https://example.com"},
            CommitmentCols.COMMITMENT_TYPE: rich_text("Other"),
            CommitmentCols.CENTRAL_REGISTER: checkbox(True),
            CommitmentCols.PUBLIC_REGISTER: checkbox(False),
            CommitmentCols.ALL_SECTORS: checkbox(True),
            CommitmentCols.SUMMARY_TEXT: {"type": "rich_text", "rich_text": [{"plain_text": "Hi"}]},
        },
    )
    row = CommitmentRow.from_page(page)
    assert row.country_id == "country-abc"
    assert row.date == dt.date(2022, 2, 4)
    assert row.central_register is True
    assert row.public_register is False
    assert row.all_sectors is True


def test_commitment_row_without_country_is_invalid():
    page = make_page(
        {CommitmentCols.COUNTRY: relation(), CommitmentCols.CENTRAL_REGISTER: checkbox(True)},
    )
    with pytest.raises(ValidationError):
        CommitmentRow.from_page(page)


####################################################################################################
# RegimeRow
####################################################################################################


def test_regime_row_valid():
    page = make_page(
        {
            RegimeCols.COUNTRY: relation("country-abc"),
            RegimeCols.REGISTER_NAME: title("Register of Beneficial Owners"),
            RegimeCols.IMPLEMENTATION_STAGE: multi_select("Systems", "Publish"),
            RegimeCols.REGISTER_URL: {"type": "url", "url": "https://reg.example"},
            RegimeCols.LAUNCH_DATE: select("2020"),
            RegimeCols.THRESHOLD: {"type": "number", "number": 25},
            RegimeCols.RESPONSIBLE_AGENCY: rich_text("Registrar"),
            RegimeCols.AGENCY_TYPE: select("Government"),
            RegimeCols.SCOPE: multi_select("Full-economy"),
            RegimeCols.WHO_CAN_ACCESS: multi_select("General public", "Registrar"),
        },
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
    page = make_page({RegimeCols.COUNTRY: relation(), RegimeCols.REGISTER_NAME: title("X")})
    with pytest.raises(ValidationError):
        RegimeRow.from_page(page)


def test_regime_row_blank_threshold_is_none():
    page = make_page(
        {
            RegimeCols.COUNTRY: relation("country-abc"),
            RegimeCols.THRESHOLD: {"type": "number", "number": None},
        },
    )
    row = RegimeRow.from_page(page)
    assert row.threshold is None


####################################################################################################
# RegimeSubRow
####################################################################################################


def test_regime_sub_row_tri_state():
    page = make_page(
        {
            RegimeSubCols.DISCLOSURE_REGIME: relation("regime-abc"),
            RegimeSubCols.API_AVAILABLE: select("Yes"),
            RegimeSubCols.BULK_DATA_AVAILABLE: select("No"),
            RegimeSubCols.ON_OO_REGISTER: select(None),
            RegimeSubCols.DATA_IN_BODS: select("No"),
            RegimeSubCols.STRUCTURED_DATA: select("Yes"),
        },
    )
    row = RegimeSubRow.from_page(page)
    assert row.api_available is True
    assert row.bulk_data_available is False
    assert row.on_oo_register is None
    assert row.data_in_bods is False
    assert row.structured_data is True


def test_regime_sub_row_without_regime_is_invalid():
    page = make_page(
        {RegimeSubCols.DISCLOSURE_REGIME: relation(), RegimeSubCols.API_AVAILABLE: select("Yes")},
    )
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


def impact_page(overrides=None):
    props = {
        BotCols.DESCRIPTION: title("Kenyan FIU used BO data in an investigation"),
        BotCols.SUMMARY: rich_text("A longer summary."),
        BotCols.LESSONS: rich_text("What we learned."),
        BotCols.OO_OUTPUTS_USED_IN: rich_text("Briefing note"),
        BotCols.PRESENTATIONS_USED_IN: rich_text("Lagos workshop"),
        BotCols.SOURCE_URL: url("https://example.com/story"),
        BotCols.YEAR: number(2024),
        BotCols.PUBLISH: checkbox(True),
        BotCols.OO_INFLUENCE: checkbox(False),
        BotCols.TANGIBLE_IMPACT: checkbox(True),
        BotCols.INTERNATIONAL: checkbox(False),
        BotCols.ARCHIVE: checkbox(False),
        BotCols.MARKED_OLD: checkbox(False),
        BotCols.ARCHIVED_TYPES: multi_select("Data use"),
        BotCols.JURISDICTIONS: relation("country-1", "country-2"),
        BotCols.DISCLOSURE_REGIMES: relation("regime-1"),
        BotCols.DATA_USER: multi_select("Government: FIU"),
        BotCols.USABILITY_THEMES: multi_select("Identifiers", "Search by person"),
        BotCols.IMPACT_TYPE: multi_select("Data use"),
        BotCols.RESOURCE_TYPE: multi_select("Public sector"),
        BotCols.POLICY_AREA: multi_select("AML/CFT", "Corruption"),
        BotCols.ATTACHMENTS: files(),
    }
    props.update(overrides or {})
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
        ImpactRow.from_page(impact_page({BotCols.DESCRIPTION: title("")}))


def test_impact_row_without_relations_is_valid():
    page = impact_page(
        {BotCols.JURISDICTIONS: relation(), BotCols.DISCLOSURE_REGIMES: relation()},
    )
    row = ImpactRow.from_page(page)
    assert row.country_ids == []
    assert row.regime_ids == []


def test_impact_row_year_may_be_missing():
    row = ImpactRow.from_page(impact_page({BotCols.YEAR: number(None)}))
    assert row.year is None


####################################################################################################
# Attachments on an impact row
####################################################################################################


HOSTED_PDF = "https://prod-files-secure.s3.us-west-2.amazonaws.com/ws/id/gao.pdf?X-Amz-Signature=x"
HOSTED_JPG = "https://prod-files-secure.s3.us-west-2.amazonaws.com/ws/id/IMG%205547.JPG?sig=y"


def attachment_page(*entries):
    return impact_page({BotCols.ATTACHMENTS: files(*entries)})


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
    ("schema", "database"),
    [
        (CountryRow, "countries"),
        (CommitmentRow, "commitments"),
        (RegimeRow, "regimes"),
        (RegimeSubRow, "regimes_sub"),
        (ImpactRow, "bot"),
    ],
)
def test_every_declared_column_id_exists_in_the_database(schema, database):
    """A typo in an id would disarm the guard and silently decode to nothing."""
    present = SCHEMAS[database]
    missing = [column.name for column in schema.COLUMNS if column.id not in present]

    assert missing == []


@pytest.mark.parametrize(
    ("schema", "database"),
    [
        (CountryRow, "countries"),
        (CommitmentRow, "commitments"),
        (RegimeRow, "regimes"),
        (RegimeSubRow, "regimes_sub"),
        (ImpactRow, "bot"),
    ],
)
def test_every_declared_column_name_matches_the_database(schema, database):
    """A stale name breaks nothing, but it misleads the next person reading the
    schema and turns the sync's failure messages into a wild goose chase.
    """
    present = SCHEMAS[database]
    wrong = [
        (column.name, present[column.id])
        for column in schema.COLUMNS
        if column.id in present and column.name != present[column.id]
    ]

    assert wrong == []


@pytest.mark.parametrize(
    "schema",
    [CountryRow, CommitmentRow, RegimeRow, RegimeSubRow, ImpactRow],
)
def test_every_column_the_schema_reads_is_declared(schema):
    """Whatever `extract` reads has to be declared, or the guard misses it."""
    import inspect

    source = inspect.getsource(schema.extract)
    read = set(re.findall(r"Cols\.([A-Z_]+)\]", source))
    declared = {name for name, _ in _declared_columns(schema)}

    assert read - declared == set()


def _declared_columns(schema):
    """The `(attribute, Column)` pairs the schema declares, from its own tuple."""
    holder = _cols_class(schema)
    return [
        (name, value)
        for name, value in vars(holder).items()
        if isinstance(value, Column) and value in schema.COLUMNS
    ]


def _cols_class(schema):
    """The `*Cols` class a row schema draws its columns from."""
    return {
        CountryRow: rows.CountryCols,
        CommitmentRow: rows.CommitmentCols,
        RegimeRow: rows.RegimeCols,
        RegimeSubRow: rows.RegimeSubCols,
        ImpactRow: rows.BotCols,
    }[schema]
