"""
notion.report

Structured results for a sync run. Each syncer produces a `SyncResult`; the
runner gathers them into a `SyncReport` it can summarise for the console and
for Slack.

A report is also stored against a `SyncRun` so the admin can show whether the
sync is still working, which makes `as_dict` a persisted format rather than a
convenience. `from_dict` is deliberately forgiving in both directions: a run
stored before a counter existed still has to render, and one stored after a
counter was dropped must not raise. Nothing here may import Django, so
`notion.models` can depend on this module and never the other way round.
"""

# stdlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# 3rd party
from pydantic import ValidationError

# The most failures stored against a single database in one run. A column
# deleted in Notion fails every row it touches, and a few thousand near-identical
# messages would put megabytes of JSON in the database without saying anything
# the first hundred did not. The true count is kept alongside.
MAX_STORED_INVALID = 100

# Every counter a result carries, which is also what a run stores and totals.
COUNTERS = (
    "fetched",
    "created",
    "updated",
    "skipped",
    "missing_parent",
    "deleted",
    "validated",
    "excluded",
)


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
    missing_properties: list[str] = field(default_factory=list)
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
        """One line per problem: which syncer, which row, and what was wrong."""
        lines = []
        if self.missing_properties:
            columns = ", ".join(repr(name) for name in self.missing_properties)
            lines.append(
                f"  {self.name}  SKIPPED, Notion is no longer sending: {columns}. "
                f"Renamed or deleted in Notion?",
            )
        lines.extend(
            f"  {self.name}  {notion_url(notion_id)}  {message}"
            for notion_id, message in self.invalid
        )
        return "\n".join(lines)

    def summary(self) -> str:
        """One line describing this result."""
        return (
            f"{self.name}: {self.fetched} fetched, {self.created} created, "
            f"{self.updated} updated, {self.skipped} unchanged, "
            f"{self.missing_parent} no-parent, {self.deleted} soft-deleted, "
            f"{self.excluded} excluded, {self.invalid_count} invalid"
        )

    def as_dict(self) -> dict:
        """This result as JSON-safe data, for storing against a run.

        Written out field by field rather than with `dataclasses.asdict`, because
        that would quietly change the stored shape the moment a field is renamed.
        """
        kept = self.invalid[:MAX_STORED_INVALID]
        return {
            "name": self.name,
            **{name: getattr(self, name) for name in COUNTERS},
            "missing_properties": list(self.missing_properties),
            "invalid": [[notion_id, message] for notion_id, message in kept],
            # The real total, which survives the cap above.
            "invalid_count": self.invalid_count,
            "invalid_dropped": max(0, self.invalid_count - len(kept)),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SyncResult":
        """Rebuild a result from stored data, tolerating a change of shape."""
        result = cls(name=data.get("name", ""))
        for name in COUNTERS:
            setattr(result, name, data.get(name, 0))
        result.missing_properties = list(data.get("missing_properties", []))
        result.invalid = [
            (entry[0], entry[1]) for entry in data.get("invalid", []) if len(entry) == 2
        ]
        return result


@dataclass
class SyncReport:
    """The combined outcome of a whole sync run."""

    results: list[SyncResult] = field(default_factory=list)

    def add(self, result: SyncResult) -> None:
        self.results.append(result)

    @property
    def has_failures(self) -> bool:
        return any(r.invalid_count or r.missing_properties for r in self.results)

    def summary(self) -> str:
        return "\n".join(r.summary() for r in self.results)

    def details(self) -> str:
        """Every problem across the whole run, or an empty string if there were none."""
        return "\n".join(
            r.details() for r in self.results if r.invalid or r.missing_properties
        )

    def totals(self) -> dict:
        """Every counter summed across the run.

        The one definition of a run's headline numbers, used by the stored run,
        by the report listing and by the tests, so the three cannot drift.
        """
        totals = {name: 0 for name in COUNTERS}
        totals["invalid_count"] = 0
        totals["missing_column_count"] = 0

        for result in self.results:
            for name in COUNTERS:
                totals[name] += getattr(result, name)
            totals["invalid_count"] += result.invalid_count
            totals["missing_column_count"] += len(result.missing_properties)

        return totals

    def as_dict(self) -> dict:
        return {"results": [result.as_dict() for result in self.results]}

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "SyncReport":
        results = (data or {}).get("results", [])
        return cls(results=[SyncResult.from_dict(item) for item in results])
