# 3rd party
import pytest
from django.test import override_settings
from notion_client.errors import RequestTimeoutError

# Module
from modules.notion.client import NotionClient, NotionConfigError


class FakeDatabases:
    def __init__(self, pages, fail_times=0, schema=None):
        self._pages = pages
        self._fail_times = fail_times
        self._schema = schema or {}
        self.calls = 0

    def query(self, **kwargs):  # noqa: ARG002
        self.calls += 1
        if self.calls <= self._fail_times:
            raise RequestTimeoutError()
        return {"results": self._pages, "has_more": False, "next_cursor": None}

    def retrieve(self, database_id):  # noqa: ARG002
        return {"properties": self._schema}


class FakeClient:
    def __init__(self, pages, fail_times=0, schema=None):
        self.databases = FakeDatabases(pages, fail_times, schema)


@override_settings(NOTION_DATABASES={"countries": "db-countries"})
def test_database_id_resolves_from_settings():
    nc = NotionClient(client=FakeClient([]))
    assert nc.database_id("countries") == "db-countries"


@override_settings(NOTION_DATABASES={"countries": "db-countries"})
def test_database_id_unknown_raises():
    nc = NotionClient(client=FakeClient([]))
    with pytest.raises(NotionConfigError):
        nc.database_id("nope")


def test_fetch_database_returns_pages():
    pages = [{"id": "a"}, {"id": "b"}]
    nc = NotionClient(client=FakeClient(pages))
    assert nc.fetch_database("db") == pages


def test_fetch_database_retries_transient_errors():
    pages = [{"id": "a"}]
    fake = FakeClient(pages, fail_times=2)
    calls = []
    nc = NotionClient(client=fake, sleep=lambda s: calls.append(s))
    assert nc.fetch_database("db") == pages
    assert fake.databases.calls == 3
    assert len(calls) == 2


def test_fetch_database_gives_up_after_max_attempts():
    fake = FakeClient([], fail_times=99)
    nc = NotionClient(client=fake, sleep=lambda s: None)
    with pytest.raises(RequestTimeoutError):
        nc.fetch_database("db")


@override_settings(NOTION_WAGTAIL_TOKEN="")
def test_missing_token_raises():
    with pytest.raises(NotionConfigError):
        NotionClient()


####################################################################################################
# Column ids
####################################################################################################


def test_fetch_columns_pairs_each_name_with_its_id():
    schema = {
        "Country": {"id": "title", "type": "title"},
        "ISO2": {"id": "abc%3D", "type": "rich_text"},
    }
    nc = NotionClient(client=FakeClient([], schema=schema))

    assert nc.fetch_columns("db") == [
        ("Country", "title", "title"),
        ("ISO2", "abc%3D", "rich_text"),
    ]


def test_fetch_columns_sorts_by_name():
    """So two runs can be compared without the API's ordering getting in the way."""
    schema = {
        "Zebra": {"id": "z", "type": "rich_text"},
        "Apple": {"id": "a", "type": "rich_text"},
    }
    nc = NotionClient(client=FakeClient([], schema=schema))

    assert [name for name, _, _ in nc.fetch_columns("db")] == ["Apple", "Zebra"]


def test_fetch_columns_on_a_database_with_no_columns():
    nc = NotionClient(client=FakeClient([], schema={}))

    assert nc.fetch_columns("db") == []
