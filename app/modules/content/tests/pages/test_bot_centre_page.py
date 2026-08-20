import pytest
from django.template.loader import render_to_string
from django.test import Client

from modules.content.models.pages import BotCentrePage
from modules.notion import search
from modules.notion.models import (
    CountryTag,
    DataUserTag,
    ImpactEntry,
    PolicyAreaTag,
    Region,
    ResourceTypeTag,
)
from modules.notion.tests.fakes import FakeClient

pytestmark = pytest.mark.django_db

client = Client()


####################################################################################################
# Helpers
####################################################################################################


@pytest.fixture
def bot_centre(home_page):
    page = BotCentrePage(title="Evidence Centre")
    home_page.add_child(instance=page)
    page.save_revision().publish()
    return page


def make_entry(notion_id, description, year=2024, publish=True, policy_areas=(), link=None):
    entry = ImpactEntry.objects.create(
        notion_id=notion_id,
        description=description,
        summary=f"Summary of {description}",
        year=year,
        publish=publish,
        source_url="https://example.com/source" if link is None else link,
    )
    for name in policy_areas:
        entry.policy_areas.add(PolicyAreaTag.objects.get_or_create(name=name)[0])
    return entry


####################################################################################################
# The page itself
####################################################################################################


def test_the_page_works_with_no_search_backend_configured(bot_centre):
    """The test settings carry no Meilisearch host, so every test in this file
    that does not use the `indexed` fixture exercises the degraded path.
    """
    response = client.get(bot_centre.url)

    assert response.status_code == 200
    assert response.context_data["evidence"].degraded is True


def test_entries_are_listed(bot_centre):
    make_entry("e1", "Kenyan FIU used BO data in an investigation")

    rendered = client.get(bot_centre.url).rendered_content

    assert "Kenyan FIU used BO data in an investigation" in rendered


def test_the_summary_is_shown(bot_centre):
    make_entry("e1", "Kenyan FIU used BO data")

    rendered = client.get(bot_centre.url).rendered_content

    assert "Summary of Kenyan FIU used BO data" in rendered


def test_entries_not_cleared_for_publication_are_hidden(bot_centre):
    make_entry("e1", "Cleared for publication")
    make_entry("e2", "Still internal", publish=False)

    rendered = client.get(bot_centre.url).rendered_content

    assert "Cleared for publication" in rendered
    assert "Still internal" not in rendered


def test_entries_with_no_link_are_hidden(bot_centre):
    """OO asked for records with nothing to link to be left out entirely."""
    make_entry("e1", "Has a source")
    make_entry("e2", "Nothing to link to", link="")

    rendered = client.get(bot_centre.url).rendered_content

    assert "Has a source" in rendered
    assert "Nothing to link to" not in rendered


def test_a_long_summary_is_cut_short_on_the_card(bot_centre):
    entry = make_entry("e1", "An entry")
    entry.summary = " ".join(f"word{n}" for n in range(120))
    entry.save()

    rendered = client.get(bot_centre.url).rendered_content

    assert "word10" in rendered
    assert "word119" not in rendered


def test_soft_deleted_entries_are_hidden(bot_centre):
    entry = make_entry("e1", "Gone from Notion")
    entry.deleted = True
    entry.save()

    assert "Gone from Notion" not in client.get(bot_centre.url).rendered_content


def test_the_card_shows_description_jurisdiction_topic_and_year(bot_centre):
    """The four fields OO asked for on a collapsed record."""
    entry = make_entry("e1", "An entry about something", year=2019, policy_areas=["Tax"])
    entry.countries.add(CountryTag.objects.create(notion_id="c1", name="Kenya", slug="kenya"))

    rendered = client.get(bot_centre.url).rendered_content

    assert "An entry about something" in rendered
    assert "Kenya" in rendered
    assert "Tax" in rendered
    assert "2019" in rendered


def test_the_card_holds_back_the_rest_until_expansion(bot_centre):
    entry = make_entry("e1", "An entry", year=2019)
    entry.resource_types.add(ResourceTypeTag.objects.create(name="Public sector"))

    assert "Public sector" not in client.get(bot_centre.url).rendered_content


####################################################################################################
# Ordering
####################################################################################################


def test_newest_year_comes_first(bot_centre):
    make_entry("old", "An older entry", year=2019)
    make_entry("new", "A newer entry", year=2026)

    entries = client.get(bot_centre.url).context_data["page_obj"].object_list

    assert [e.notion_id for e in entries] == ["new", "old"]


def test_within_a_year_entries_are_ordered_by_topic(bot_centre):
    make_entry("tax", "Second by topic", year=2024, policy_areas=["Tax"])
    make_entry("aml", "First by topic", year=2024, policy_areas=["AML/CFT"])

    entries = client.get(bot_centre.url).context_data["page_obj"].object_list

    assert [e.notion_id for e in entries] == ["aml", "tax"]


def test_entries_without_a_topic_come_last(bot_centre):
    make_entry("none", "No topic at all", year=2024)
    make_entry("tax", "Has a topic", year=2024, policy_areas=["Tax"])

    entries = client.get(bot_centre.url).context_data["page_obj"].object_list

    assert [e.notion_id for e in entries] == ["tax", "none"]


def test_entries_without_a_year_come_last(bot_centre):
    make_entry("dated", "Has a year", year=2019)
    make_entry("undated", "No year", year=None)

    entries = client.get(bot_centre.url).context_data["page_obj"].object_list

    assert [e.notion_id for e in entries] == ["dated", "undated"]


def test_the_same_year_and_topic_falls_back_to_alphabetical(bot_centre):
    make_entry("b", "Beta comes second", year=2024, policy_areas=["Tax"])
    make_entry("a", "Alpha comes first", year=2024, policy_areas=["Tax"])

    entries = client.get(bot_centre.url).context_data["page_obj"].object_list

    assert [e.notion_id for e in entries] == ["a", "b"]


def test_an_entry_with_several_topics_is_not_repeated(bot_centre):
    make_entry("e1", "Several topics", year=2024, policy_areas=["Tax", "Corruption"])

    entries = client.get(bot_centre.url).context_data["page_obj"].object_list

    assert [e.notion_id for e in entries] == ["e1"]


####################################################################################################
# Pagination
####################################################################################################


def test_the_first_page_holds_one_page_worth(bot_centre):
    for index in range(BotCentrePage.objects_per_page + 5):
        make_entry(f"e{index}", f"Entry {index:03d}", year=2024)

    page_obj = client.get(bot_centre.url).context_data["page_obj"]

    assert len(page_obj.object_list) == BotCentrePage.objects_per_page
    assert page_obj.paginator.count == BotCentrePage.objects_per_page + 5


def test_the_second_page_holds_the_rest(bot_centre):
    for index in range(BotCentrePage.objects_per_page + 5):
        make_entry(f"e{index}", f"Entry {index:03d}", year=2024)

    page_obj = client.get(f"{bot_centre.url}?page=2").context_data["page_obj"]

    assert len(page_obj.object_list) == 5
    assert page_obj.number == 2


def test_pagination_links_appear_when_there_is_more_than_one_page(bot_centre):
    for index in range(BotCentrePage.objects_per_page + 1):
        make_entry(f"e{index}", f"Entry {index:03d}", year=2024)

    rendered = client.get(bot_centre.url).rendered_content

    assert "?page=2" in rendered


def test_no_pagination_when_everything_fits(bot_centre):
    make_entry("e1", "The only entry")

    assert "?page=2" not in client.get(bot_centre.url).rendered_content


def test_an_out_of_range_page_falls_back_to_the_last_one(bot_centre):
    make_entry("e1", "The only entry")

    page_obj = client.get(f"{bot_centre.url}?page=99").context_data["page_obj"]

    assert page_obj.number == 1


def test_a_nonsense_page_number_falls_back_to_the_first(bot_centre):
    make_entry("e1", "The only entry")

    page_obj = client.get(f"{bot_centre.url}?page=banana").context_data["page_obj"]

    assert page_obj.number == 1


####################################################################################################
# Empty state
####################################################################################################


def test_the_page_still_renders_with_no_entries(bot_centre):
    response = client.get(bot_centre.url)

    assert response.status_code == 200
    assert response.context_data["page_obj"].paginator.count == 0


####################################################################################################
# Filtering, searching and sorting
####################################################################################################


@pytest.fixture
def indexed(monkeypatch):
    """Point the page's search at a fake index built from the current entries."""
    monkeypatch.setattr(search, "get_client", lambda: FakeClient(documents=search.documents()))


@pytest.fixture
def stocked(bot_centre, indexed):  # noqa: ARG001
    journalism = ResourceTypeTag.objects.create(name="Journalism")
    reporter = DataUserTag.objects.create(name="Journalist/media")

    tax = make_entry("tax", "A tax investigation", year=2024, policy_areas=["Tax"])
    corr = make_entry("corr", "A corruption case", year=2023, policy_areas=["Corruption"])
    proc = make_entry(
        "proc",
        "A procurement review",
        year=2022,
        policy_areas=["Public procurement"],
    )

    for entry in (tax, corr, proc):
        entry.data_users.add(reporter)
        entry.resource_types.add(journalism)

    return bot_centre


def listed(response):
    return [entry.notion_id for entry in response.context_data["page_obj"].object_list]


def test_the_search_index_is_used_when_it_is_available(stocked):
    response = client.get(stocked.url)

    assert response.context_data["evidence"].degraded is False
    assert len(listed(response)) == 3


def test_filtering_by_topic(stocked):
    assert listed(client.get(f"{stocked.url}?topic=Tax")) == ["tax"]


def test_filtering_by_two_topics_returns_both(stocked):
    found = listed(client.get(f"{stocked.url}?topic=Tax&topic=Corruption"))

    assert sorted(found) == ["corr", "tax"]


def test_searching_by_keyword(stocked):
    assert listed(client.get(f"{stocked.url}?q=procurement")) == ["proc"]


def test_sorting_oldest_first(stocked):
    assert listed(client.get(f"{stocked.url}?sort=oldest")) == ["proc", "corr", "tax"]


def test_a_nonsense_filter_shows_the_page_rather_than_an_error(stocked):
    response = client.get(f"{stocked.url}?topic=Nonsense&year=banana&sort=sideways&page=x")

    assert response.status_code == 200
    assert listed(response) == []


####################################################################################################
# The filter controls
####################################################################################################


def test_the_facets_are_rendered_with_counts(stocked):
    rendered = client.get(stocked.url).rendered_content

    assert 'name="topic"' in rendered
    assert 'value="Tax"' in rendered
    assert 'name="year"' in rendered
    assert 'name="resource"' in rendered


def test_the_data_user_facet_is_not_offered(stocked):
    """Open Ownership asked for the resource type only."""
    rendered = client.get(stocked.url).rendered_content

    assert 'name="type"' not in rendered


def test_a_selected_filter_is_checked(stocked):
    rendered = client.get(f"{stocked.url}?topic=Tax").rendered_content

    assert 'value="Tax" checked' in rendered or 'checked value="Tax"' in rendered


def test_a_second_topic_is_still_offered_once_one_is_chosen(stocked):
    """The disjunctive facet counts, seen from the template."""
    rendered = client.get(f"{stocked.url}?topic=Tax").rendered_content

    assert 'value="Corruption"' in rendered


def test_the_sort_control_marks_the_current_option(stocked):
    rendered = client.get(f"{stocked.url}?sort=az").rendered_content

    assert 'value="az" selected' in rendered or 'selected value="az"' in rendered


def test_a_clear_link_appears_only_when_something_is_filtered(stocked):
    assert "evidence-filters__clear" not in client.get(stocked.url).rendered_content
    assert "evidence-filters__clear" in client.get(f"{stocked.url}?topic=Tax").rendered_content


def test_the_result_count_is_shown(stocked):
    assert "3 records" in client.get(stocked.url).rendered_content


def test_a_filter_matching_nothing_says_so(stocked):
    rendered = client.get(f"{stocked.url}?topic=Nonsense").rendered_content

    assert "no records" in rendered.lower()
    assert 'name="topic"' in rendered


def test_the_form_carries_no_page_field(stocked):
    """Changing a filter has to send the reader back to page one."""
    rendered = client.get(f"{stocked.url}?page=1").rendered_content

    assert 'name="page"' not in rendered


####################################################################################################
# Every control points at the listing
####################################################################################################

# Opening a record puts that record's URL in the address bar, so a relative
# `?...` link or a form with no action would aim at the record rather than the
# listing. Each of these has to name the listing itself.


def test_the_filter_form_posts_to_the_listing(stocked):
    rendered = client.get(stocked.url).rendered_content

    assert f'action="{stocked.url}"' in rendered


def test_the_clear_filters_link_points_at_the_listing(stocked):
    rendered = client.get(f"{stocked.url}?topic=Tax").rendered_content

    assert f'href="{stocked.url}?' in rendered


def test_a_facet_chip_points_at_the_listing(stocked):
    rendered = client.get(f"{stocked.url}?topic=Tax").rendered_content

    assert 'href="?' not in rendered


def test_pagination_links_point_at_the_listing(bot_centre):
    for index in range(BotCentrePage.objects_per_page + 1):
        make_entry(f"e{index}", f"Entry {index:03d}", year=2024)

    rendered = client.get(bot_centre.url).rendered_content

    assert f'href="{bot_centre.url}?page=2"' in rendered


####################################################################################################
# Crawling and caching
####################################################################################################


def test_a_filtered_view_is_not_indexed_by_search_engines(stocked):
    assert "noindex" in client.get(f"{stocked.url}?topic=Tax").rendered_content


def test_the_bare_listing_is_indexed(stocked):
    assert "noindex" not in client.get(stocked.url).rendered_content


####################################################################################################
# Degraded mode
####################################################################################################


def test_a_search_outage_still_lists_the_records(stocked, monkeypatch):
    def boom(*args, **kwargs):
        msg = "connection refused"
        raise ConnectionError(msg)

    monkeypatch.setattr(search, "search", boom)

    response = client.get(stocked.url)

    assert response.status_code == 200
    assert len(listed(response)) == 3
    assert response.context_data["evidence"].degraded is True


def test_a_search_outage_says_so_and_hides_the_controls(stocked, monkeypatch):
    def boom(*args, **kwargs):
        msg = "connection refused"
        raise ConnectionError(msg)

    monkeypatch.setattr(search, "search", boom)

    rendered = client.get(stocked.url).rendered_content

    assert "temporarily unavailable" in rendered.lower()
    assert 'name="topic"' not in rendered


####################################################################################################
# Topic icons
####################################################################################################


def test_a_card_shows_its_topic_icon(bot_centre):
    entry = make_entry("e1", "A tax case", policy_areas=["Tax"])

    rendered = client.get(bot_centre.url).rendered_content

    assert "tax-1" in rendered  # the namespaced class from tax.svg
    assert entry.policy_areas.first().name in rendered


def test_the_topic_name_is_always_shown_beside_the_icon(bot_centre):
    """The icon is decorative. A topic we have not drawn yet must still read."""
    make_entry("e1", "A record", policy_areas=["Something brand new"])

    rendered = client.get(bot_centre.url).rendered_content

    assert "Something brand new" in rendered


def test_an_unmapped_topic_falls_back_rather_than_breaking(bot_centre):
    make_entry("e1", "A record", policy_areas=["Something brand new"])

    response = client.get(bot_centre.url)

    assert response.status_code == 200


def test_two_icons_on_one_page_keep_their_own_class_names(bot_centre):
    """Every supplied file shipped with the same generic `.cls-1` names, so
    inlining two would have made them restyle each other. The site logo uses
    `.cls-1` too, so the collision was never only between icons.
    """
    make_entry("e1", "A record", policy_areas=["Tax", "Corruption"])

    rendered = client.get(bot_centre.url).rendered_content

    assert "tax-1" in rendered
    assert "corruption-1" in rendered


####################################################################################################
# Region colours
####################################################################################################


def with_region(notion_id, description, country_name, region_names):
    entry = make_entry(notion_id, description)
    for region_name in region_names:
        region = Region.objects.get_or_create(name=region_name)[0]
        country = CountryTag.objects.get_or_create(
            notion_id=f"c-{region_name}",
            defaults={"name": f"{country_name} {region_name}", "slug": f"c-{region_name}".lower()},
        )[0]
        country.regions.add(region)
        entry.countries.add(country)
    return entry


def test_a_card_carries_its_region_colour(bot_centre):
    with_region("e1", "A European case", "Somewhere", ["Europe"])

    rendered = client.get(bot_centre.url).rendered_content

    assert "#009BFE" in rendered


def test_a_two_region_card_splits_the_bar(bot_centre):
    """Fourteen published records span two regions. Showing one region's colour
    would misreport the record.
    """
    with_region("e1", "A cross-border case", "Somewhere", ["Asia", "Europe"])

    rendered = client.get(bot_centre.url).rendered_content

    assert "linear-gradient" in rendered
    assert "#7F12E0" in rendered
    assert "#009BFE" in rendered


def test_a_card_with_no_region_has_no_bar(bot_centre):
    """Six published records carry no jurisdiction at all."""
    make_entry("e1", "A worldwide case")

    rendered = client.get(bot_centre.url).rendered_content

    assert "evidence-card__region-bar" not in rendered


def test_the_region_name_is_shown_beside_its_colour(bot_centre):
    """Colour is never the only signal, which is what was promised on
    accessibility grounds when this was agreed (A-S8).
    """
    with_region("e1", "A European case", "Somewhere", ["Europe"])

    rendered = client.get(bot_centre.url).rendered_content

    assert "region-tag__dot" in rendered
    assert "Europe" in rendered


def test_the_colour_is_not_set_through_a_css_variable(bot_centre):
    """`postcss-css-variables` resolves custom properties at build time, so one
    set from a template arrives in the stylesheet as `undefined`.
    """
    with_region("e1", "A European case", "Somewhere", ["Europe"])

    rendered = client.get(bot_centre.url).rendered_content

    assert "--region-bar" not in rendered


####################################################################################################
# Keyboard and screen reader
####################################################################################################


def test_a_card_title_sits_below_the_section_heading(bot_centre):
    """The results section is headed "Evidence records", so a card inside it is
    an `h3`. As `h2` the cards were siblings of the section, which left a screen
    reader with a flat list and no structure to navigate.
    """
    make_entry("e1", "A record")

    rendered = client.get(bot_centre.url).rendered_content

    assert '<h3 class="card-group__title"' in rendered
    assert '<h2 class="card-group__title"' not in rendered


def test_a_card_title_can_take_focus(bot_centre):
    """Opening a record destroys the control that was clicked, so focus is moved
    to the heading. That needs the heading to be focusable.
    """
    make_entry("e1", "A record")

    rendered = client.get(bot_centre.url).rendered_content

    assert 'class="card-group__title" tabindex="-1"' in rendered


def test_the_record_page_keeps_its_own_heading_level(bot_centre):  # noqa: ARG001
    """A record on its own page is the page, so it stays an `h1`.

    `bot_centre` is needed even though it is not named: the detail view looks the
    listing up for its breadcrumb.
    """
    entry = make_entry("e1", "A record")

    rendered = client.get(entry.get_absolute_url()).content.decode()

    assert "<h1" in rendered


def test_the_expand_control_is_a_plain_link_in_the_markup():
    """`aria-expanded` is added by JavaScript, not here. Without JavaScript the
    control navigates to the record's page, so claiming it expands would be a
    lie. Rendered on its own because the site navigation uses `aria-expanded`
    legitimately, all over every page.
    """
    entry = make_entry("e1", "A record")

    card = render_to_string("_partials/evidence_card.jinja", {"entry": entry})

    assert "aria-expanded" not in card
    assert 'hx-push-url="true"' in card


def test_the_result_count_is_announced(bot_centre):
    """Filtering is a full page load, so the count is what tells a screen reader
    the results changed.
    """
    make_entry("e1", "A record")

    rendered = client.get(bot_centre.url).rendered_content

    assert 'class="evidence-list__count" role="status"' in rendered


####################################################################################################
# Nothing to show
####################################################################################################


def test_a_listing_with_nothing_published_says_so(bot_centre):
    """Before the first sync, or if OO untick every record. Telling a reader to
    remove a filter they never set is worse than useless.
    """
    rendered = client.get(bot_centre.url).rendered_content

    assert "no records here yet" in rendered
    assert "removing a filter" not in rendered


def test_a_search_that_matches_nothing_says_that_instead(stocked):
    rendered = client.get(f"{stocked.url}?q=zzzznothing").rendered_content

    assert "no records matching what you asked for" in rendered
    assert "no records here yet" not in rendered


def test_a_filter_that_matches_nothing_says_that_instead(stocked):
    rendered = client.get(f"{stocked.url}?topic=Nonexistent").rendered_content

    assert "no records matching what you asked for" in rendered


def test_sorting_an_empty_listing_still_reads_as_empty(bot_centre):
    """A sort hides nothing, so it is not something to suggest removing."""
    rendered = client.get(f"{bot_centre.url}?sort=az").rendered_content

    assert "no records here yet" in rendered


def test_nothing_to_download_means_no_download_link(bot_centre):
    rendered = client.get(bot_centre.url).rendered_content

    assert "evidence-list__export" not in rendered
