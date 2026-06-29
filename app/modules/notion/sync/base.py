"""
notion.sync.base

The persistence engine. `BaseSyncer` owns the per-row lifecycle that every
database shares: validate, skip-if-unchanged, upsert inside a transaction, and
soft-delete rows that have left Notion. Subclasses describe the source, the
target model, and how to turn a validated row into model fields.
"""

# 3rd party
from django.db import transaction
from loguru import logger
from pydantic import ValidationError

# Module
from modules.notion.report import Outcome, SyncResult
from modules.notion.schemas.rows import NotionRow


class BaseSyncer:
    name: str = ""
    schema: type[NotionRow] = NotionRow
    model = None
    db_key: str = ""

    # Whether rows missing from Notion should be soft-deleted after a run. The
    # regime-sub feed augments existing regimes and owns no rows of its own.
    cleans_up: bool = True

    def __init__(self, client):
        self.client = client

    ################################################################################################
    # Lifecycle
    ################################################################################################

    def run(self, pages: list[dict] = None, force: bool = False, dry_run: bool = False) -> SyncResult:
        result = SyncResult(self.name)
        if pages is None:
            pages = self.client.fetch_database(self.client.database_id(self.db_key))
        result.fetched = len(pages)

        seen = set()
        for page in pages:
            try:
                row = self.schema.from_page(page)
            except ValidationError as err:
                # The row exists in Notion but is malformed. Record it as seen so
                # a validation failure never causes a soft-delete.
                seen.add(page.get("id"))
                result.add_invalid(page.get("id"), err)
                continue

            seen.add(row.notion_id)
            if dry_run:
                result.validated += 1
                continue

            try:
                with transaction.atomic():
                    outcome = self.persist(row, force=force)
            except Exception as err:
                logger.error(f"{self.name}: failed to persist {row.notion_id}: {err}")
                result.add_invalid(row.notion_id, err)
                continue

            result.record(outcome)

        if not dry_run and self.cleans_up:
            result.deleted = self.soft_delete(seen)

        return result

    ################################################################################################
    # Hooks for subclasses
    ################################################################################################

    def persist(self, row: NotionRow, force: bool = False) -> Outcome:
        raise NotImplementedError

    ################################################################################################
    # Shared helpers
    ################################################################################################

    def universals(self, row: NotionRow) -> dict:
        """Fields common to every Notion-backed model."""
        return {
            "notion_created": row.notion_created,
            "notion_updated": row.notion_updated,
            "archived": row.archived,
            "deleted": False,
        }

    def upsert(self, row: NotionRow, defaults: dict, force: bool):
        """Create or update by `notion_id`, skipping rows Notion has not touched.

        Returns the `Outcome` and the model instance. A row is skipped only when
        it already exists, is not soft-deleted, and its `last_edited_time` is no
        newer than what we stored.
        """
        existing = self.model.objects.filter(notion_id=row.notion_id).first()
        if (
            existing is not None
            and not force
            and not existing.deleted
            and existing.notion_updated is not None
            and row.notion_updated <= existing.notion_updated
        ):
            return Outcome.SKIPPED, existing

        created = existing is None
        obj, _ = self.model.objects.update_or_create(
            notion_id=row.notion_id,
            defaults=defaults,
        )
        return (Outcome.CREATED if created else Outcome.UPDATED), obj

    def soft_delete(self, seen: set) -> int:
        """Soft-delete rows whose `notion_id` was not seen in this run."""
        stale = self.model.objects.exclude(notion_id__in=seen).filter(deleted=False)
        return stale.update(deleted=True)
