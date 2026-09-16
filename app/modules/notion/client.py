"""
notion.client

A thin wrapper over `notion_client` that resolves credentials and database ids
from Django settings, paginates a database query into a full list of pages, and
retries transient API failures. The underlying client is injectable so the sync
layers can be tested without touching the network.
"""

# stdlib
import time
from typing import Callable, Optional

# 3rd party
from django.conf import settings
from notion_client import Client
from notion_client.errors import APIResponseError, HTTPResponseError, RequestTimeoutError
from notion_client.helpers import collect_paginated_api

# Transient failures worth retrying. A 4xx that is not rate limiting is not retried.
RETRYABLE_ERRORS = (HTTPResponseError, RequestTimeoutError)

MAX_ATTEMPTS = 3
BACKOFF_SECONDS = 2


class NotionConfigError(Exception):
    """Raised when the sync is missing the configuration it needs to run."""


class NotionClient:
    def __init__(
        self,
        token: Optional[str] = None,
        client: Optional[Client] = None,
        sleep: Callable[[float], None] = time.sleep,
    ):
        self._sleep = sleep
        if client is not None:
            self._client = client
            return
        token = token or settings.NOTION_WAGTAIL_TOKEN
        if not token:
            raise NotionConfigError(
                "No Notion token. Set NOTION_WAGTAIL_TOKEN in the environment.",
            )
        self._client = Client(auth=token)

    def database_id(self, name: str) -> str:
        """Resolve a configured database id by its short name."""
        try:
            return settings.NOTION_DATABASES[name]
        except KeyError as err:
            raise NotionConfigError(f"No Notion database configured for {name!r}") from err

    def fetch_database(self, db_id: str) -> list[dict]:
        """Return every page in a Notion database, following pagination.

        Retries transient API errors with a simple exponential backoff. A
        rate-limit response (429) carries a `Retry-After` header which is
        honoured in preference to the backoff.
        """
        attempt = 1
        while True:
            try:
                return collect_paginated_api(
                    self._client.databases.query,
                    database_id=db_id,
                )
            except RETRYABLE_ERRORS as err:
                if attempt >= MAX_ATTEMPTS:
                    raise
                self._sleep(self._retry_delay(err, attempt))
                attempt += 1

    def fetch_columns(self, db_id: str) -> list[tuple[str, str, str]]:
        """Every column of a database as `(name, id, type)`, sorted by name.

        The sync matches columns by id, so this is how an id is captured in the
        first place and how a change is diagnosed later. Sorted so the output of
        two runs can be compared directly.
        """
        schema = self._client.databases.retrieve(database_id=db_id)
        properties = schema.get("properties") or {}
        return sorted(
            (name, value.get("id", ""), value.get("type", ""))
            for name, value in properties.items()
        )

    def _retry_delay(self, err: Exception, attempt: int) -> float:
        """Seconds to wait before the next attempt, honouring `Retry-After`."""
        if isinstance(err, APIResponseError):
            headers = getattr(getattr(err, "response", None), "headers", {}) or {}
            retry_after = headers.get("Retry-After")
            if retry_after:
                try:
                    return float(retry_after)
                except ValueError:
                    pass
        return BACKOFF_SECONDS * attempt
