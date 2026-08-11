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
from typing import Annotated, Optional
from urllib.parse import unquote, urlsplit, urlunsplit

# 3rd party
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

# Module
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


class CountryRow(NotionRow):
    name: str = Field(min_length=1)
    oo_support: str = ""
    iso2: str = ""
    icon: str = ""

    @classmethod
    def extract(cls, page: dict) -> dict:
        props = page.get("properties", {})
        icon = page.get("icon") or {}
        return {
            "name": get_title(props.get("Country")),
            "oo_support": get_select(props.get("OO Support")) or "",
            "iso2": get_rich_text(props.get("ISO2")),
            "icon": icon.get("emoji", ""),
        }


####################################################################################################
# Commitment tracker
####################################################################################################


class CommitmentRow(NotionRow):
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
        props = page.get("properties", {})
        return {
            "country_id": get_first_relation_id(props.get("Country")),
            "date": get_date(props.get("Date")),
            "link": get_url(props.get("Link")) or "",
            "commitment_type_name": get_rich_text(props.get("Commitment type")),
            "central_register": get_checkbox(props.get("Central register")),
            "public_register": get_checkbox(props.get("Public register")),
            "all_sectors": get_checkbox(props.get("All sectors")),
            "summary_text": get_rich_text_html(props.get("Summary Text")),
        }


####################################################################################################
# Disclosure regimes (master)
####################################################################################################


class RegimeRow(NotionRow):
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
        props = page.get("properties", {})
        return {
            "country_id": get_first_relation_id(props.get("Country")),
            "title": get_title(props.get("Register name")),
            "stage": ", ".join(get_multi_select(props.get("Implementation stage"))),
            "public_access_register_url": get_url(props.get("Register URL")) or "",
            "year_launched": get_select(props.get("Launch date")) or "",
            "threshold": get_number(props.get("Threshold (%)")),
            "responsible_agency": get_rich_text(props.get("Responsible agency")),
            "agency_type": get_select(props.get("Agency type")) or "",
            "coverage_scope": get_multi_select(props.get("Scope")),
            "who_can_access": get_multi_select(props.get("Who can access")),
        }


####################################################################################################
# Disclosure regimes sub (data features)
####################################################################################################


class RegimeSubRow(NotionRow):
    regime_id: str = Field(min_length=1)
    api_available: YesNo = None
    bulk_data_available: YesNo = None
    on_oo_register: YesNo = None
    data_in_bods: YesNo = None
    structured_data: YesNo = None

    @classmethod
    def extract(cls, page: dict) -> dict:
        props = page.get("properties", {})
        return {
            "regime_id": get_first_relation_id(props.get("Disclosure regime")),
            "api_available": get_select(props.get("API available")),
            "bulk_data_available": get_select(props.get("Bulk data available")),
            "on_oo_register": get_select(props.get("Data on OO Register")),
            "data_in_bods": get_select(props.get("Data published in BODS")),
            "structured_data": get_select(props.get("Structured data")),
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


class ImpactRow(NotionRow):
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
        props = page.get("properties", {})
        return {
            "description": get_title(props.get("One sentence description (P)")),
            "summary": get_rich_text(props.get("Short summary (P)")),
            "lessons": get_rich_text(props.get("Lessons")),
            "oo_outputs_used_in": get_rich_text(props.get("OO outputs used in")),
            "presentations_used_in": get_rich_text(props.get("Presentations/slide decks used in")),
            "source_url": get_url(props.get("Source URL (P)")) or "",
            "year": get_number(props.get("Year (P)")),
            "publish": get_checkbox(props.get("Publish?")),
            "oo_influence": get_checkbox(props.get("OO's influence")),
            "tangible_impact": get_checkbox(props.get("Tangible impact")),
            "international": get_checkbox(props.get("International")),
            "source_archived": get_checkbox(props.get("Archive")),
            "source_marked_old": get_checkbox(props.get("[TEMP] Old?")),
            "archived_types": ", ".join(get_multi_select(props.get("[Archive]"))),
            "country_ids": get_relation_ids(props.get("Jurisdiction(s) (P)")),
            "regime_ids": get_relation_ids(props.get("Disclosure regime(s)")),
            "data_users": get_multi_select(props.get("Data user")),
            "usability_themes": get_multi_select(props.get("Usability theme(s)")),
            "impact_types": get_multi_select(props.get("Type")),
            "resource_types": get_multi_select(props.get("Type of resource (P)")),
            "policy_areas": get_multi_select(props.get("Policy area (P)")),
            "attachments": get_files(
                props.get("Attach source/supporting documentation if possible"),
            ),
        }
