"""
notion.report

Structured results for a sync run. Each syncer produces a `SyncResult`; the
runner gathers them into a `SyncReport` it can summarise for the console and
for Slack.
"""

# stdlib
from dataclasses import dataclass, field
from enum import Enum

# 3rd party
from pydantic import ValidationError


def notion_url(notion_id: str) -> str:
    """A link to a row in Notion, so a reported failure can be opened and fixed."""
    slug = notion_id.replace("-", "").strip()
    if not slug:
        return "?"
    return f"https://www.notion.so/{slug}"


def describe(error: Exception) -> str:
    """One line saying what was wrong with a row.

    Pydantic reports each bad field over several lines with a documentation
    link, which is too much for a console summary or a Slack message, so its
    errors are reduced to `field: what was wrong`.
    """
    if isinstance(error, ValidationError):
        return "; ".join(
            f"{'.'.join(str(part) for part in item['loc']) or '(row)'}: {item['msg']}"
            for item in error.errors()
        )
    return f"{type(error).__name__}: {error}"


class Outcome(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    SKIPPED = "skipped"
    MISSING_PARENT = "missing_parent"


@dataclass
class SyncResult:
    """The outcome of syncing one Notion database."""

    name: str
    fetched: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    missing_parent: int = 0
    deleted: int = 0
    validated: int = 0
    excluded: int = 0
    invalid: list[tuple[str, str]] = field(default_factory=list)

    def record(self, outcome: Outcome) -> None:
        if outcome is Outcome.CREATED:
            self.created += 1
        elif outcome is Outcome.UPDATED:
            self.updated += 1
        elif outcome is Outcome.SKIPPED:
            self.skipped += 1
        elif outcome is Outcome.MISSING_PARENT:
            self.missing_parent += 1

    def add_invalid(self, notion_id: str, error: Exception) -> None:
        self.invalid.append((notion_id or "?", describe(error)))

    @property
    def invalid_count(self) -> int:
        return len(self.invalid)

    def details(self) -> str:
        """One line per bad row: which syncer, which row, and what was wrong."""
        return "\n".join(
            f"  {self.name}  {notion_url(notion_id)}  {message}"
            for notion_id, message in self.invalid
        )

    def summary(self) -> str:
        """One line describing this result."""
        return (
            f"{self.name}: {self.fetched} fetched, {self.created} created, "
            f"{self.updated} updated, {self.skipped} unchanged, "
            f"{self.missing_parent} no-parent, {self.deleted} soft-deleted, "
            f"{self.excluded} excluded, {self.invalid_count} invalid"
        )


@dataclass
class SyncReport:
    """The combined outcome of a whole sync run."""

    results: list[SyncResult] = field(default_factory=list)

    def add(self, result: SyncResult) -> None:
        self.results.append(result)

    @property
    def has_failures(self) -> bool:
        return any(r.invalid_count for r in self.results)

    def summary(self) -> str:
        return "\n".join(r.summary() for r in self.results)

    def details(self) -> str:
        """Every bad row across the whole run, or an empty string if there were none."""
        return "\n".join(r.details() for r in self.results if r.invalid)
