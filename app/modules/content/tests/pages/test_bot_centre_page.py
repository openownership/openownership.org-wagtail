# stdlib
import datetime as dt
import html
import re

# 3rd party
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


def test_a_worldwide_card_names_its_jurisdiction_as_global(bot_centre):
    """The tracker gives these records the "Global" row rather than a country,
    so a shut card would otherwise show no jurisdiction at all.
    """
    entry = make_entry("e1", "A worldwide case")
    entry.worldwide = True
    entry.save()

    rendered = client.get(bot_centre.url).rendered_content

    assert '<span class="evidence-card__jurisdictions">Global</span>' in rendered


def test_a_worldwide_card_does_not_say_global_twice(bot_centre):
    """The shut card labels neither the jurisdiction nor the region, so the same
    word in both places reads as a mistake.
    """
    entry = make_entry("e1", "A worldwide case")
    entry.worldwide = True
    entry.save()

    rendered = client.get(bot_centre.url).rendered_content

    facts = re.search(r"evidence-card__facts.*?</p>", rendered, re.S).group(0)
    assert facts.count("Global") == 1


def test_a_shut_card_does_not_offer_the_source(bot_centre):
    """Open Ownership asked for the link to the source to wait until a reader
    has opened the record, so a card carries one control rather than two.
    """
    make_entry("e1", "A record", link="https://example.com/story")

    rendered = client.get(bot_centre.url).rendered_content

    assert "View source" not in rendered
    assert "https://example.com/story" not in rendered


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
# When the tracker last changed
####################################################################################################


def test_the_page_says_when_the_tracker_last_changed(bot_centre):
    entry = make_entry("e1", "A record")
    ImpactEntry.objects.filter(pk=entry.pk).update(
        notion_updated=dt.datetime(2026, 3, 9, tzinfo=dt.timezone.utc),
    )

    rendered = client.get(bot_centre.url).rendered_content

    assert "The BOT Evidence Centre is updated on an ongoing basis" in rendered
    assert "09 March 2026" in rendered


def test_the_date_is_machine_readable(bot_centre):
    """A date a reader can read is not a date anything else can."""
    entry = make_entry("e1", "A record")
    ImpactEntry.objects.filter(pk=entry.pk).update(
        notion_updated=dt.datetime(2026, 3, 9, tzinfo=dt.timezone.utc),
    )

    rendered = client.get(bot_centre.url).rendered_content

    assert '<time datetime="2026-03-09"' in rendered


def test_nothing_is_claimed_before_the_first_sync(bot_centre):
    """No records, so no date, so no sentence about how current it is."""
    rendered = client.get(bot_centre.url).rendered_content

    assert "updated on an ongoing basis" not in rendered


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
    rendered = client.get(f"{stocked.url}?sort=oldest").rendered_content

    assert 'value="oldest" selected' in rendered or 'selected value="oldest"' in rendered


def test_the_sort_control_offers_the_two_date_orders_only(stocked):
    """Open Ownership asked for the title orders to come out. The default sorts
    with an empty value, so it is the label that shows it is still offered.
    """
    rendered = client.get(stocked.url).rendered_content

    assert "Newest first" in rendered
    assert 'value="oldest"' in rendered
    assert 'value="az"' not in rendered
    assert 'value="za"' not in rendered


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
# Topic tags as filters
####################################################################################################


def topic_hrefs(rendered):
    """Where a record's topic tags point, unescaped as a browser would read them."""
    return [
        html.unescape(href)
        for href in re.findall(r'<a class="topic-tag"[^>]*href="([^"]+)"', rendered)
    ]


def test_a_topic_tag_links_to_the_listing_filtered_by_it(stocked):
    rendered = client.get(stocked.url).rendered_content

    assert f"{stocked.url}?topic=Tax" in topic_hrefs(rendered)


def test_a_topic_tag_keeps_the_filters_the_reader_already_set(stocked):
    """Clicking a tag narrows what the reader is looking at. It does not throw
    away the filters they got there with.
    """
    rendered = client.get(f"{stocked.url}?resource=Journalism").rendered_content

    assert f"{stocked.url}?topic=Tax&resource=Journalism" in topic_hrefs(rendered)


def test_a_chosen_topics_tag_links_to_removing_it(stocked):
    """The same click twice undoes itself, as unticking the box would."""
    rendered = client.get(f"{stocked.url}?topic=Tax").rendered_content

    assert topic_hrefs(rendered) == [f"{stocked.url}?"]


def test_a_topic_tag_says_what_it_does(stocked):
    """The link text is otherwise just the topic's name, which reads as a label
    rather than as something that will change the page.
    """
    rendered = client.get(stocked.url).rendered_content

    assert "Show records tagged" in rendered


def test_topic_tags_are_not_followed_by_crawlers(stocked):
    """Filtered views are `noindex` already. This keeps a crawler out of the
    combinations rather than relying on it reading that afterwards.
    """
    rendered = client.get(stocked.url).rendered_content

    assert 'rel="nofollow"' in rendered


def facet_hrefs(rendered, css_class):
    return [
        html.unescape(href)
        for href in re.findall(rf'<a class="{css_class}"[^>]*href="([^"]+)"', rendered)
    ]


def test_a_jurisdiction_links_to_the_listing_filtered_by_it(bot_centre):
    entry = make_entry("e1", "A Kenyan case")
    entry.countries.add(
        CountryTag.objects.create(
            notion_id="c-ke", name="Kenya", slug="kenya", notion_region="Africa",
        ),
    )

    rendered = client.get(bot_centre.url).rendered_content

    assert f"{bot_centre.url}?jurisdiction=Kenya" in facet_hrefs(rendered, "jurisdiction-tag")


def test_two_jurisdictions_are_separated_by_a_comma_and_nothing_else(bot_centre):
    """Each name is its own link now, so the markup between them decides whether
    a reader sees "Kenya, Nigeria" or "Kenya , Nigeria".
    """
    entry = make_entry("e1", "A case in two countries")
    for notion_id, name in (("c-ke", "Kenya"), ("c-ng", "Nigeria")):
        entry.countries.add(
            CountryTag.objects.create(
                notion_id=notion_id, name=name, slug=name.lower(), notion_region="Africa",
            ),
        )

    rendered = client.get(bot_centre.url).rendered_content

    assert "Kenya</a>, <a" in re.sub(r"\s+", " ", rendered)


def test_a_region_links_to_the_listing_filtered_by_it(bot_centre):
    with_region("e1", "A European case", "Somewhere", ["Europe and Central Asia"])

    rendered = client.get(bot_centre.url).rendered_content

    assert (
        f"{bot_centre.url}?region=Europe+and+Central+Asia"
        in facet_hrefs(rendered, "region-tag")
    )


def test_a_year_links_to_the_listing_filtered_by_it(bot_centre):
    make_entry("e1", "A record", year=2019)

    rendered = client.get(bot_centre.url).rendered_content

    assert f"{bot_centre.url}?year=2019" in facet_hrefs(rendered, "year-tag")


def test_a_chosen_years_link_takes_it_off_again(bot_centre):
    make_entry("e1", "A record", year=2019)

    rendered = client.get(f"{bot_centre.url}?year=2019").rendered_content

    assert facet_hrefs(rendered, "year-tag") == [f"{bot_centre.url}?"]


def test_a_worldwide_records_jurisdiction_is_not_a_link(bot_centre):
    """"Global" is what the tracker calls these records, not a jurisdiction
    anyone can filter by, so there is nowhere for it to go.
    """
    entry = make_entry("e1", "A worldwide case")
    entry.worldwide = True
    entry.save()

    rendered = client.get(bot_centre.url).rendered_content

    assert '<span class="evidence-card__jurisdictions">Global</span>' in rendered


def test_opening_a_record_carries_the_readers_filters(stocked):
    """The open card is rendered by another view, so without this its own topic
    tags would come back knowing nothing about what the reader had chosen.
    """
    rendered = client.get(f"{stocked.url}?resource=Journalism").rendered_content

    assert 'hx-get="/en/evidence/tax/?resource=Journalism"' in rendered


def test_the_record_link_itself_stays_clean(stocked):
    """`href` and `hx-push-url` are what a reader shares or bookmarks, so the
    filters that happened to be set are left out of both.
    """
    rendered = client.get(f"{stocked.url}?resource=Journalism").rendered_content

    assert 'href="/en/evidence/tax/"' in rendered
    assert 'hx-push-url="true"' in rendered


####################################################################################################
# The edge of a card
####################################################################################################


def with_region(notion_id, description, country_name, region_names):
    entry = make_entry(notion_id, description)
    for region_name in region_names:
        country = CountryTag.objects.get_or_create(
            notion_id=f"c-{region_name}",
            defaults={
                "name": f"{country_name} {region_name}",
                "slug": f"c-{region_name}".lower(),
                "notion_region": region_name,
            },
        )[0]
        entry.countries.add(country)
    return entry


def test_every_card_carries_the_same_edge(bot_centre):
    """One colour for every record. Open Ownership found a colour per region
    more confusing than useful, so the edge no longer says anything.
    """
    with_region("e1", "A European case", "Somewhere", ["Europe and Central Asia"])
    make_entry("e2", "A record with no region at all")

    rendered = client.get(bot_centre.url).rendered_content

    assert rendered.count("evidence-card__edge") == 2


def test_the_edge_colour_comes_from_the_stylesheet(bot_centre):
    """It is the same on every card, so there is nothing for a template to say
    about it and no inline style to say it with.
    """
    with_region("e1", "A European case", "Somewhere", ["Europe and Central Asia"])

    rendered = client.get(bot_centre.url).rendered_content

    assert "evidence-card__edge" in rendered
    assert 'class="evidence-card__edge" style' not in rendered


def test_a_region_is_named_without_a_colour_beside_it(bot_centre):
    with_region("e1", "A European case", "Somewhere", ["Europe and Central Asia"])

    rendered = client.get(bot_centre.url).rendered_content

    assert "Europe and Central Asia" in rendered
    assert "region-tag__dot" not in rendered


def test_no_region_colour_is_left_anywhere_on_the_page(bot_centre):
    """The old palette was set inline, so a leftover would show up as a hex."""
    with_region("e1", "A European case", "Somewhere", ["Europe and Central Asia"])
    with_region("e2", "An African case", "Somewhere", ["Africa"])

    rendered = client.get(bot_centre.url).rendered_content

    assert "#DB00C9" not in rendered
    assert "linear-gradient" not in rendered


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
