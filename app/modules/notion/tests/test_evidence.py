# 3rd party
import pytest
from django.http import QueryDict

# Module
from modules.notion import evidence


def params(querystring: str) -> QueryDict:
    return QueryDict(querystring)


####################################################################################################
# Keyword
####################################################################################################


def test_the_keyword_is_read():
    assert evidence.parse(params("q=procurement")).terms == "procurement"


def test_a_missing_keyword_is_empty():
    assert evidence.parse(params("")).terms == ""


def test_the_keyword_is_stripped():
    assert evidence.parse(params("q=%20%20tax%20%20")).terms == "tax"


def test_an_overlong_keyword_is_cut():
    long_term = "x" * (evidence.MAX_TERMS + 500)

    assert len(evidence.parse(params(f"q={long_term}")).terms) == evidence.MAX_TERMS


####################################################################################################
# Facet values
####################################################################################################


def test_a_facet_value_is_read():
    assert evidence.parse(params("topic=Tax")).selected["topic"] == ("Tax",)


def test_several_values_for_one_facet():
    query = evidence.parse(params("topic=Tax&topic=Corruption"))

    assert query.selected["topic"] == ("Tax", "Corruption")


def test_repeated_values_are_deduped():
    assert evidence.parse(params("topic=Tax&topic=Tax")).selected["topic"] == ("Tax",)


def test_an_unknown_parameter_is_ignored():
    query = evidence.parse(params("lessons=anything&colour=red"))

    assert query.is_filtered is False
    assert "lessons" not in query.selected


def test_usability_themes_cannot_be_reached_from_a_url():
    """It is filterable in the index but is not one of the six OO asked for."""
    query = evidence.parse(params("usability_themes=Bulk%20data&usability=Bulk%20data"))

    assert query.is_filtered is False


def test_an_empty_value_is_dropped():
    assert evidence.parse(params("topic=&topic=Tax")).selected["topic"] == ("Tax",)


def test_too_many_values_are_capped():
    many = "&".join(f"topic=value{n}" for n in range(evidence.MAX_VALUES_PER_FACET + 20))

    values = evidence.parse(params(many)).selected["topic"]

    assert len(values) == evidence.MAX_VALUES_PER_FACET


def test_an_unknown_facet_value_is_kept_rather_than_rejected():
    """It quotes and escapes safely, and simply matches nothing."""
    query = evidence.parse(params("topic=Not%20A%20Real%20Topic"))

    assert query.selected["topic"] == ("Not A Real Topic",)


####################################################################################################
# Year coercion
####################################################################################################


def test_a_year_becomes_a_number():
    """The index stores year as a number, so a string would never match."""
    assert evidence.parse(params("year=2024")).selected["year"] == (2024,)


def test_a_nonsense_year_is_dropped_without_error():
    query = evidence.parse(params("year=banana&year=2024"))

    assert query.selected["year"] == (2024,)


def test_an_implausible_year_is_dropped():
    assert evidence.parse(params("year=99")).selected["year"] == ()
    assert evidence.parse(params("year=999999")).selected["year"] == ()


####################################################################################################
# Sort
####################################################################################################


def test_the_default_sort_is_newest():
    assert evidence.parse(params("")).sort is evidence.DEFAULT_SORT
    assert evidence.DEFAULT_SORT.key == "newest"


def test_a_named_sort_is_used():
    assert evidence.parse(params("sort=oldest")).sort.key == "oldest"


def test_an_unknown_sort_falls_back_to_the_default():
    assert evidence.parse(params("sort=sideways")).sort is evidence.DEFAULT_SORT


def test_the_two_sorts_oo_asked_for():
    """Both are by date. Open Ownership asked for the title orders to come out."""
    assert [option.key for option in evidence.SORT_OPTIONS] == ["newest", "oldest"]


def test_an_old_title_sort_link_still_works():
    """`?sort=az` was a real URL for a while, so it lands on the default rather
    than on an error.
    """
    assert evidence.parse(params("sort=az")).sort is evidence.DEFAULT_SORT


def test_every_sort_option_only_uses_sortable_attributes():
    # 3rd party
    from modules.notion import search

    for option in evidence.SORT_OPTIONS:
        for term in option.terms:
            assert term.split(":")[0] in search.SORTABLE_ATTRIBUTES


def test_the_orm_order_matches_the_index_terms():
    """One definition of each order, so the degraded path cannot drift."""
    for option in evidence.SORT_OPTIONS:
        assert len(option.orm_order()) == len(option.terms)


####################################################################################################
# Page number
####################################################################################################


def test_the_default_page_is_one():
    assert evidence.parse(params("")).page == 1


def test_a_page_number_is_read():
    assert evidence.parse(params("page=3")).page == 3


def test_a_nonsense_page_falls_back_to_one():
    assert evidence.parse(params("page=banana")).page == 1


def test_a_negative_page_falls_back_to_one():
    assert evidence.parse(params("page=-4")).page == 1


####################################################################################################
# Turning a query into filters
####################################################################################################


def test_filters_map_public_names_to_index_attributes():
    query = evidence.parse(params("topic=Tax&jurisdiction=Kenya&resource=Journalism"))

    assert query.filters() == {
        "policy_areas": ["Tax"],
        "jurisdictions": ["Kenya"],
        "resource_types": ["Journalism"],
    }


def test_a_parameter_outside_the_facets_is_ignored():
    """`data_users` is filterable in the index, so the allowlist is what keeps a
    hand-written `?type=` out of the query.
    """
    assert evidence.parse(params("type=CSO%2FNGO")).filters() == {}


def test_an_unused_facet_is_left_out_of_the_filters():
    assert evidence.parse(params("topic=Tax")).filters() == {"policy_areas": ["Tax"]}


def test_no_filters_at_all():
    assert evidence.parse(params("q=tax")).filters() == {}


def test_filters_excluding_drops_exactly_one_facet():
    query = evidence.parse(params("topic=Tax&region=Africa&year=2024"))

    assert query.filters_excluding("topic") == {"regions": ["Africa"], "year": [2024]}
    assert query.filters_excluding("region") == {"policy_areas": ["Tax"], "year": [2024]}


def test_is_filtered_ignores_the_keyword():
    assert evidence.parse(params("q=tax")).is_filtered is False
    assert evidence.parse(params("topic=Tax")).is_filtered is True


####################################################################################################
# Building URLs
####################################################################################################


def test_the_querystring_round_trips():
    query = evidence.parse(params("q=tax&topic=Tax&region=Africa&sort=oldest"))

    assert evidence.parse(params(query.querystring())) == query


def test_the_querystring_leaves_out_the_page():
    """The pagination partial appends its own page number."""
    query = evidence.parse(params("topic=Tax&page=4"))

    assert "page" not in query.querystring()
    assert "topic=Tax" in query.querystring()


def test_the_default_sort_is_not_written_into_the_url():
    assert "sort" not in evidence.parse(params("topic=Tax")).querystring()


def test_a_chosen_sort_is_written_into_the_url():
    assert "sort=oldest" in evidence.parse(params("sort=oldest")).querystring()


def test_without_terms_drops_the_keyword_and_keeps_everything_else():
    query = evidence.parse(params("q=tax&topic=Tax&sort=oldest"))

    remaining = evidence.parse(params(query.without_terms()))

    assert remaining.terms == ""
    assert remaining.selected["topic"] == ("Tax",)
    assert remaining.sort.key == "oldest"


def test_without_terms_sends_the_reader_back_to_page_one():
    query = evidence.parse(params("q=tax&page=4"))

    assert "page" not in query.without_terms()


def test_the_querystring_is_empty_for_a_bare_page():
    assert evidence.parse(params("")).querystring() == ""


def test_without_removes_one_value_and_keeps_its_siblings():
    query = evidence.parse(params("topic=Tax&topic=Corruption&region=Africa"))

    remaining = evidence.parse(params(query.without("topic", "Tax")))

    assert remaining.selected["topic"] == ("Corruption",)
    assert remaining.selected["region"] == ("Africa",)


def test_without_removes_the_last_value_of_a_facet():
    query = evidence.parse(params("topic=Tax&region=Africa"))

    remaining = evidence.parse(params(query.without("topic", "Tax")))

    assert remaining.selected["topic"] == ()
    assert remaining.selected["region"] == ("Africa",)


def test_without_sends_the_reader_back_to_page_one():
    query = evidence.parse(params("topic=Tax&topic=Corruption&page=5"))

    assert "page" not in query.without("topic", "Tax")


def test_toggled_adds_a_value_that_was_not_chosen():
    query = evidence.parse(params("topic=Tax"))

    remaining = evidence.parse(params(query.toggled("topic", "Corruption")))

    assert remaining.selected["topic"] == ("Tax", "Corruption")


def test_toggled_removes_a_value_that_was_already_chosen():
    """So a tag on a card can be clicked twice to undo itself."""
    query = evidence.parse(params("topic=Tax&topic=Corruption"))

    remaining = evidence.parse(params(query.toggled("topic", "Tax")))

    assert remaining.selected["topic"] == ("Corruption",)


def test_toggled_keeps_the_keyword_the_sort_and_the_other_facets():
    query = evidence.parse(params("q=tax&region=Africa&sort=oldest&topic=Tax"))

    remaining = evidence.parse(params(query.toggled("topic", "Corruption")))

    assert remaining.terms == "tax"
    assert remaining.sort.key == "oldest"
    assert remaining.selected["region"] == ("Africa",)


def test_toggled_sends_the_reader_back_to_page_one():
    query = evidence.parse(params("topic=Tax&page=3"))

    assert "page" not in query.toggled("topic", "Corruption")


def test_toggled_handles_a_year_given_as_text():
    """A template hands over text, while a selected year is an int."""
    query = evidence.parse(params("year=2024"))

    remaining = evidence.parse(params(query.toggled("year", "2024")))

    assert remaining.selected["year"] == ()


def test_facet_query_starts_from_nothing_when_there_is_no_query():
    """A record's own page has no listing state behind it, so the values on it
    link to a listing filtered by that value and nothing else.
    """
    assert evidence.facet_query(None, "topic", "Tax") == "topic=Tax"


def test_facet_query_toggles_against_a_query():
    query = evidence.parse(params("topic=Tax&region=Africa"))

    assert evidence.facet_query(query, "topic", "Tax") == "region=Africa"


def test_facet_query_works_for_every_facet():
    query = evidence.parse(params("jurisdiction=Kenya"))

    assert evidence.facet_query(query, "region", "Africa") == "jurisdiction=Kenya&region=Africa"


def test_without_handles_a_year():
    query = evidence.parse(params("year=2024&year=2019"))

    remaining = evidence.parse(params(query.without("year", 2024)))

    assert remaining.selected["year"] == (2019,)


def test_without_handles_a_year_given_as_text():
    """What a template passes. `FacetValue.value` is always a string, while a
    selected year is an int, so the two have to be brought together here or the
    chip silently removes nothing.
    """
    query = evidence.parse(params("year=2024&year=2019"))

    remaining = evidence.parse(params(query.without("year", "2024")))

    assert remaining.selected["year"] == (2019,)


####################################################################################################
# The facets themselves
####################################################################################################


def test_the_five_facets_oo_asked_for():
    """`data_users` ("Type") stays filterable in the index but is not offered:
    Open Ownership only wanted the resource type.
    """
    assert [facet.param for facet in evidence.FACETS] == [
        "year",
        "jurisdiction",
        "region",
        "topic",
        "resource",
    ]


def test_every_facet_points_at_a_filterable_attribute():
    # 3rd party
    from modules.notion import search

    for facet in evidence.FACETS:
        assert facet.attribute in search.FILTERABLE_ATTRIBUTES


def test_jurisdictions_are_listed_alphabetically():
    """The reader looks a country up by name, so the count is not the order."""
    assert evidence.FACETS_BY_PARAM["jurisdiction"].order == evidence.ORDER_ALPHA


def test_only_jurisdiction_collapses():
    """48 values, against 16 or fewer everywhere else."""
    collapsing = [f.param for f in evidence.FACETS if f.collapse_after is not None]

    assert collapsing == ["jurisdiction"]


####################################################################################################
# Facet groups
####################################################################################################


def group(values, collapse_after=None, selected=()):
    return evidence.FacetGroup(
        param="topic",
        label="Topic",
        values=tuple(
            evidence.FacetValue(value=name, label=name, count=count, selected=name in selected)
            for name, count in values
        ),
        collapse_after=collapse_after,
    )


def test_an_uncollapsed_group_shows_everything():
    built = group([("Tax", 3), ("Corruption", 2)])

    assert len(built.visible) == 2
    assert built.hidden == ()


def test_a_collapsed_group_hides_the_tail():
    built = group([(f"v{n}", 1) for n in range(10)], collapse_after=4)

    assert len(built.visible) == 4
    assert len(built.hidden) == 6


def test_a_selected_value_is_never_hidden():
    """Otherwise the reader cannot untick it."""
    built = group([(f"v{n}", 1) for n in range(10)], collapse_after=4, selected={"v8"})

    assert "v8" in [item.value for item in built.visible]
    assert "v8" not in [item.value for item in built.hidden]


def test_a_group_counts_its_selections():
    built = group([("Tax", 3), ("Corruption", 2)], selected={"Tax"})

    assert built.selected_count == 1


####################################################################################################
# Running a query end to end
####################################################################################################


@pytest.fixture
def corpus():
    """A handful of real entries, plus a fake index built from them."""
    # Module
    from modules.notion import search
    from modules.notion.models import (
        CountryTag,
        DataUserTag,
        ImpactEntry,
        PolicyAreaTag,
        ResourceTypeTag,
    )
    from modules.notion.tests.fakes import FakeClient

    kenya = CountryTag.objects.create(
        notion_id="c-ke", name="Kenya", slug="kenya", notion_region="Africa",
    )
    uk = CountryTag.objects.create(
        notion_id="c-uk",
        name="United Kingdom",
        slug="uk",
        notion_region="Europe and Central Asia",
    )

    def add(notion_id, description, year, country, topics, users=("CSO/NGO",)):
        entry = ImpactEntry.objects.create(
            notion_id=notion_id,
            description=description,
            summary=f"Summary of {description}",
            source_url=f"https://example.com/{notion_id}",
            year=year,
            publish=True,
        )
        entry.countries.add(country)
        for name in topics:
            entry.policy_areas.add(PolicyAreaTag.objects.get_or_create(name=name)[0])
        for name in users:
            entry.data_users.add(DataUserTag.objects.get_or_create(name=name)[0])
        entry.resource_types.add(ResourceTypeTag.objects.get_or_create(name="Journalism")[0])
        return entry

    add("tax-ke", "Kenyan tax investigation", 2024, kenya, ["Tax"])
    add("corr-uk", "UK corruption case", 2023, uk, ["Corruption"])
    add("both-uk", "UK procurement and tax review", 2022, uk, ["Tax", "Public procurement"])
    add("aml-ke", "Kenyan AML enforcement", 2021, kenya, ["AML/CFT"], users=("Government: FIU",))

    return FakeClient(documents=search.documents())


def run(querystring, corpus, per_page=12):
    return evidence.results(params(querystring), per_page=per_page, client=corpus)


def ids_of(found):
    return [entry.notion_id for entry in found.page_obj.object_list]


def counts_for(found, param):
    group = next(g for g in found.facets if g.param == param)
    return {item.value: item.count for item in group.values}


def test_an_unfiltered_query_returns_everything_newest_first(corpus):
    found = run("", corpus)

    assert found.total == 4
    assert ids_of(found) == ["tax-ke", "corr-uk", "both-uk", "aml-ke"]
    assert found.degraded is False


def test_filtering_by_topic_narrows_the_results(corpus):
    found = run("topic=Tax", corpus)

    assert sorted(ids_of(found)) == ["both-uk", "tax-ke"]


def test_two_values_in_one_facet_are_a_union_not_an_intersection(corpus):
    found = run("topic=Tax&topic=Corruption", corpus)

    assert sorted(ids_of(found)) == ["both-uk", "corr-uk", "tax-ke"]


def test_two_facets_are_combined_with_and(corpus):
    found = run("topic=Tax&region=Africa", corpus)

    assert ids_of(found) == ["tax-ke"]


def test_a_keyword_narrows_the_results(corpus):
    found = run("q=procurement", corpus)

    assert ids_of(found) == ["both-uk"]


def test_a_keyword_and_a_filter_combine(corpus):
    assert ids_of(run("q=Kenyan&topic=Tax", corpus)) == ["tax-ke"]
    assert ids_of(run("topic=Tax&q=Kenyan", corpus)) == ["tax-ke"]


def test_sorting_oldest_first_reverses_the_years(corpus):
    assert ids_of(run("sort=oldest", corpus)) == ["aml-ke", "both-uk", "corr-uk", "tax-ke"]


def test_a_filter_matching_nothing_gives_an_empty_page_not_an_error(corpus):
    found = run("topic=Nothing%20Like%20This", corpus)

    assert found.total == 0
    assert found.page_obj.object_list == []
    assert found.facets


####################################################################################################
# Facet counts
####################################################################################################


def test_counts_reflect_the_filtered_results(corpus):
    """A facet the reader has not touched counts against what they can see."""
    found = run("region=Africa", corpus)

    assert counts_for(found, "topic") == {"Tax": 1, "AML/CFT": 1}


def test_a_ticked_facet_still_offers_its_other_values(corpus):
    """The one that matters. Without recounting, ticking Tax would hide
    Corruption and a second topic could never be chosen.
    """
    found = run("topic=Tax", corpus)

    topics = counts_for(found, "topic")
    assert "Corruption" in topics
    assert topics["Corruption"] == 1
    assert topics["Tax"] == 2


def test_a_ticked_facet_is_still_narrowed_by_the_other_facets(corpus):
    """Recounting drops that facet's own filter, not everybody else's."""
    found = run("topic=Tax&region=Africa", corpus)

    assert counts_for(found, "topic") == {"Tax": 1, "AML/CFT": 1}


def test_other_facets_are_still_narrowed_by_the_ticked_one(corpus):
    found = run("topic=Tax", corpus)

    assert counts_for(found, "region") == {"Africa": 1, "Europe and Central Asia": 1}


def test_a_ticked_value_is_marked_selected(corpus):
    found = run("topic=Tax", corpus)

    group = next(g for g in found.facets if g.param == "topic")
    assert [item.value for item in group.values if item.selected] == ["Tax"]


def test_years_are_offered_newest_first(corpus):
    group = next(g for g in run("", corpus).facets if g.param == "year")

    assert [item.value for item in group.values] == ["2024", "2023", "2022", "2021"]


def test_a_selected_year_survives_the_round_trip(corpus):
    found = run("year=2024", corpus)

    group = next(g for g in found.facets if g.param == "year")
    assert [item.value for item in group.values if item.selected] == ["2024"]
    assert ids_of(found) == ["tax-ke"]


####################################################################################################
# Pagination
####################################################################################################


def test_results_are_paginated(corpus):
    found = run("", corpus, per_page=2)

    assert len(found.page_obj.object_list) == 2
    assert found.page_obj.paginator.num_pages == 2
    assert found.total == 4


def test_the_second_page_holds_the_rest(corpus):
    found = run("page=2", corpus, per_page=2)

    assert ids_of(found) == ["both-uk", "aml-ke"]


def test_a_page_past_the_end_falls_back_to_the_last(corpus):
    assert run("page=99", corpus, per_page=2).page_obj.number == 2


def test_only_the_current_page_is_fetched_from_the_database(corpus):
    found = run("", corpus, per_page=2)

    assert len(found.page_obj.object_list) == 2


def test_a_record_the_index_still_holds_but_the_database_does_not_is_skipped(corpus):
    """The index can be ahead of the database between syncs."""
    # Module
    from modules.notion.models import ImpactEntry

    ImpactEntry.objects.filter(notion_id="tax-ke").delete()

    found = run("", corpus)

    assert "tax-ke" not in ids_of(found)
    assert len(found.page_obj.object_list) == 3


####################################################################################################
# When search is unavailable
####################################################################################################


def test_a_search_failure_falls_back_to_the_database(corpus, monkeypatch):  # noqa: ARG001
    def boom(*args, **kwargs):
        msg = "connection refused"
        raise ConnectionError(msg)

    monkeypatch.setattr(evidence.search, "search", boom)

    found = evidence.results(params(""))

    assert found.degraded is True
    assert found.total == 4
    assert found.facets == ()


def test_the_fallback_keeps_the_sort_order(monkeypatch, corpus):  # noqa: ARG001
    def boom(*args, **kwargs):
        msg = "connection refused"
        raise ConnectionError(msg)

    monkeypatch.setattr(evidence.search, "search", boom)

    assert ids_of(evidence.results(params("sort=oldest"))) == [
        "aml-ke",
        "both-uk",
        "corr-uk",
        "tax-ke",
    ]


def test_the_fallback_orders_the_same_way_the_index_would(corpus):
    """Both paths must agree, or the page reshuffles during an outage."""
    indexed = ids_of(run("", corpus))
    from_database = [
        entry.notion_id for entry in evidence.fallback_queryset(evidence.DEFAULT_SORT)
    ]

    assert indexed == from_database


def test_with_no_meilisearch_configured_at_all_the_page_still_works():
    """The test settings carry no Meilisearch host, so this is the real path."""
    found = evidence.results(params(""))

    assert found.degraded is True


####################################################################################################
# The whole result set, for export
####################################################################################################


def test_every_record_comes_back_unpaginated(corpus):
    """An export covers the whole result set, not the page the reader is on."""
    records = evidence.all_records(params("page=2"), client=corpus)

    assert len(records) == 4


def test_the_whole_result_set_respects_the_filters(corpus):
    records = evidence.all_records(params("topic=Tax"), client=corpus)

    assert [entry.notion_id for entry in records] == ["tax-ke", "both-uk"]


def test_the_whole_result_set_respects_a_keyword(corpus):
    records = evidence.all_records(params("q=corruption"), client=corpus)

    assert [entry.notion_id for entry in records] == ["corr-uk"]


def test_the_whole_result_set_respects_the_sort_order(corpus):
    records = evidence.all_records(params("sort=oldest"), client=corpus)

    assert [entry.notion_id for entry in records] == [
        "aml-ke",
        "both-uk",
        "corr-uk",
        "tax-ke",
    ]


def test_the_whole_result_set_matches_what_the_listing_shows(corpus):
    """The export and the listing have to agree, or a reader downloads
    something other than what they were looking at.
    """
    listed = ids_of(run("topic=Tax", corpus))
    exported = [
        entry.notion_id for entry in evidence.all_records(params("topic=Tax"), client=corpus)
    ]

    assert exported == listed


def test_the_whole_result_set_falls_back_to_the_database(monkeypatch, corpus):  # noqa: ARG001
    """With search down there are no filters to apply, so this is everything."""

    def boom(*args, **kwargs):
        msg = "connection refused"
        raise ConnectionError(msg)

    monkeypatch.setattr(evidence.search, "search", boom)

    records = evidence.all_records(params("topic=Tax"))

    assert len(records) == 4


####################################################################################################
# Telling an empty listing from an empty result set
####################################################################################################


def test_a_bare_listing_restricts_nothing():
    assert evidence.parse(params("")).is_restricted is False


def test_a_keyword_restricts_the_results():
    assert evidence.parse(params("q=tax")).is_restricted is True


def test_a_facet_restricts_the_results():
    assert evidence.parse(params("topic=Tax")).is_restricted is True


def test_sorting_alone_does_not_restrict_the_results():
    """`is_narrowed` counts a sort, because a sorted view should not be cached
    or indexed. Nothing is hidden by it, so an empty listing under a sort is
    still an empty listing rather than a search that found nothing.
    """
    query = evidence.parse(params("sort=oldest"))

    assert query.is_narrowed is True
    assert query.is_restricted is False


def test_paging_alone_does_not_restrict_the_results():
    assert evidence.parse(params("page=3")).is_restricted is False
