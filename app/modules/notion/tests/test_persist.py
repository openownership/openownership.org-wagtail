# 3rd party
import pytest
from django.conf import settings

# Module
from modules.notion import attachments as notion_attachments
from modules.notion.models import (
    Commitment,
    CountryTag,
    CoverageScope,
    DisclosureRegime,
    ImpactEntry,
    PolicyAreaTag,
)
from modules.notion.sync.runner import run_sync
from modules.notion.sync.syncers import (
    CommitmentSyncer,
    CountrySyncer,
    ImpactSyncer,
    RegimeSubSyncer,
    RegimeSyncer,
)


####################################################################################################
# Page builders
####################################################################################################


def make_page(properties, notion_id, updated="2023-11-21T12:29:00.000Z"):
    return {
        "id": notion_id,
        "created_time": "2023-11-17T08:56:00.000Z",
        "last_edited_time": updated,
        "archived": False,
        "properties": properties,
    }


def title(text):
    return {"type": "title", "title": [{"type": "text", "plain_text": text}]}


def rich_text(text):
    return {"type": "rich_text", "rich_text": [{"type": "text", "plain_text": text}]}


def select(name):
    return {"type": "select", "select": {"name": name} if name is not None else None}


def multi_select(*names):
    return {"type": "multi_select", "multi_select": [{"name": n} for n in names]}


def relation(*ids):
    return {"type": "relation", "relation": [{"id": i} for i in ids]}


def checkbox(value):
    return {"type": "checkbox", "checkbox": value}


def country_page(notion_id, name, updated="2023-11-21T12:29:00.000Z"):
    return make_page(
        {"Country": title(name), "OO Support": select("Medium"), "ISO2": rich_text("XX")},
        notion_id,
        updated,
    )


def commitment_page(notion_id, country_id, central=False):
    return make_page(
        {
            "Country": relation(country_id),
            "Central register": checkbox(central),
            "Public register": checkbox(False),
            "All sectors": checkbox(False),
            "Commitment type": rich_text("Other"),
        },
        notion_id,
    )


def regime_page(notion_id, country_id, scope=(), access=()):
    return make_page(
        {
            "Country": relation(country_id),
            "Register name": title("Register"),
            "Implementation stage": multi_select("Publish"),
            "Threshold (%)": {"type": "number", "number": 25},
            "Scope": multi_select(*scope),
            "Who can access": multi_select(*access),
        },
        notion_id,
    )


def regime_sub_page(notion_id, regime_id, api="Yes", bods="No"):
    return make_page(
        {
            "Disclosure regime": relation(regime_id),
            "API available": select(api),
            "Data published in BODS": select(bods),
        },
        notion_id,
    )


####################################################################################################
# Countries
####################################################################################################


def test_country_sync_creates():
    res = CountrySyncer(None).run(pages=[country_page("c1", "Afghanistan"), country_page("c2", "Brazil")])
    assert res.created == 2
    assert res.fetched == 2
    assert CountryTag.objects.get(notion_id="c1").name == "Afghanistan"


def test_country_sync_skips_unchanged():
    page = country_page("c1", "Afghanistan", updated="2023-01-01T00:00:00.000Z")
    CountrySyncer(None).run(pages=[page])
    res = CountrySyncer(None).run(pages=[page])
    assert res.skipped == 1
    assert res.updated == 0


def test_country_sync_force_updates_unchanged():
    page = country_page("c1", "Afghanistan", updated="2023-01-01T00:00:00.000Z")
    CountrySyncer(None).run(pages=[page])
    res = CountrySyncer(None).run(pages=[page], force=True)
    assert res.updated == 1


def test_country_sync_soft_deletes_missing():
    CountrySyncer(None).run(pages=[country_page("c1", "Afghanistan"), country_page("c2", "Brazil")])
    CountrySyncer(None).run(pages=[country_page("c1", "Afghanistan")])
    assert CountryTag.objects.get(notion_id="c2").deleted is True
    assert CountryTag.objects.get(notion_id="c1").deleted is False


def test_invalid_row_reported_and_not_clobbered():
    CountrySyncer(None).run(pages=[country_page("c1", "Afghanistan"), country_page("c2", "Brazil")])
    bad = make_page({"Country": title(""), "OO Support": select("Medium")}, "c2")
    res = CountrySyncer(None).run(pages=[country_page("c1", "Afghanistan"), bad])
    assert res.invalid_count == 1
    c2 = CountryTag.objects.get(notion_id="c2")
    assert c2.name == "Brazil"
    assert c2.deleted is False


def test_dry_run_writes_nothing():
    res = CountrySyncer(None).run(pages=[country_page("c1", "Afghanistan")], dry_run=True)
    assert res.validated == 1
    assert res.created == 0
    assert CountryTag.objects.filter(notion_id="c1").count() == 0


####################################################################################################
# Commitments
####################################################################################################


def test_commitment_missing_country_is_skipped():
    res = CommitmentSyncer(None).run(pages=[commitment_page("m1", "unknown")])
    assert res.missing_parent == 1
    assert Commitment.objects.filter(notion_id="m1").count() == 0


def test_commitment_created_with_country():
    CountrySyncer(None).run(pages=[country_page("c1", "Afghanistan")])
    res = CommitmentSyncer(None).run(pages=[commitment_page("m1", "c1", central=True)])
    assert res.created == 1
    com = Commitment.objects.get(notion_id="m1")
    assert com.central_register is True
    assert com.country.notion_id == "c1"


####################################################################################################
# Regimes
####################################################################################################


def test_regime_sets_tags():
    CountrySyncer(None).run(pages=[country_page("c1", "Afghanistan")])
    res = RegimeSyncer(None).run(
        pages=[regime_page("r1", "c1", scope=["Full-economy"], access=["General public", "Registrar"])]
    )
    assert res.created == 1
    regime = DisclosureRegime.objects.get(notion_id="r1")
    assert set(regime.coverage_scope.values_list("name", flat=True)) == {"Full-economy"}
    assert set(regime.who_can_access.values_list("name", flat=True)) == {"General public", "Registrar"}
    assert regime.threshold == 25
    assert CoverageScope.objects.filter(name="Full-economy").exists()


####################################################################################################
# Regime sub
####################################################################################################


def test_regime_sub_updates_existing_regime():
    CountrySyncer(None).run(pages=[country_page("c1", "Afghanistan")])
    RegimeSyncer(None).run(pages=[regime_page("r1", "c1")])
    res = RegimeSubSyncer(None).run(pages=[regime_sub_page("s1", "r1", api="Yes", bods="No")])
    assert res.updated == 1
    regime = DisclosureRegime.objects.get(notion_id="r1")
    assert regime.api_available is True
    assert regime.data_in_bods is False


def test_regime_sub_missing_regime_is_skipped():
    res = RegimeSubSyncer(None).run(pages=[regime_sub_page("s1", "nope")])
    assert res.missing_parent == 1


####################################################################################################
# Runner
####################################################################################################


class FakeClient:
    def __init__(self, data):
        self._data = data

    def database_id(self, name):
        return name

    def fetch_database(self, db_id):
        return self._data.get(db_id, [])


def test_run_sync_orders_dependencies():
    client = FakeClient(
        {
            "countries": [country_page("c1", "Afghanistan")],
            "commitments": [commitment_page("m1", "c1")],
            "regimes": [regime_page("r1", "c1", scope=["Full-economy"])],
            "regimes_sub": [regime_sub_page("s1", "r1", api="Yes")],
        }
    )
    report = run_sync(client=client, notify=False)
    assert not report.has_failures
    assert Commitment.objects.get(notion_id="m1").country.notion_id == "c1"
    assert DisclosureRegime.objects.get(notion_id="r1").api_available is True


####################################################################################################
# Impact tracker
####################################################################################################


def url(value):
    return {"type": "url", "url": value}


def number(value):
    return {"type": "number", "number": value}


def files(*entries):
    """Build a `files` property from `(label, url, hosted)` triples."""
    items = []
    for label, href, hosted in entries:
        kind = "file" if hosted else "external"
        items.append({"name": label, "type": kind, kind: {"url": href}})
    return {"type": "files", "files": items}


def impact_page(notion_id, countries=(), regimes=(), attachments=(), **overrides):
    props = {
        "One sentence description (P)": title("Kenyan FIU used BO data"),
        "Short summary (P)": rich_text("A longer summary."),
        "Lessons": rich_text("What we learned."),
        "Source URL (P)": url("https://example.com/story"),
        "Year (P)": number(2024),
        "Publish?": checkbox(True),
        "Tangible impact": checkbox(True),
        "International": checkbox(False),
        "Jurisdiction(s) (P)": relation(*countries),
        "Disclosure regime(s)": relation(*regimes),
        "Data user": multi_select("Government: FIU"),
        "Policy area (P)": multi_select("AML/CFT", "Corruption"),
        "Type": multi_select("Data use"),
        "Attach source/supporting documentation if possible": files(*attachments),
    }
    props.update(overrides)
    return make_page(props, notion_id)


@pytest.fixture
def no_downloads(monkeypatch):
    monkeypatch.setattr(notion_attachments, "_download", lambda url: b"%PDF-1.4 pretend")  # noqa: ARG005


def test_impact_sync_creates_entry(no_downloads):  # noqa: ARG001
    res = ImpactSyncer(None).run(pages=[impact_page("i1")])

    assert res.created == 1
    entry = ImpactEntry.objects.get(notion_id="i1")
    assert entry.description == "Kenyan FIU used BO data"
    assert entry.summary == "A longer summary."
    assert entry.year == 2024
    assert entry.publish is True
    assert entry.tangible_impact is True


def test_impact_sync_creates_vocabulary_tags(no_downloads):  # noqa: ARG001
    ImpactSyncer(None).run(pages=[impact_page("i1")])

    entry = ImpactEntry.objects.get(notion_id="i1")
    assert set(entry.policy_areas.values_list("name", flat=True)) == {"AML/CFT", "Corruption"}
    assert set(entry.data_users.values_list("name", flat=True)) == {"Government: FIU"}
    assert PolicyAreaTag.objects.filter(name="AML/CFT").exists()


def test_impact_sync_reuses_existing_tags(no_downloads):  # noqa: ARG001
    ImpactSyncer(None).run(pages=[impact_page("i1")])
    ImpactSyncer(None).run(pages=[impact_page("i2")])

    assert PolicyAreaTag.objects.filter(name="AML/CFT").count() == 1


def test_impact_sync_links_countries_and_regimes(no_downloads):  # noqa: ARG001
    CountrySyncer(None).run(pages=[country_page("c1", "Kenya")])
    RegimeSyncer(None).run(pages=[regime_page("r1", "c1")])

    ImpactSyncer(None).run(pages=[impact_page("i1", countries=["c1"], regimes=["r1"])])

    entry = ImpactEntry.objects.get(notion_id="i1")
    assert list(entry.countries.values_list("notion_id", flat=True)) == ["c1"]
    assert list(entry.regimes.values_list("notion_id", flat=True)) == ["r1"]


def test_impact_entry_with_no_jurisdiction_is_still_created(no_downloads):  # noqa: ARG001
    res = ImpactSyncer(None).run(pages=[impact_page("i1")])

    assert res.created == 1
    assert ImpactEntry.objects.get(notion_id="i1").countries.count() == 0


def test_impact_entry_ignores_countries_we_do_not_hold(no_downloads):  # noqa: ARG001
    res = ImpactSyncer(None).run(pages=[impact_page("i1", countries=["nope"])])

    assert res.created == 1
    assert ImpactEntry.objects.get(notion_id="i1").countries.count() == 0


def test_impact_sync_soft_deletes_missing(no_downloads):  # noqa: ARG001
    ImpactSyncer(None).run(pages=[impact_page("i1"), impact_page("i2")])
    ImpactSyncer(None).run(pages=[impact_page("i1")])

    assert ImpactEntry.objects.get(notion_id="i2").deleted is True
    assert ImpactEntry.objects.get(notion_id="i1").deleted is False


def test_impact_sync_stores_attachments(no_downloads):  # noqa: ARG001
    page = impact_page(
        "i1",
        attachments=[
            ("gao.pdf", "https://prod-files-secure.s3.amazonaws.com/ws/gao.pdf?sig=1", True),
            ("Article 2", "https://media.am/story", False),
        ],
    )
    ImpactSyncer(None).run(pages=[page])

    entry = ImpactEntry.objects.get(notion_id="i1")
    assert entry.attachments.count() == 2
    assert entry.attachments.filter(kind="document").get().document is not None
    assert entry.attachments.filter(kind="link").get().url == "https://media.am/story"


def test_impact_row_without_a_description_is_reported(no_downloads):  # noqa: ARG001
    bad = impact_page("i1", **{"One sentence description (P)": title("")})
    res = ImpactSyncer(None).run(pages=[bad])

    assert res.invalid_count == 1
    assert ImpactEntry.objects.filter(notion_id="i1").count() == 0


####################################################################################################
# The "Global" pseudo-country
####################################################################################################


GLOBAL_ID = settings.NOTION_NON_COUNTRY_ROWS[0]


def test_global_is_not_created_as_a_country():
    res = CountrySyncer(None).run(
        pages=[country_page("c1", "Kenya"), country_page(GLOBAL_ID, "Global")],
    )

    assert res.created == 1
    assert res.excluded == 1
    assert CountryTag.objects.filter(notion_id=GLOBAL_ID).count() == 0


def test_global_already_held_is_soft_deleted():
    CountryTag.objects.create(notion_id=GLOBAL_ID, name="Global", slug="global")

    CountrySyncer(None).run(pages=[country_page(GLOBAL_ID, "Global")])

    assert CountryTag.objects.get(notion_id=GLOBAL_ID).deleted is True


def test_impact_entry_ignores_a_global_jurisdiction(no_downloads):  # noqa: ARG001
    CountrySyncer(None).run(pages=[country_page("c1", "Kenya")])

    ImpactSyncer(None).run(pages=[impact_page("i1", countries=[GLOBAL_ID, "c1"])])

    entry = ImpactEntry.objects.get(notion_id="i1")
    assert list(entry.countries.values_list("notion_id", flat=True)) == ["c1"]


def test_global_only_entry_keeps_its_international_flag(no_downloads):  # noqa: ARG001
    page = impact_page("i1", countries=[GLOBAL_ID], **{"International": checkbox(True)})
    ImpactSyncer(None).run(pages=[page])

    entry = ImpactEntry.objects.get(notion_id="i1")
    assert entry.countries.count() == 0
    assert entry.international is True


####################################################################################################
# Runner covers the impact tracker
####################################################################################################


def test_run_sync_includes_impact_after_regimes(no_downloads):  # noqa: ARG001
    client = FakeClient(
        {
            "countries": [country_page("c1", "Kenya")],
            "regimes": [regime_page("r1", "c1")],
            "bot": [impact_page("i1", countries=["c1"], regimes=["r1"])],
        },
    )
    report = run_sync(client=client, notify=False)

    assert not report.has_failures
    entry = ImpactEntry.objects.get(notion_id="i1")
    assert list(entry.regimes.values_list("notion_id", flat=True)) == ["r1"]
