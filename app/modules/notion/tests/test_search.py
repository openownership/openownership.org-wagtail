# 3rd party
import pytest
from django.core.management import call_command

# Module
from modules.notion import search
from modules.notion.models import (
    CountryTag,
    DataUserTag,
    ImpactEntry,
    PolicyAreaTag,
    Region,
    ResourceTypeTag,
    UsabilityThemeTag,
)


####################################################################################################
# Fakes
####################################################################################################


class FakeIndex:
    """Records what the real Meilisearch client would have been asked to do."""

    def __init__(self, documents=None):
        self.settings = {}
        self.added = []
        self.deleted = []
        self.searches = []
        self._documents = documents or []

    def update_settings(self, body):
        self.settings.update(body)

    def add_documents(self, documents, primary_key=None):
        self.added.append((documents, primary_key))
        return {"taskUid": 1}

    def delete_documents(self, ids):
        self.deleted.append(ids)
        return {"taskUid": 2}

    def get_documents(self, parameters=None):
        parameters = parameters or {}
        offset = parameters.get("offset", 0)
        limit = parameters.get("limit", 20)
        page = self._documents[offset : offset + limit]
        return type("Results", (), {"results": page, "total": len(self._documents)})()

    def search(self, query, opt_params=None):
        self.searches.append((query, opt_params))
        return {"hits": [], "estimatedTotalHits": 0}


class FakeClient:
    def __init__(self, documents=None):
        self.indexes = {}
        self.created = []
        self._documents = documents or []

    def create_index(self, uid, options=None):
        self.created.append((uid, options))

    def index(self, uid):
        if uid not in self.indexes:
            self.indexes[uid] = FakeIndex(self._documents)
        return self.indexes[uid]


####################################################################################################
# Fixtures
####################################################################################################


@pytest.fixture
def kenya():
    region = Region.objects.create(name="Africa")
    country = CountryTag.objects.create(notion_id="c-ke", name="Kenya", slug="kenya", iso2="KE")
    country.regions.add(region)
    return country


@pytest.fixture
def entry(kenya):
    item = ImpactEntry.objects.create(
        notion_id="e1",
        description="Kenyan FIU used BO data in an investigation",
        summary="A longer summary.",
        source_url="https://example.com/story",
        year=2024,
        publish=True,
    )
    item.countries.add(kenya)
    item.policy_areas.add(
        PolicyAreaTag.objects.create(name="Corruption"),
        PolicyAreaTag.objects.create(name="AML/CFT"),
    )
    item.data_users.add(DataUserTag.objects.create(name="Government: FIU"))
    item.resource_types.add(ResourceTypeTag.objects.create(name="Public sector"))
    item.usability_themes.add(UsabilityThemeTag.objects.create(name="Identifiers"))
    return item


####################################################################################################
# Building a document
####################################################################################################


def test_document_carries_the_public_text(entry):
    document = search.build_document(entry)

    assert document["id"] == entry.pk
    assert document["description"] == "Kenyan FIU used BO data in an investigation"
    assert document["summary"] == "A longer summary."
    assert document["source_url"] == "https://example.com/story"


def test_year_stays_a_number(entry):
    """A string year would break numeric filters like year > 2020."""
    assert search.build_document(entry)["year"] == 2024
    assert isinstance(search.build_document(entry)["year"], int)


def test_vocabularies_stay_as_lists(entry):
    """Flattening these to one string is exactly what makes faceting useless."""
    document = search.build_document(entry)

    assert document["policy_areas"] == ["AML/CFT", "Corruption"]
    assert document["data_users"] == ["Government: FIU"]
    assert document["resource_types"] == ["Public sector"]
    assert document["usability_themes"] == ["Identifiers"]


def test_jurisdiction_and_region_come_from_the_country(entry):
    document = search.build_document(entry)

    assert document["jurisdictions"] == ["Kenya"]
    assert document["regions"] == ["Africa"]


def test_a_region_is_not_repeated_when_two_countries_share_it(entry):
    region = Region.objects.get(name="Africa")
    nigeria = CountryTag.objects.create(notion_id="c-ng", name="Nigeria", slug="nigeria")
    nigeria.regions.add(region)
    entry.countries.add(nigeria)

    document = search.build_document(entry)

    assert document["jurisdictions"] == ["Kenya", "Nigeria"]
    assert document["regions"] == ["Africa"]


def test_internal_notes_are_not_indexed(entry):
    """Lessons and the OO output fields are not marked public in the tracker."""
    entry.lessons = "Internal reflection"
    entry.oo_outputs_used_in = "Internal briefing"
    entry.save()

    document = search.build_document(entry)

    assert "lessons" not in document
    assert "oo_outputs_used_in" not in document
    assert "presentations_used_in" not in document
    assert "publish" not in document
    assert "archived_types" not in document


def test_an_entry_with_no_tags_or_countries(kenya):  # noqa: ARG001
    bare = ImpactEntry.objects.create(notion_id="e2", description="Bare entry", publish=True)

    document = search.build_document(bare)

    assert document["policy_areas"] == []
    assert document["jurisdictions"] == []
    assert document["regions"] == []
    assert document["year"] is None


####################################################################################################
# Sort keys
####################################################################################################


def test_topic_sort_is_the_first_policy_area(entry):
    assert search.build_document(entry)["topic_sort"] == "aml/cft"


def test_topic_sort_is_empty_without_a_policy_area(entry):
    entry.policy_areas.clear()

    assert search.build_document(entry)["topic_sort"] == ""


def test_sort_title_is_lowercased(entry):
    document = search.build_document(entry)

    assert document["sort_title"] == "kenyan fiu used bo data in an investigation"


def test_the_default_sort_is_year_then_topic_then_title():
    assert search.DEFAULT_SORT == ["year:desc", "topic_sort:asc", "sort_title:asc"]


def test_every_sort_attribute_is_declared_sortable():
    for term in search.DEFAULT_SORT:
        assert term.split(":")[0] in search.SORTABLE_ATTRIBUTES


####################################################################################################
# Which entries are indexed
####################################################################################################


def test_only_entries_cleared_for_publication_are_indexed(entry):
    ImpactEntry.objects.create(notion_id="e3", description="Not cleared", publish=False)

    assert [d["id"] for d in search.documents()] == [entry.pk]


def test_soft_deleted_entries_are_not_indexed(entry):
    entry.deleted = True
    entry.save()

    assert search.documents() == []


####################################################################################################
# Filters
####################################################################################################


def test_a_single_filter_value():
    assert search.build_filter({"year": [2024]}) == "year IN [2024]"


def test_several_values_for_one_filter():
    built = search.build_filter({"policy_areas": ["AML/CFT", "Tax"]})

    assert built == 'policy_areas IN ["AML/CFT", "Tax"]'


def test_filters_are_combined_with_and():
    built = search.build_filter({"year": [2024], "regions": ["Africa"]})

    assert built == 'year IN [2024] AND regions IN ["Africa"]'


def test_a_quote_in_a_value_is_escaped():
    built = search.build_filter({"jurisdictions": ['Cote d"Ivoire']})

    assert built == 'jurisdictions IN ["Cote d\\"Ivoire"]'


def test_no_filters():
    assert search.build_filter({}) == ""
    assert search.build_filter(None) == ""


def test_an_empty_value_list_is_ignored():
    assert search.build_filter({"year": [], "regions": ["Africa"]}) == 'regions IN ["Africa"]'


def test_an_unknown_filter_is_refused():
    with pytest.raises(ValueError, match="not filterable"):
        search.build_filter({"lessons": ["anything"]})


####################################################################################################
# Configuring the index
####################################################################################################


def test_configure_sets_every_attribute_group():
    client = FakeClient()

    search.configure_index(client)

    settings = client.index(search.INDEX_NAME).settings
    assert settings["searchableAttributes"] == search.SEARCHABLE_ATTRIBUTES
    assert settings["filterableAttributes"] == search.FILTERABLE_ATTRIBUTES
    assert settings["sortableAttributes"] == search.SORTABLE_ATTRIBUTES


def test_configure_creates_the_index_with_its_primary_key():
    client = FakeClient()

    search.configure_index(client)

    assert client.created == [(search.INDEX_NAME, {"primaryKey": search.PRIMARY_KEY})]


def test_every_filterable_attribute_is_also_searchable_or_deliberately_not():
    """Year is a number, so it filters and sorts but is not free-text searchable."""
    not_searchable = set(search.FILTERABLE_ATTRIBUTES) - set(search.SEARCHABLE_ATTRIBUTES)

    assert not_searchable == {"year"}


####################################################################################################
# Reindexing
####################################################################################################


def test_reindex_adds_the_published_entries(entry):
    client = FakeClient()

    result = search.reindex(client=client)

    documents, primary_key = client.index(search.INDEX_NAME).added[0]
    assert [d["id"] for d in documents] == [entry.pk]
    assert primary_key == search.PRIMARY_KEY
    assert result["indexed"] == 1


def test_reindex_removes_entries_that_are_no_longer_published(entry):
    stale = {"id": 999}
    client = FakeClient(documents=[{"id": entry.pk}, stale])

    result = search.reindex(client=client)

    assert client.index(search.INDEX_NAME).deleted == [[999]]
    assert result["removed"] == 1


def test_reindex_does_not_empty_the_index_first(entry):  # noqa: ARG001
    """Deleting everything up front would leave search blank mid-run."""
    client = FakeClient()

    search.reindex(client=client)

    assert client.index(search.INDEX_NAME).deleted == []


def test_reindex_configures_the_index_too(entry):  # noqa: ARG001
    client = FakeClient()

    search.reindex(client=client)

    assert client.index(search.INDEX_NAME).settings["sortableAttributes"]


####################################################################################################
# Searching
####################################################################################################


def test_search_applies_the_default_sort_and_facets():
    client = FakeClient()

    search.search("beneficial ownership", client=client)

    query, params = client.index(search.INDEX_NAME).searches[0]
    assert query == "beneficial ownership"
    assert params["sort"] == search.DEFAULT_SORT
    assert params["facets"] == search.FILTERABLE_ATTRIBUTES


def test_search_passes_filters_through():
    client = FakeClient()

    search.search("", filters={"regions": ["Africa"]}, client=client)

    _, params = client.index(search.INDEX_NAME).searches[0]
    assert params["filter"] == 'regions IN ["Africa"]'


def test_search_without_filters_sends_none():
    client = FakeClient()

    search.search("", client=client)

    _, params = client.index(search.INDEX_NAME).searches[0]
    assert "filter" not in params


def test_search_paginates():
    client = FakeClient()

    search.search("", limit=10, offset=30, client=client)

    _, params = client.index(search.INDEX_NAME).searches[0]
    assert params["limit"] == 10
    assert params["offset"] == 30


####################################################################################################
# Management command
####################################################################################################


def test_index_evidence_reports_what_it_did(monkeypatch, capsys):
    monkeypatch.setattr(search, "reindex", lambda: {"indexed": 121, "removed": 3, "withheld": 2})

    call_command("index_evidence")

    assert "evidence: 121 indexed, 3 removed, 2 withheld" in capsys.readouterr().out


def test_index_evidence_can_apply_settings_only(monkeypatch, capsys):
    applied = []
    monkeypatch.setattr(search, "configure_index", lambda: applied.append(True))
    monkeypatch.setattr(search, "reindex", lambda: pytest.fail("should not reindex"))

    call_command("index_evidence", "--configure-only")

    assert applied == [True]
    assert "settings applied" in capsys.readouterr().out


####################################################################################################
# Records with no link
####################################################################################################


def test_a_record_with_no_link_is_not_indexed(entry):
    """OO asked for these to be left out entirely: every record points at its source."""
    ImpactEntry.objects.create(notion_id="e9", description="No source", publish=True)

    assert [d["id"] for d in search.documents()] == [entry.pk]


def test_reindex_reports_what_was_withheld(entry):  # noqa: ARG001
    ImpactEntry.objects.create(notion_id="e9", description="No source", publish=True)
    client = FakeClient()

    result = search.reindex(client=client)

    assert result["indexed"] == 1
    assert result["withheld"] == 1


def test_nothing_withheld_when_every_record_has_a_link(entry):  # noqa: ARG001
    assert search.reindex(client=FakeClient())["withheld"] == 0


def test_a_record_that_loses_its_link_leaves_the_index(entry):
    client = FakeClient(documents=[{"id": entry.pk}])
    entry.source_url = ""
    entry.save()

    result = search.reindex(client=client)

    assert client.index(search.INDEX_NAME).deleted == [[entry.pk]]
    assert result["indexed"] == 0
