"""
notion.evidence

The public query layer for the BOT Evidence Centre: what a reader can filter and
sort by, what those controls are called in a URL, and how a set of GET parameters
becomes a page of results.

`search.py` stays a plain Meilisearch adapter and knows nothing about URLs or
labels. That matters here because the public vocabulary and the index vocabulary
genuinely differ: Open Ownership call `policy_areas` "Topic" and `data_users`
"Type". `FACETS` is where the two are reconciled, and it doubles as the
allowlist, so an attribute missing from it simply cannot be reached from a URL.
"""

# stdlib
from dataclasses import dataclass, field, replace
from typing import Callable, Optional
from urllib.parse import urlencode

# 3rd party
from consoler import console
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

# Module
from modules.notion import search
from modules.notion.models import ImpactEntry

PARAM_QUERY = "q"
PARAM_SORT = "sort"
PARAM_PAGE = "page"

MAX_TERMS = 200
MAX_VALUES_PER_FACET = 60

# Years outside this are a typo or a probe, not a record.
EARLIEST_YEAR = 1900
LATEST_YEAR = 2200

ORDER_ALPHA = "alpha"
ORDER_YEAR = "year"

PREFETCH = ("countries", "policy_areas", "data_users", "resource_types")


####################################################################################################
# Coercing what a reader typed
####################################################################################################


def as_year(value) -> Optional[int]:
    """A four-digit year as a number, or `None` for anything else.

    The index stores `year` as a number and the filter builder writes numbers
    unquoted, so `year IN ["2024"]` would never match.
    """
    try:
        year = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    if EARLIEST_YEAR <= year <= LATEST_YEAR:
        return year
    return None


def as_text(value) -> Optional[str]:
    """A non-empty string, or `None`."""
    return str(value).strip() or None


def as_page(value) -> int:
    """A page number of at least 1. Anything else starts at the beginning."""
    try:
        number = int(str(value).strip())
    except (TypeError, ValueError):
        return 1
    return max(number, 1)


####################################################################################################
# What can be filtered and sorted
####################################################################################################


@dataclass(frozen=True)
class Facet:
    """One filter, as a reader sees it."""

    param: str
    attribute: str
    label: str
    order: str = ORDER_ALPHA
    collapse_after: Optional[int] = None
    coerce: Callable = as_text


FACETS = (
    Facet("year", "year", _("Year"), order=ORDER_YEAR, coerce=as_year),
    Facet("jurisdiction", "jurisdictions", _("Jurisdiction"), collapse_after=8),
    Facet("region", "regions", _("Region")),
    Facet("topic", "policy_areas", _("Topic")),
    Facet("type", "data_users", _("Type")),
    Facet("resource", "resource_types", _("Type of resource")),
)

FACETS_BY_PARAM = {facet.param: facet for facet in FACETS}


@dataclass(frozen=True)
class SortOption:
    key: str
    label: str
    terms: tuple

    def orm_order(self) -> list:
        """The same order expressed for the database.

        Derived from `terms` rather than written out separately, so the indexed
        and degraded listings cannot drift apart. `nulls_last` is set in both
        directions because Meilisearch puts a record missing a sort attribute at
        the end whichever way it is asked to sort.
        """
        order = []
        for term in self.terms:
            attribute, _sep, direction = term.partition(":")
            column = models.F(attribute)
            order.append(
                column.desc(nulls_last=True)
                if direction == "desc"
                else column.asc(nulls_last=True),
            )
        return order


SORT_OPTIONS = (
    SortOption("newest", _("Newest first"), ("year:desc", "topic_sort:asc", "sort_title:asc")),
    SortOption("oldest", _("Oldest first"), ("year:asc", "topic_sort:asc", "sort_title:asc")),
    SortOption("az", _("Title A to Z"), ("sort_title:asc",)),
    SortOption("za", _("Title Z to A"), ("sort_title:desc",)),
)

SORT_BY_KEY = {option.key: option for option in SORT_OPTIONS}
DEFAULT_SORT = SORT_OPTIONS[0]


####################################################################################################
# A reader's query
####################################################################################################


@dataclass(frozen=True)
class Query:
    terms: str = ""
    selected: dict = field(default_factory=dict)
    sort: SortOption = DEFAULT_SORT
    page: int = 1

    @property
    def is_filtered(self) -> bool:
        """Whether any facet has a selection. A keyword on its own does not count."""
        return any(self.selected.values())

    @property
    def is_narrowed(self) -> bool:
        """Whether the reader has done anything at all to the default listing.

        Used for crawling and caching, where a sorted view counts: it is another
        URL that should not be indexed or cached separately.
        """
        return bool(self.terms) or self.is_filtered or self.sort is not DEFAULT_SORT

    @property
    def is_restricted(self) -> bool:
        """Whether the reader has asked for less than everything.

        Narrower than `is_narrowed`, which also counts a sort. Sorting hides
        nothing, so an empty listing under a sort is still an empty listing
        rather than a search that came back with nothing. That is the difference
        between telling a reader there is nothing here yet and telling them to
        remove a filter they never set.
        """
        return bool(self.terms) or self.is_filtered

    def filters(self) -> dict:
        """The selections, keyed by index attribute."""
        return {
            FACETS_BY_PARAM[param].attribute: list(values)
            for param, values in self.selected.items()
            if values
        }

    def filters_excluding(self, param: str) -> dict:
        """The selections without one facet's own filter.

        Used to recount that facet, so its unticked values do not vanish the
        moment one of them is ticked.
        """
        return {
            FACETS_BY_PARAM[key].attribute: list(values)
            for key, values in self.selected.items()
            if values and key != param
        }

    def querystring(self, page: Optional[int] = None) -> str:
        """This query as a query string, without the page unless one is given."""
        pairs = []
        if self.terms:
            pairs.append((PARAM_QUERY, self.terms))
        for facet in FACETS:
            pairs.extend((facet.param, value) for value in self.selected.get(facet.param, ()))
        if self.sort is not DEFAULT_SORT:
            pairs.append((PARAM_SORT, self.sort.key))
        if page and page > 1:
            pairs.append((PARAM_PAGE, page))
        return urlencode(pairs)

    def without(self, param: str, value) -> str:
        """A query string with one selected value removed, back at page one.

        `value` is coerced first because a template hands over a facet value,
        which is always text, while a selected year is an int. Comparing the two
        raw would drop nothing and leave the reader unable to untick a year.
        """
        dropped = FACETS_BY_PARAM[param].coerce(value)
        remaining = {
            key: tuple(item for item in values if item != dropped) if key == param else values
            for key, values in self.selected.items()
        }
        return replace(self, selected=remaining, page=1).querystring()

    def cleared(self) -> str:
        """A query string with every filter dropped, keeping the keyword and sort."""
        empty = dict.fromkeys(self.selected, ())
        return replace(self, selected=empty, page=1).querystring()


def parse(params) -> Query:
    """Read a query out of GET parameters, ignoring anything unrecognised.

    This is a public listing. A stale bookmark or a mangled share link should
    show the records, never an error, so bad input is dropped rather than
    rejected.
    """
    selected = {}
    for facet in FACETS:
        values = []
        for raw in params.getlist(facet.param):
            value = facet.coerce(raw)
            if value is not None and value not in values:
                values.append(value)
        selected[facet.param] = tuple(values[:MAX_VALUES_PER_FACET])

    return Query(
        terms=params.get(PARAM_QUERY, "").strip()[:MAX_TERMS],
        selected=selected,
        sort=SORT_BY_KEY.get(params.get(PARAM_SORT, ""), DEFAULT_SORT),
        page=as_page(params.get(PARAM_PAGE)),
    )


####################################################################################################
# Facets, shaped for a template
####################################################################################################


@dataclass(frozen=True)
class FacetValue:
    value: str
    label: str
    count: int
    selected: bool


@dataclass(frozen=True)
class FacetGroup:
    param: str
    label: str
    values: tuple
    collapse_after: Optional[int] = None

    @property
    def visible(self) -> tuple:
        """The values shown up front.

        A selected value is always here, however far down the list it falls,
        because a reader cannot untick something they cannot see.
        """
        if self.collapse_after is None:
            return self.values
        head = self.values[: self.collapse_after]
        chosen = tuple(item for item in self.values[self.collapse_after :] if item.selected)
        return tuple(head) + chosen

    @property
    def hidden(self) -> tuple:
        """The values behind the "show all" toggle."""
        if self.collapse_after is None:
            return ()
        return tuple(item for item in self.values[self.collapse_after :] if not item.selected)

    @property
    def selected_count(self) -> int:
        return sum(1 for item in self.values if item.selected)


def _facet_groups(distributions: dict, query: Query) -> tuple:
    groups = []
    for facet in FACETS:
        counts = distributions.get(facet.param, {})
        selected = query.selected.get(facet.param, ())
        values = [
            FacetValue(
                value=str(raw),
                label=str(raw),
                count=count,
                selected=facet.coerce(raw) in selected,
            )
            for raw, count in counts.items()
        ]
        groups.append(
            FacetGroup(
                param=facet.param,
                label=facet.label,
                values=tuple(_ordered(values, facet)),
                collapse_after=facet.collapse_after,
            ),
        )
    return tuple(groups)


def _ordered(values: list, facet: Facet) -> list:
    """Order a facet's values explicitly rather than trusting the response."""
    if facet.order == ORDER_YEAR:
        return sorted(values, key=lambda item: as_year(item.value) or 0, reverse=True)
    return sorted(values, key=lambda item: item.label)


####################################################################################################
# Results
####################################################################################################


@dataclass(frozen=True)
class Results:
    query: Query
    page_obj: object
    facets: tuple = ()
    degraded: bool = False

    @property
    def sort_options(self) -> tuple:
        return SORT_OPTIONS

    @property
    def total(self) -> int:
        return self.page_obj.paginator.count


def results(params, per_page: int = 12, client=None) -> Results:
    """Run a reader's query, falling back to the database if search is down.

    Args:
        params: The request's GET parameters.
        per_page: Records per page.
        client: Meilisearch client, built from settings when not given.
    """
    query = parse(params)
    try:
        return _from_index(query, per_page, client)
    except Exception as err:  # noqa: BLE001
        # Deliberately broad. Under the test settings there is no Meilisearch
        # host at all, so this is a KeyError rather than a search error, and a
        # listing page should degrade rather than fail.
        console.error(f"Evidence search unavailable, listing from the database instead: {err}")
        return _from_database(query, per_page)


def all_records(params, client=None) -> list:
    """Every record matching a reader's query, unpaginated and in order.

    What an export needs: the whole result set rather than the page the reader
    happens to be on. The same parsing and the same ordering as `results`, so a
    download matches the listing it was started from.

    If search is unreachable there are no filters to apply, so this returns
    every publishable record, exactly as the listing does while degraded.
    """
    query = parse(params)
    try:
        _, ids = _matching(query, client or search.get_client())
        return _entries(ids)
    except Exception as err:  # noqa: BLE001
        console.error(f"Evidence search unavailable, exporting the whole set instead: {err}")
        return list(fallback_queryset(query.sort))


def _matching(query: Query, client) -> tuple:
    """The index response for a query, and the ids it returned in order.

    One definition of the search call, so the listing and an export of it cannot
    ask the index for different things.
    """
    response = search.search(
        query.terms,
        filters=query.filters(),
        sort=list(query.sort.terms),
        limit=search.MAX_TOTAL_HITS,
        client=client,
        attributes=[search.PRIMARY_KEY],
    )

    ids = [hit[search.PRIMARY_KEY] for hit in response["hits"]]
    if len(ids) >= search.MAX_TOTAL_HITS:
        console.warn(
            f"Evidence search hit the {search.MAX_TOTAL_HITS} result ceiling; "
            f"results are being truncated",
        )

    return response, ids


def _from_index(query: Query, per_page: int, client) -> Results:
    client = client or search.get_client()
    response, ids = _matching(query, client)

    distributions = _distributions(query, response, client)

    page_obj = _paginate(ids, per_page, query.page)
    page_obj.object_list = _entries(page_obj.object_list)

    return Results(
        query=query,
        page_obj=page_obj,
        facets=_facet_groups(distributions, query),
        degraded=False,
    )


def _distributions(query: Query, response: dict, client) -> dict:
    """Facet counts, recounted for any facet the reader has ticked.

    Meilisearch counts against the filtered results, so ticking one topic would
    make every other topic disappear and a second one could never be chosen.
    Each ticked facet is therefore recounted with its own filter dropped, which
    is what keeps OR-within-a-facet usable. Untouched facets are already right
    from the first response.
    """
    counts = response.get("facetDistribution", {})
    distributions = {facet.param: counts.get(facet.attribute, {}) for facet in FACETS}

    for facet in FACETS:
        if not query.selected.get(facet.param):
            continue
        recount = search.search(
            query.terms,
            filters=query.filters_excluding(facet.param),
            sort=list(query.sort.terms),
            limit=0,
            client=client,
            attributes=[search.PRIMARY_KEY],
            facets=[facet.attribute],
        )
        distributions[facet.param] = recount.get("facetDistribution", {}).get(facet.attribute, {})

    return distributions


def _from_database(query: Query, per_page: int) -> Results:
    """The listing without Meilisearch: right order, no filters, no keyword."""
    page_obj = _paginate(fallback_queryset(query.sort), per_page, query.page)
    return Results(query=query, page_obj=page_obj, facets=(), degraded=True)


def fallback_queryset(sort: SortOption):
    """Every publishable entry, ordered the way the index would order it.

    The sort keys are annotated under the same names the index uses, so a sort
    option's terms translate straight across.
    """
    return (
        ImpactEntry.objects.publishable()
        .prefetch_related(*PREFETCH)
        .annotate(
            topic_sort=models.Min(Lower("policy_areas__name")),
            sort_title=Lower("description"),
        )
        .order_by(*sort.orm_order())
    )


def _paginate(items, per_page: int, number: int):
    paginator = Paginator(items, per_page)
    try:
        return paginator.page(number)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def _entries(ids) -> list:
    """Fetch the page's records, in the order the search returned them.

    The guard matters: the index can be ahead of the database, so an id for a
    record that has since been unpublished must be skipped rather than raise.
    """
    found = ImpactEntry.objects.publishable().prefetch_related(*PREFETCH).in_bulk(ids)
    return [found[pk] for pk in ids if pk in found]
