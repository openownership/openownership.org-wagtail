# Module
from modules.notion.models import (
    Commitment,
    CountryTag,
    CoverageScope,
    DisclosureRegime,
)
from modules.notion.sync.runner import run_sync
from modules.notion.sync.syncers import (
    CommitmentSyncer,
    CountrySyncer,
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
