# Module
from modules.notion.schemas import properties as p

from .data import (
    COMPLEX_RICHTEXT,
    COMPLEX_RICHTEXT_TARGET,
    LEGISLATION_RICHTEXT,
    LEGISLATION_RICHTEXT_TARGET,
)


####################################################################################################
# Title
####################################################################################################


def test_get_title():
    prop = {
        "type": "title",
        "title": [{"type": "text", "plain_text": "Afghanistan"}],
    }
    assert p.get_title(prop) == "Afghanistan"


def test_get_title_multi_segment():
    prop = {
        "type": "title",
        "title": [
            {"type": "text", "plain_text": "Open "},
            {"type": "text", "plain_text": "Ownership"},
        ],
    }
    assert p.get_title(prop) == "Open Ownership"


def test_get_title_empty():
    assert p.get_title({"type": "title", "title": []}) == ""


def test_get_title_none():
    assert p.get_title(None) == ""


####################################################################################################
# Rich text
####################################################################################################


def test_get_rich_text_plain():
    prop = COMPLEX_RICHTEXT["properties"]["Summary Text"]
    expected = "Bahrain has made a commitment to beneficial ownership Ministerial Order No. (83) of 2020"
    assert p.get_rich_text(prop) == expected


def test_get_rich_text_empty():
    assert p.get_rich_text({"type": "rich_text", "rich_text": []}) == ""


def test_get_rich_text_none():
    assert p.get_rich_text(None) == ""


def test_get_rich_text_html_single_link():
    prop = LEGISLATION_RICHTEXT["properties"]["2.3 Coverage: Legislation URL"]
    assert p.get_rich_text_html(prop) == LEGISLATION_RICHTEXT_TARGET


def test_get_rich_text_html_mixed():
    prop = COMPLEX_RICHTEXT["properties"]["Summary Text"]
    assert p.get_rich_text_html(prop) == COMPLEX_RICHTEXT_TARGET


####################################################################################################
# Select / multi-select
####################################################################################################


def test_get_select():
    prop = {"type": "select", "select": {"name": "Medium", "color": "orange"}}
    assert p.get_select(prop) == "Medium"


def test_get_select_none_value():
    assert p.get_select({"type": "select", "select": None}) is None


def test_get_select_none():
    assert p.get_select(None) is None


def test_get_multi_select():
    prop = {
        "type": "multi_select",
        "multi_select": [{"name": "Full-economy"}, {"name": "Sectoral: Extractives"}],
    }
    assert p.get_multi_select(prop) == ["Full-economy", "Sectoral: Extractives"]


def test_get_multi_select_empty():
    assert p.get_multi_select({"type": "multi_select", "multi_select": []}) == []


def test_get_multi_select_none():
    assert p.get_multi_select(None) == []


####################################################################################################
# Relation
####################################################################################################


def test_get_relation_ids():
    prop = {"type": "relation", "relation": [{"id": "abc"}, {"id": "def"}]}
    assert p.get_relation_ids(prop) == ["abc", "def"]


def test_get_first_relation_id():
    prop = {"type": "relation", "relation": [{"id": "abc"}, {"id": "def"}]}
    assert p.get_first_relation_id(prop) == "abc"


def test_get_first_relation_id_empty():
    assert p.get_first_relation_id({"type": "relation", "relation": []}) is None


def test_get_first_relation_id_none():
    assert p.get_first_relation_id(None) is None


####################################################################################################
# Number / checkbox / url / date
####################################################################################################


def test_get_number():
    assert p.get_number({"type": "number", "number": 23}) == 23


def test_get_number_zero():
    assert p.get_number({"type": "number", "number": 0}) == 0


def test_get_number_none_value():
    assert p.get_number({"type": "number", "number": None}) is None


def test_get_number_none():
    assert p.get_number(None) is None


def test_get_checkbox_true():
    assert p.get_checkbox({"type": "checkbox", "checkbox": True}) is True


def test_get_checkbox_false():
    assert p.get_checkbox({"type": "checkbox", "checkbox": False}) is False


def test_get_checkbox_none():
    assert p.get_checkbox(None) is False


def test_get_url():
    prop = {"type": "url", "url": "https://example.com"}
    assert p.get_url(prop) == "https://example.com"


def test_get_url_none_value():
    assert p.get_url({"type": "url", "url": None}) is None


def test_get_url_none():
    assert p.get_url(None) is None


def test_get_date():
    prop = {"type": "date", "date": {"start": "2022-02-04", "end": None}}
    assert p.get_date(prop) == "2022-02-04"


def test_get_date_none_value():
    assert p.get_date({"type": "date", "date": None}) is None


def test_get_date_none():
    assert p.get_date(None) is None


####################################################################################################
# Files
####################################################################################################


def test_get_files_hosted():
    prop = {
        "type": "files",
        "files": [
            {
                "name": "report.pdf",
                "type": "file",
                "file": {"url": "https://s3.example.com/abc/report.pdf?sig=1"},
            },
        ],
    }
    assert p.get_files(prop) == [
        {
            "label": "report.pdf",
            "url": "https://s3.example.com/abc/report.pdf?sig=1",
            "hosted": True,
        },
    ]


def test_get_files_external():
    prop = {
        "type": "files",
        "files": [
            {
                "name": "Article 2",
                "type": "external",
                "external": {"url": "https://media.am/story"},
            },
        ],
    }
    assert p.get_files(prop) == [
        {"label": "Article 2", "url": "https://media.am/story", "hosted": False},
    ]


def test_get_files_keeps_order():
    prop = {
        "type": "files",
        "files": [
            {"name": "a", "type": "external", "external": {"url": "https://example.com/a"}},
            {"name": "b", "type": "external", "external": {"url": "https://example.com/b"}},
        ],
    }
    assert [item["label"] for item in p.get_files(prop)] == ["a", "b"]


def test_get_files_skips_entries_without_a_url():
    prop = {"type": "files", "files": [{"name": "broken", "type": "file", "file": {}}]}
    assert p.get_files(prop) == []


def test_get_files_empty():
    assert p.get_files({"type": "files", "files": []}) == []


def test_get_files_none():
    assert p.get_files(None) == []
