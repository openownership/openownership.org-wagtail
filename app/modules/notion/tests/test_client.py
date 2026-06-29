# 3rd party
import pytest
from django.test import override_settings
from notion_client.errors import RequestTimeoutError

# Module
from modules.notion.client import NotionClient, NotionConfigError


class FakeDatabases:
    def __init__(self, pages, fail_times=0):
        self._pages = pages
        self._fail_times = fail_times
        self.calls = 0

    def query(self, **kwargs):  # noqa: ARG002
        self.calls += 1
        if self.calls <= self._fail_times:
            raise RequestTimeoutError()
        return {"results": self._pages, "has_more": False, "next_cursor": None}


class FakeClient:
    def __init__(self, pages, fail_times=0):
        self.databases = FakeDatabases(pages, fail_times)


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
