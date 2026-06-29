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
from typing import Annotated, Optional

# 3rd party
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

# Module
from modules.notion.schemas.properties import (
    get_checkbox,
    get_date,
    get_first_relation_id,
    get_multi_select,
    get_number,
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
