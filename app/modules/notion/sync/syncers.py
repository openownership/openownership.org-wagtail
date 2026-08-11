"""
notion.sync.syncers

One syncer per Notion database. Each maps a validated row onto its Django model.
Countries, commitments, regimes and impact entries own their rows (create,
update, soft-delete); the regime-sub feed augments existing regimes with extra
data-feature fields.
"""

# 3rd party
from django.conf import settings
from django.utils.text import slugify

# Module
from modules.notion.attachments import sync_attachments
from modules.notion.models import (
    AccessTag,
    Commitment,
    CountryTag,
    CoverageScope,
    DataUserTag,
    DisclosureRegime,
    ImpactEntry,
    ImpactTypeTag,
    PolicyAreaTag,
    ResourceTypeTag,
    UsabilityThemeTag,
)
from modules.notion.report import Outcome
from modules.notion.schemas.rows import (
    CommitmentRow,
    CountryRow,
    ImpactRow,
    RegimeRow,
    RegimeSubRow,
)
from modules.notion.sync.base import BaseSyncer

####################################################################################################
# Countries
####################################################################################################


class CountrySyncer(BaseSyncer):
    name = "countries"
    schema = CountryRow
    model = CountryTag
    db_key = "countries"

    def excluded(self, row):
        """Leave out rows that sit in the countries database but are not countries.

        "Global" is the one in use today. The impact tracker points at it to mean
        worldwide, and letting it through would put a country with no ISO2,
        region or map position into the country lists and the CSV exports.
        """
        return row.notion_id in settings.NOTION_NON_COUNTRY_ROWS

    def persist(self, row, force=False):
        defaults = {
            **self.universals(row),
            "name": row.name,
            "slug": slugify(row.name),
            "oo_support": row.oo_support,
            "iso2": row.iso2,
            "icon": row.icon,
        }
        outcome, _ = self.upsert(row, defaults, force)
        return outcome


####################################################################################################
# Commitments
####################################################################################################


class CommitmentSyncer(BaseSyncer):
    name = "commitments"
    schema = CommitmentRow
    model = Commitment
    db_key = "commitments"

    def persist(self, row, force=False):
        country = CountryTag.objects.filter(notion_id=row.country_id).first()
        if country is None:
            return Outcome.MISSING_PARENT
        defaults = {
            **self.universals(row),
            "country": country,
            "date": row.date,
            "link": row.link,
            "commitment_type_name": row.commitment_type_name,
            "central_register": row.central_register,
            "public_register": row.public_register,
            "all_sectors": row.all_sectors,
            "summary_text": row.summary_text,
        }
        outcome, _ = self.upsert(row, defaults, force)
        return outcome


####################################################################################################
# Disclosure regimes (master)
####################################################################################################


class RegimeSyncer(BaseSyncer):
    name = "regimes"
    schema = RegimeRow
    model = DisclosureRegime
    db_key = "regimes"

    def persist(self, row, force=False):
        country = CountryTag.objects.filter(notion_id=row.country_id).first()
        if country is None:
            return Outcome.MISSING_PARENT
        defaults = {
            **self.universals(row),
            "country": country,
            "title": row.title,
            "stage": row.stage,
            "public_access_register_url": row.public_access_register_url,
            "year_launched": row.year_launched,
            "threshold": row.threshold,
            "responsible_agency": row.responsible_agency,
            "agency_type": row.agency_type,
        }
        outcome, obj = self.upsert(row, defaults, force)
        if outcome is not Outcome.SKIPPED:
            self._set_tags(obj, row)
        return outcome

    def _set_tags(self, obj, row):
        """Replace the regime's tag relations to match Notion, then commit.

        The relations are `ParentalManyToManyField`s on a non-clusterable model,
        so writes are deferred until `commit`.
        """
        scopes = [CoverageScope.objects.get_or_create(name=name)[0] for name in row.coverage_scope]
        obj.coverage_scope.set(scopes)
        obj.coverage_scope.commit()

        access = [AccessTag.objects.get_or_create(name=name)[0] for name in row.who_can_access]
        obj.who_can_access.set(access)
        obj.who_can_access.commit()


####################################################################################################
# Disclosure regimes sub (data features)
####################################################################################################


class RegimeSubSyncer(BaseSyncer):
    name = "regimes_sub"
    schema = RegimeSubRow
    model = DisclosureRegime
    db_key = "regimes_sub"

    # This feed writes extra fields onto regimes synced by RegimeSyncer; it does
    # not create or remove regimes.
    cleans_up = False

    FIELDS = (
        "api_available",
        "bulk_data_available",
        "data_in_bods",
        "on_oo_register",
        "structured_data",
    )

    def persist(self, row, force=False):  # noqa: ARG002
        regime = DisclosureRegime.objects.filter(notion_id=row.regime_id).first()
        if regime is None:
            return Outcome.MISSING_PARENT
        for field_name in self.FIELDS:
            setattr(regime, field_name, getattr(row, field_name))
        regime.save(update_fields=list(self.FIELDS))
        return Outcome.UPDATED


####################################################################################################
# BOT impact tracker
####################################################################################################


class ImpactSyncer(BaseSyncer):
    """Recorded uses of beneficial ownership data, with their files.

    Jurisdictions and regimes are optional here: an entry can be worldwide, or
    about data use that no single register owns, so an id we do not hold is
    dropped rather than treated as a missing parent.
    """

    name = "impact"
    schema = ImpactRow
    model = ImpactEntry
    db_key = "bot"

    FIELDS = (
        "description",
        "summary",
        "lessons",
        "oo_outputs_used_in",
        "presentations_used_in",
        "source_url",
        "year",
        "publish",
        "oo_influence",
        "tangible_impact",
        "international",
        "source_archived",
        "source_marked_old",
        "archived_types",
    )

    VOCABULARIES = (
        ("data_users", DataUserTag),
        ("usability_themes", UsabilityThemeTag),
        ("impact_types", ImpactTypeTag),
        ("resource_types", ResourceTypeTag),
        ("policy_areas", PolicyAreaTag),
    )

    def persist(self, row, force=False):
        defaults = {
            **self.universals(row),
            **{name: getattr(row, name) for name in self.FIELDS},
        }
        outcome, obj = self.upsert(row, defaults, force)
        if outcome is not Outcome.SKIPPED:
            self._set_relations(obj, row)
            self._set_vocabularies(obj, row)
            sync_attachments(obj, row.attachments)
        return outcome

    def _set_relations(self, obj, row):
        """Point the entry at the countries and regimes we hold.

        Ids we do not hold are left out. That covers "Global", which is excluded
        from the country sync on purpose, and anything added to Notion since the
        last run of the syncers above.
        """
        country_ids = [
            item for item in row.country_ids if item not in settings.NOTION_NON_COUNTRY_ROWS
        ]
        obj.countries.set(CountryTag.objects.filter(notion_id__in=country_ids))
        obj.regimes.set(DisclosureRegime.objects.filter(notion_id__in=row.regime_ids))

    def _set_vocabularies(self, obj, row):
        """Replace the entry's multi-select tags to match Notion.

        Options are created on sight, so the vocabularies on this side are only
        ever as tidy as the option lists in the source database.
        """
        for field_name, tag_model in self.VOCABULARIES:
            names = getattr(row, field_name)
            tags = [tag_model.objects.get_or_create(name=name)[0] for name in names]
            getattr(obj, field_name).set(tags)
