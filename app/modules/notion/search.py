"""
notion.search

A dedicated Meilisearch index for the evidence records that Open Ownership have
cleared for publication.

The Wagtail search backend is deliberately not used for these. It flattens every
indexed value to a string, so a record's list of policy areas would arrive as the
single value "AML/CFT, Corruption" and could never be faceted on, and it offers
no way to declare sortable attributes at all. Talking to Meilisearch directly
costs little and gives us both.

Only the columns Open Ownership mark public in the tracker are indexed. Anything
in the index can end up in front of a reader, so the internal notes stay out.
"""

# stdlib
import contextlib
from typing import Optional

# 3rd party
import meilisearch
from django.conf import settings

# Module
from modules.notion.models import ImpactEntry

INDEX_NAME = "evidence"
PRIMARY_KEY = "id"

# Order matters: Meilisearch ranks a match in an earlier attribute above a match
# in a later one.
SEARCHABLE_ATTRIBUTES = [
    "description",
    "summary",
    "jurisdictions",
    "regions",
    "policy_areas",
    "usability_themes",
    "data_users",
    "resource_types",
    "source_url",
]

FILTERABLE_ATTRIBUTES = [
    "year",
    "jurisdictions",
    "regions",
    "policy_areas",
    "usability_themes",
    "data_users",
    "resource_types",
]

# `topic_sort` and `sort_title` exist only to sort on. Sorting on the
# vocabularies themselves is not dependable, because a record holds several
# values, and sorting on the raw description is case-sensitive.
SORTABLE_ATTRIBUTES = ["year", "topic_sort", "sort_title"]

DEFAULT_SORT = ["year:desc", "topic_sort:asc", "sort_title:asc"]

# Documents fetched per request when working out what has left the index.
PAGE_SIZE = 500

# Seconds to wait on Meilisearch. One search runs per page request, so without a
# timeout an unresponsive Meilisearch would hold a worker until the socket gives up.
TIMEOUT = 3

# Jurisdictions alone has 48 values and Meilisearch's default cap is 100. Set it
# where it can be seen rather than finding out when a facet quietly truncates.
MAX_FACET_VALUES = 200

# The most hits a single search will return. Matches Meilisearch's own default
# for `pagination.maxTotalHits`, declared here so the two cannot drift.
MAX_TOTAL_HITS = 1000


####################################################################################################
# Client
####################################################################################################


def get_client() -> meilisearch.Client:
    """Return a Meilisearch client.

    Built from the Wagtail search backend's settings so there is one place that
    says where Meilisearch lives, even though this index is our own.
    """
    params = settings.WAGTAILSEARCH_BACKENDS["default"]
    return meilisearch.Client(
        f"{params['HOST']}:{params['PORT']}",
        params.get("MASTER_KEY", ""),
        timeout=TIMEOUT,
    )


####################################################################################################
# Documents
####################################################################################################


def build_document(entry: ImpactEntry) -> dict:
    """Turn one entry into the document that gets indexed.

    Lists stay lists so each value can be faceted on separately, and the year
    stays a number so it can be filtered and sorted numerically.
    """
    jurisdictions = sorted(entry.countries.values_list("name", flat=True))
    policy_areas = sorted(entry.policy_areas.values_list("name", flat=True))

    return {
        PRIMARY_KEY: entry.pk,
        "notion_id": entry.notion_id,
        "description": entry.description,
        "summary": entry.summary,
        "source_url": entry.source_url,
        "year": entry.year,
        "jurisdictions": jurisdictions,
        "regions": entry.display_regions,
        "policy_areas": policy_areas,
        "usability_themes": sorted(entry.usability_themes.values_list("name", flat=True)),
        "data_users": sorted(entry.data_users.values_list("name", flat=True)),
        "resource_types": sorted(entry.resource_types.values_list("name", flat=True)),
        "topic_sort": policy_areas[0].lower() if policy_areas else "",
        "sort_title": entry.description.lower(),
    }


def documents() -> list[dict]:
    """Every entry that may appear publicly, as index documents."""
    queryset = (
        ImpactEntry.objects.publishable()
        .prefetch_related(
            "countries",
            "policy_areas",
            "usability_themes",
            "data_users",
            "resource_types",
        )
        .order_by("pk")
    )
    return [build_document(entry) for entry in queryset]


####################################################################################################
# Filters
####################################################################################################


def build_filter(filters: Optional[dict]) -> str:
    """Turn a mapping of attribute to values into a Meilisearch filter expression.

    Values within one attribute are an OR, and the attributes are ANDed
    together, which is how a reader expects a set of facets to behave.

    Args:
        filters: Attribute name to the list of values to accept.

    Returns:
        A filter expression, or an empty string when there is nothing to filter.

    Raises:
        ValueError: If an attribute was never declared filterable, which would
            otherwise fail at query time with a less obvious message.
    """
    if not filters:
        return ""

    clauses = []
    for attribute, values in filters.items():
        if attribute not in FILTERABLE_ATTRIBUTES:
            msg = f"{attribute!r} is not filterable on the {INDEX_NAME} index"
            raise ValueError(msg)
        if not values:
            continue
        clauses.append(f"{attribute} IN [{', '.join(_literal(v) for v in values)}]")

    return " AND ".join(clauses)


def _literal(value) -> str:
    """Render one filter value, quoting and escaping anything that is not a number."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


####################################################################################################
# Index management
####################################################################################################


def configure_index(client: Optional[meilisearch.Client] = None) -> None:
    """Create the index if it is missing and apply its attribute settings."""
    client = client or get_client()

    # Meilisearch reports an index that already exists as an error, and there is
    # nothing to do in that case.
    with contextlib.suppress(Exception):
        client.create_index(INDEX_NAME, {"primaryKey": PRIMARY_KEY})

    client.index(INDEX_NAME).update_settings(
        {
            "searchableAttributes": SEARCHABLE_ATTRIBUTES,
            "filterableAttributes": FILTERABLE_ATTRIBUTES,
            "sortableAttributes": SORTABLE_ATTRIBUTES,
            "faceting": {"maxValuesPerFacet": MAX_FACET_VALUES},
            "pagination": {"maxTotalHits": MAX_TOTAL_HITS},
        },
    )


def reindex(client: Optional[meilisearch.Client] = None) -> dict:
    """Bring the index into line with the database.

    Documents are added over the top of what is already there and only then are
    the ones that have left removed, so a search running at the same time never
    sees an empty index.

    Returns:
        How many documents were written, how many were removed, and how many
        entries were held back for having no link.
    """
    client = client or get_client()
    configure_index(client)
    index = client.index(INDEX_NAME)

    records = documents()
    if records:
        index.add_documents(records, primary_key=PRIMARY_KEY)

    live = {record[PRIMARY_KEY] for record in records}
    stale = sorted(_indexed_ids(index) - live)
    if stale:
        index.delete_documents(stale)

    return {
        "indexed": len(records),
        "removed": len(stale),
        "withheld": ImpactEntry.objects.withheld_for_no_link().count(),
    }


def _indexed_ids(index) -> set:
    """Every id currently held in the index."""
    ids = set()
    offset = 0
    while True:
        page = index.get_documents(
            {"limit": PAGE_SIZE, "offset": offset, "fields": [PRIMARY_KEY]},
        )
        results = list(page.results)
        if not results:
            return ids
        for document in results:
            ids.add(getattr(document, PRIMARY_KEY, None) or dict(document)[PRIMARY_KEY])
        offset += len(results)


####################################################################################################
# Querying
####################################################################################################


def search(
    query: str = "",
    filters: Optional[dict] = None,
    sort: Optional[list] = None,
    limit: int = 20,
    offset: int = 0,
    client: Optional[meilisearch.Client] = None,
    attributes: Optional[list] = None,
    facets: Optional[list] = None,
) -> dict:
    """Search the evidence index.

    Args:
        query: Free text to search for. An empty string returns everything, in
            sort order, which is what an unsearched listing page wants.
        filters: Attribute name to the list of values to accept.
        sort: Sort terms, defaulting to year descending, then topic, then title.
        limit: How many results to return.
        offset: Where to start, for paging.
        client: Meilisearch client, built from settings when not given.
        attributes: Document fields to return. Narrow this to `["id"]` when the
            caller only needs to know which records matched.
        facets: Attributes to count. Defaults to every filterable attribute;
            pass a single one when recounting a facet in isolation.

    Returns:
        The raw Meilisearch response, including `hits` and `facetDistribution`.
    """
    client = client or get_client()
    params = {
        "limit": limit,
        "offset": offset,
        "sort": list(sort) if sort else list(DEFAULT_SORT),
        "facets": list(facets) if facets is not None else list(FILTERABLE_ATTRIBUTES),
    }
    if attributes is not None:
        params["attributesToRetrieve"] = list(attributes)

    expression = build_filter(filters)
    if expression:
        params["filter"] = expression

    return client.index(INDEX_NAME).search(query, params)
