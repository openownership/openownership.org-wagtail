"""
notion.schemas.rows

Pydantic models, one per Notion database row. Each model declares the typed
shape we expect and a `from_page` constructor that decodes a raw Notion page
into validated data. A row that does not validate raises `ValidationError`,
which the sync runner catches to skip and report the row rather than writing
empty values over good data.
"""

# stdlib
import datetime as dt
from decimal import Decimal
from pathlib import PurePosixPath
from typing import Annotated, ClassVar, Optional
from urllib.parse import unquote, urlsplit, urlunsplit

# 3rd party
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

# Module
from modules.notion.schemas.columns import Column, Columns
from modules.notion.schemas.properties import (
    get_checkbox,
    get_date,
    get_files,
    get_first_relation_id,
    get_multi_select,
    get_number,
    get_relation_ids,
    get_rich_text,
    get_rich_text_html,
    get_select,
    get_title,
    get_url,
)


def _yes_no_to_bool(value: object) -> Optional[bool]:
    """Map a Notion `Yes`/`No` select name to a tri-state boolean.

    Anything that is not a clear yes or no (blank, unset, an unexpected option)
    becomes `None`, meaning we have no answer for that field.
    """
    if value is None or isinstance(value, bool):
        return value
    normalised = str(value).strip().lower()
    if normalised in ("yes", "true"):
        return True
    if normalised in ("no", "false"):
        return False
    return None


YesNo = Annotated[Optional[bool], BeforeValidator(_yes_no_to_bool)]

# Extensions Wagtail can make renditions from. Anything else Notion hosts is
# treated as a document.
IMAGE_EXTENSIONS = frozenset(
    {".avif", ".bmp", ".gif", ".jpeg", ".jpg", ".png", ".tif", ".tiff", ".webp"},
)

KIND_DOCUMENT = "document"
KIND_IMAGE = "image"
KIND_LINK = "link"


####################################################################################################
# Base
####################################################################################################


class NotionRow(BaseModel):
    """Fields shared by every Notion row, drawn from the page envelope."""

    model_config = ConfigDict(str_strip_whitespace=True)

    # Every Notion column `extract` reads. The sync checks these are still
    # there before it writes anything, because a column that has gone decodes to
    # an empty value rather than an error and would otherwise be written over
    # good data and reported as a success.
    #
    # These are matched by id, not by name, so Open Ownership can rename a
    # tracker column without the sync noticing. See `schemas.columns`.
    COLUMNS: ClassVar[tuple[Column, ...]] = ()

    notion_id: str = Field(min_length=1)
    notion_created: dt.datetime
    notion_updated: dt.datetime
    archived: bool = False

    @classmethod
    def from_page(cls, page: dict) -> "NotionRow":
        """Decode a raw Notion page dict into a validated row."""
        data = {
            "notion_id": page.get("id"),
            "notion_created": page.get("created_time"),
            "notion_updated": page.get("last_edited_time"),
            "archived": page.get("archived", False),
        }
        data.update(cls.extract(page))
        return cls.model_validate(data)

    @classmethod
    def extract(cls, page: dict) -> dict:
        """Pull this row's typed fields out of the page properties."""
        raise NotImplementedError


####################################################################################################
# Country tracker
####################################################################################################


class CountryCols:
    """Columns of the country tracker."""

    NAME = Column("title", "Country")
    OO_SUPPORT = Column("%25%24OQ", "OO Support")
    ISO2 = Column("H%24!6", "ISO2")
    REGION = Column("NtuA", "Region")

    ALL = (NAME, OO_SUPPORT, ISO2, REGION)


class CountryRow(NotionRow):
    COLUMNS = CountryCols.ALL

    name: str = Field(min_length=1)
    oo_support: str = ""
    iso2: str = ""
    icon: str = ""
    region: str = ""

    @classmethod
    def extract(cls, page: dict) -> dict:
        cols = Columns(page)
        icon = page.get("icon") or {}
        return {
            "name": get_title(cols[CountryCols.NAME]),
            "oo_support": get_select(cols[CountryCols.OO_SUPPORT]) or "",
            "iso2": get_rich_text(cols[CountryCols.ISO2]),
            "icon": icon.get("emoji", ""),
            "region": get_select(cols[CountryCols.REGION]) or "",
        }


####################################################################################################
# Commitment tracker
####################################################################################################


class CommitmentCols:
    """Columns of the commitment tracker."""

    COUNTRY = Column("X'sx", "Country")
    DATE = Column("%3Ao%7C%23", "Date")
    LINK = Column("-ifl", "Link")
    COMMITMENT_TYPE = Column(")UWR", "Commitment type")
    CENTRAL_REGISTER = Column("o)_-", "Central register")
    PUBLIC_REGISTER = Column("%3C%7C%3Cz", "Public register")
    ALL_SECTORS = Column("j%22%5DW", "All sectors")
    SUMMARY_TEXT = Column("ZC(N", "Summary Text")

    ALL = (
        COUNTRY,
        DATE,
        LINK,
        COMMITMENT_TYPE,
        CENTRAL_REGISTER,
        PUBLIC_REGISTER,
        ALL_SECTORS,
        SUMMARY_TEXT,
    )


class CommitmentRow(NotionRow):
    COLUMNS = CommitmentCols.ALL

    country_id: str = Field(min_length=1)
    date: Optional[dt.date] = None
    link: str = ""
    commitment_type_name: str = ""
    central_register: bool = False
    public_register: bool = False
    all_sectors: bool = False
    summary_text: str = ""

    @classmethod
    def extract(cls, page: dict) -> dict:
        cols = Columns(page)
        return {
            "country_id": get_first_relation_id(cols[CommitmentCols.COUNTRY]),
            "date": get_date(cols[CommitmentCols.DATE]),
            "link": get_url(cols[CommitmentCols.LINK]) or "",
            "commitment_type_name": get_rich_text(cols[CommitmentCols.COMMITMENT_TYPE]),
            "central_register": get_checkbox(cols[CommitmentCols.CENTRAL_REGISTER]),
            "public_register": get_checkbox(cols[CommitmentCols.PUBLIC_REGISTER]),
            "all_sectors": get_checkbox(cols[CommitmentCols.ALL_SECTORS]),
            "summary_text": get_rich_text_html(cols[CommitmentCols.SUMMARY_TEXT]),
        }


####################################################################################################
# Disclosure regimes (master)
####################################################################################################


class RegimeCols:
    """Columns of the disclosure regime tracker."""

    COUNTRY = Column("PTKs", "Country")
    REGISTER_NAME = Column("title", "Register name")
    IMPLEMENTATION_STAGE = Column("86%605", "Implementation stage")
    REGISTER_URL = Column("X%26sR", "Register URL")
    LAUNCH_DATE = Column("x%5EQC", "Launch date")
    THRESHOLD = Column("%24I.J", "Threshold (%)")
    RESPONSIBLE_AGENCY = Column("Nkzy", "Responsible agency")
    AGENCY_TYPE = Column("GzVi", "Agency type")
    SCOPE = Column("Z%3Dqf", "Scope")
    WHO_CAN_ACCESS = Column("jxf!", "Who can access")

    ALL = (
        COUNTRY,
        REGISTER_NAME,
        IMPLEMENTATION_STAGE,
        REGISTER_URL,
        LAUNCH_DATE,
        THRESHOLD,
        RESPONSIBLE_AGENCY,
        AGENCY_TYPE,
        SCOPE,
        WHO_CAN_ACCESS,
    )


class RegimeRow(NotionRow):
    COLUMNS = RegimeCols.ALL

    country_id: str = Field(min_length=1)
    title: str = ""
    stage: str = ""
    public_access_register_url: str = ""
    year_launched: str = ""
    threshold: Optional[Decimal] = None
    responsible_agency: str = ""
    agency_type: str = ""
    coverage_scope: list[str] = Field(default_factory=list)
    who_can_access: list[str] = Field(default_factory=list)

    @classmethod
    def extract(cls, page: dict) -> dict:
        cols = Columns(page)
        return {
            "country_id": get_first_relation_id(cols[RegimeCols.COUNTRY]),
            "title": get_title(cols[RegimeCols.REGISTER_NAME]),
            "stage": ", ".join(get_multi_select(cols[RegimeCols.IMPLEMENTATION_STAGE])),
            "public_access_register_url": get_url(cols[RegimeCols.REGISTER_URL]) or "",
            "year_launched": get_select(cols[RegimeCols.LAUNCH_DATE]) or "",
            "threshold": get_number(cols[RegimeCols.THRESHOLD]),
            "responsible_agency": get_rich_text(cols[RegimeCols.RESPONSIBLE_AGENCY]),
            "agency_type": get_select(cols[RegimeCols.AGENCY_TYPE]) or "",
            "coverage_scope": get_multi_select(cols[RegimeCols.SCOPE]),
            "who_can_access": get_multi_select(cols[RegimeCols.WHO_CAN_ACCESS]),
        }


####################################################################################################
# Disclosure regimes sub (data features)
####################################################################################################


class RegimeSubCols:
    """Columns of the disclosure regime data features tracker."""

    DISCLOSURE_REGIME = Column("_qpq", "Disclosure regime")
    API_AVAILABLE = Column("Rs%3D%7C", "API available")
    BULK_DATA_AVAILABLE = Column("mkyf", "Bulk data available")
    ON_OO_REGISTER = Column("y%3D%7Bs", "Data on OO Register")
    DATA_IN_BODS = Column("G%5D%3B%7D", "Data published in BODS")
    STRUCTURED_DATA = Column("ybCM", "Structured data")

    ALL = (
        DISCLOSURE_REGIME,
        API_AVAILABLE,
        BULK_DATA_AVAILABLE,
        ON_OO_REGISTER,
        DATA_IN_BODS,
        STRUCTURED_DATA,
    )


class RegimeSubRow(NotionRow):
    COLUMNS = RegimeSubCols.ALL

    regime_id: str = Field(min_length=1)
    api_available: YesNo = None
    bulk_data_available: YesNo = None
    on_oo_register: YesNo = None
    data_in_bods: YesNo = None
    structured_data: YesNo = None

    @classmethod
    def extract(cls, page: dict) -> dict:
        cols = Columns(page)
        return {
            "regime_id": get_first_relation_id(cols[RegimeSubCols.DISCLOSURE_REGIME]),
            "api_available": get_select(cols[RegimeSubCols.API_AVAILABLE]),
            "bulk_data_available": get_select(cols[RegimeSubCols.BULK_DATA_AVAILABLE]),
            "on_oo_register": get_select(cols[RegimeSubCols.ON_OO_REGISTER]),
            "data_in_bods": get_select(cols[RegimeSubCols.DATA_IN_BODS]),
            "structured_data": get_select(cols[RegimeSubCols.STRUCTURED_DATA]),
        }


####################################################################################################
# BOT impact tracker
####################################################################################################


class NotionFile(BaseModel):
    """One item from a Notion `files` property.

    Notion re-signs the urls of files it hosts on every fetch, so the url alone
    cannot say whether we already hold a file. `fingerprint` strips the signature
    and gives a value stable across runs.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    label: str = ""
    url: str = Field(min_length=1)
    hosted: bool = False

    @property
    def _path(self) -> str:
        return urlsplit(self.url).path

    @property
    def extension(self) -> str:
        return PurePosixPath(self._path).suffix.lower()

    @property
    def filename(self) -> str:
        return unquote(PurePosixPath(self._path).name)

    @property
    def kind(self) -> str:
        """Where this item should end up: Wagtail images, documents, or a link."""
        if not self.hosted:
            return KIND_LINK
        if self.extension in IMAGE_EXTENSIONS:
            return KIND_IMAGE
        return KIND_DOCUMENT

    @property
    def fingerprint(self) -> str:
        """A value identifying this item across syncs."""
        if not self.hosted:
            return self.url
        parts = urlsplit(self.url)
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


class BotCols:
    """Columns of the BOT impact tracker.

    Three of these names are due to change: `Data user` becomes Type, `Policy
    area (P)` becomes Topic and `Source URL (P)` becomes Link. Because the sync
    matches on the ids, that rename is a non-event. Updating the names here
    afterwards is tidying, not repair.
    """

    DESCRIPTION = Column("title", "One sentence description (P)")
    SUMMARY = Column("%5EE%3B%3C", "Short summary (P)")
    LESSONS = Column("dJ%3EA", "Lessons")
    OO_OUTPUTS_USED_IN = Column("LORe", "OO outputs used in")
    PRESENTATIONS_USED_IN = Column("R%5D%3FH", "Presentations/slide decks used in")
    SOURCE_URL = Column("ka%3CB", "Source URL (P)")
    YEAR = Column("x%7B%5B%3C", "Year (P)")
    PUBLISH = Column("J%60Y%3F", "Publish?")
    OO_INFLUENCE = Column("L%5EZN", "OO's influence")
    TANGIBLE_IMPACT = Column("QTHZ", "Tangible impact")
    INTERNATIONAL = Column("wgwg", "International")
    ARCHIVE = Column("s_dh", "Archive")
    MARKED_OLD = Column("j%7Cit", "[TEMP] Old?")
    ARCHIVED_TYPES = Column("J%3DgA", "[Archive]")
    JURISDICTIONS = Column("uMFg", "Jurisdiction(s) (P)")
    DISCLOSURE_REGIMES = Column("OZh_", "Disclosure regime(s)")
    DATA_USER = Column("CAQ%3A", "Data user")
    USABILITY_THEMES = Column("OfYG", "Usability theme(s)")
    IMPACT_TYPE = Column("R%5Dk~", "Type")
    RESOURCE_TYPE = Column("RsOD", "Type of resource (P)")
    POLICY_AREA = Column("%5Di%60%5E", "Policy area (P)")
    ATTACHMENTS = Column("otX%3B", "Attach source/supporting documentation if possible")

    ALL = (
        DESCRIPTION,
        SUMMARY,
        LESSONS,
        OO_OUTPUTS_USED_IN,
        PRESENTATIONS_USED_IN,
        SOURCE_URL,
        YEAR,
        PUBLISH,
        OO_INFLUENCE,
        TANGIBLE_IMPACT,
        INTERNATIONAL,
        ARCHIVE,
        MARKED_OLD,
        ARCHIVED_TYPES,
        JURISDICTIONS,
        DISCLOSURE_REGIMES,
        DATA_USER,
        USABILITY_THEMES,
        IMPACT_TYPE,
        RESOURCE_TYPE,
        POLICY_AREA,
        ATTACHMENTS,
    )


class ImpactRow(NotionRow):
    COLUMNS = BotCols.ALL

    description: str = Field(min_length=1)
    summary: str = ""
    lessons: str = ""
    oo_outputs_used_in: str = ""
    presentations_used_in: str = ""
    source_url: str = ""
    year: Optional[int] = None
    publish: bool = False
    oo_influence: bool = False
    tangible_impact: bool = False
    international: bool = False
    source_archived: bool = False
    source_marked_old: bool = False
    archived_types: str = ""
    country_ids: list[str] = Field(default_factory=list)
    regime_ids: list[str] = Field(default_factory=list)
    data_users: list[str] = Field(default_factory=list)
    usability_themes: list[str] = Field(default_factory=list)
    impact_types: list[str] = Field(default_factory=list)
    resource_types: list[str] = Field(default_factory=list)
    policy_areas: list[str] = Field(default_factory=list)
    attachments: list[NotionFile] = Field(default_factory=list)

    @classmethod
    def extract(cls, page: dict) -> dict:
        cols = Columns(page)
        return {
            "description": get_title(cols[BotCols.DESCRIPTION]),
            "summary": get_rich_text(cols[BotCols.SUMMARY]),
            "lessons": get_rich_text(cols[BotCols.LESSONS]),
            "oo_outputs_used_in": get_rich_text(cols[BotCols.OO_OUTPUTS_USED_IN]),
            "presentations_used_in": get_rich_text(cols[BotCols.PRESENTATIONS_USED_IN]),
            "source_url": get_url(cols[BotCols.SOURCE_URL]) or "",
            "year": get_number(cols[BotCols.YEAR]),
            "publish": get_checkbox(cols[BotCols.PUBLISH]),
            "oo_influence": get_checkbox(cols[BotCols.OO_INFLUENCE]),
            "tangible_impact": get_checkbox(cols[BotCols.TANGIBLE_IMPACT]),
            "international": get_checkbox(cols[BotCols.INTERNATIONAL]),
            "source_archived": get_checkbox(cols[BotCols.ARCHIVE]),
            "source_marked_old": get_checkbox(cols[BotCols.MARKED_OLD]),
            "archived_types": ", ".join(get_multi_select(cols[BotCols.ARCHIVED_TYPES])),
            "country_ids": get_relation_ids(cols[BotCols.JURISDICTIONS]),
            "regime_ids": get_relation_ids(cols[BotCols.DISCLOSURE_REGIMES]),
            "data_users": get_multi_select(cols[BotCols.DATA_USER]),
            "usability_themes": get_multi_select(cols[BotCols.USABILITY_THEMES]),
            "impact_types": get_multi_select(cols[BotCols.IMPACT_TYPE]),
            "resource_types": get_multi_select(cols[BotCols.RESOURCE_TYPE]),
            "policy_areas": get_multi_select(cols[BotCols.POLICY_AREA]),
            "attachments": get_files(cols[BotCols.ATTACHMENTS]),
        }
