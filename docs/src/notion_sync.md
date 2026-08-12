## Notion sync

Country, commitment, disclosure regime and impact data all come from Notion
databases. An external cron runs one management command:

```
manpy sync_notion
```

Useful flags: `--dry-run` fetches and validates without writing, `--force`
updates rows Notion has not touched, and `--only` limits the run to named
syncers (`countries`, `commitments`, `regimes`, `regimes_sub`, `impact`).

### Columns are matched by id, not by name

Open Ownership rename tracker columns as their own thinking moves on. Notion
keeps a column's **id** when that happens, so the sync matches on the id and a
rename costs nothing.

Each row schema declares its columns in a `*Cols` class in
`modules/notion/schemas/rows.py`, one `Column(id, name)` per column:

```python
class BotCols:
    DESCRIPTION = Column("title", "One sentence description (P)")
    DATA_USER = Column("CAQ%3A", "Data user")
```

The name is there for people. It is what the schema reads as, and what the
sync's failure messages say, so it should be kept current, but nothing breaks if
it goes stale. `schemas/columns.py` holds the `Column` type and the `Columns`
lookup that reindexes a page's properties by id.

The sync still checks every declared column is present before writing anything,
and skips that database with a loud message if any have gone. Without that check
a missing column would decode to an empty value rather than an error, so the
sync would blank every field behind it and report success.

**An id is not a complete defence.** A column deleted and recreated in Notion
keeps its name but gets a new id, which the sync sees as the column having gone.
That is what this is for:

```
manpy notion_columns
```

It prints every column of every configured database as a ready-made `Column(...)`
line. Run it when the sync reports a missing column: if the id has moved, that is
a delete and recreate rather than a rename. `modules/notion/samples/columns.py`
is a snapshot of the same output, and the schema tests check every declared id
and name against it, so a typo cannot quietly disarm the guard.

The code is in three layers: `client.py` fetches, `schemas/` validates with
Pydantic, and `sync/` persists. A row that fails validation is skipped rather
than being allowed to write empty values over good data, and is listed at the
end of the run with a link to the row in Notion and what was wrong with it.
The same summary goes to Slack.

Database ids live in `NOTION_DATABASES` in the settings. Adding a new one needs
the Wagtail integration connected to that page in Notion, which only a Notion
workspace admin can do; `manpy check_notion_access` reports what the integration
can currently reach.

Two things about the impact tracker are worth knowing:

* Its files column becomes `ImpactAttachment` rows. Files Notion hosts are
  fetched once into the "BOT impact tracker" Wagtail collection as images or
  documents; external links are stored as links and never fetched. Notion
  re-signs its file urls on every fetch, so attachments are identified by the
  url path rather than the whole url.
* Only entries with `publish` set have been cleared by Open Ownership for
  display. Everything else is synced so the record stays complete, and must
  stay hidden.
* A record with no link is not shown at all, at Open Ownership's request: the
  point of a record is to send a reader to its source. `ImpactEntry.objects`
  has `publishable()` for the rule and `withheld_for_no_link()` for the ones it
  drops, and the indexer reports how many were held back.

The countries database also holds a row called "Global", which the impact
tracker uses to mean worldwide. It is listed in `NOTION_NON_COUNTRY_ROWS` and
excluded from the sync, so it never becomes a country on the site. Impact
entries carry their own `international` flag instead.


## Evidence search

Published impact entries have their own Meilisearch index, `evidence`, built by
`modules/notion/search.py`.

`sync_notion` rebuilds it automatically once a sync finishes, so the index never
drifts from the data. It always rebuilds, not only when impact entries changed,
because a change to a country's region alters evidence documents too. A dry run
skips it, and so does `--no-index`. If Meilisearch is unreachable the sync still
counts as done, since the Notion data is already saved, and it tells you to
rerun the indexer by hand:

```
manpy index_evidence
```

Use `--configure-only` to reapply the index settings without rewriting the
documents. Reindexing writes over the existing documents and only then removes
the ones that have gone, so a search running at the same time never sees an
empty index.

This does not go through the Wagtail search backend. That backend flattens every
value to a string, so a record's list of policy areas would be indexed as the
single value `"AML/CFT, Corruption"` and could not be faceted on, and it has no
way to declare sortable attributes.

* **Searchable**: description, summary, jurisdictions, regions, policy areas,
  usability themes, data users, resource types, source URL. Order matters,
  since Meilisearch ranks a match in an earlier attribute higher.
* **Filterable**: year, jurisdictions, regions, policy areas, usability themes,
  data users, resource types. Values within one facet are ORed and the facets
  are ANDed.
* **Sortable**: year, `topic_sort` and `sort_title`. The last two exist only to
  sort on, because a record holds several policy areas and the raw description
  sorts case-sensitively.
* **Default order**: year descending, then topic, then title. Records with no
  policy area come last within their year.

The index holds the whole summary so a term late in the text is still findable.
Cards show `display_summary`, which trims to `ImpactEntry.SUMMARY_WORDS` (50).
Open Ownership aim for that length but Notion cannot enforce it, and a character
count reads differently at every font width, so the limit is applied on words at
display time rather than relied on at their end.

### Filtering, search and sort

`modules/notion/evidence.py` is the public query layer: it owns the URL parameter
names, the sort options, and turning GET parameters into a page of results.
`search.py` stays a plain Meilisearch adapter and knows nothing about URLs.

Six facets are exposed, and `FACETS` is both the naming map and the allowlist, so
an attribute missing from it cannot be reached from a URL at all:

| URL parameter | Index attribute | Shown as |
|---|---|---|
| `year` | `year` | Year |
| `jurisdiction` | `jurisdictions` | Jurisdiction |
| `region` | `regions` | Region |
| `topic` | `policy_areas` | Topic |
| `type` | `data_users` | Type |
| `resource` | `resource_types` | Type of resource |

`usability_themes` stays filterable in the index but is not exposed: it is
populated on only 29 of 237 rows and is not one of the six Open Ownership asked
for. Sort is `?sort=` with `newest` (the default, and left out of URLs),
`oldest`, `az` or `za`.

Everything is a plain GET form, so filtering, searching, sorting and pagination
all work with JavaScript off. There is deliberately no hidden `page` field:
unchecked boxes submit nothing, so changing a filter starts again at page one
without a line of code.

**Facet counts are recounted per facet.** Meilisearch counts against the filtered
results, so ticking one topic would make every other topic vanish and a second
one could never be chosen. Each ticked facet is queried again with its own filter
dropped. That is what keeps "filter by multiple topics" usable, and it is the
first thing to check if the facet lists ever start collapsing.

Filtered views are served `noindex` and `no-cache`. Six facets over 48
jurisdictions is an unbounded crawl space, and wagtail-cache keys on the full URL,
so caching the combinations would let anyone fill Redis with `?anything=1`.

If Meilisearch is unreachable the page still lists every record, in the reader's
chosen order, with the filters hidden and a notice saying so.
`evidence.fallback_queryset` owns that ordering and derives it from the same sort
terms, so the two paths cannot drift.

Only entries that pass `ImpactEntry.objects.publishable()` are indexed, and only
the columns Open Ownership mark public in the tracker. Lessons, "OO outputs used in"
and "Presentations/slide decks used in" are deliberately left out: anything in
the index can end up in front of a reader.

### One record

Every published record has its own URL, `/<lang>/evidence/<notion-id>/`, served by
`EvidenceDetailView` in `modules/content/views.py`. It is a plain Django view
rather than a route on `BotCentrePage`, because entries are not Wagtail pages,
and it is keyed on the Notion id because a record has no title to build a slug
from. `ImpactEntry.get_absolute_url` is the only place that URL is built.

The same view answers three ways:

| Request | Response |
|---|---|
| Ordinary | `views/evidence_detail.jinja`, a whole page |
| `HX-Request` header | `_partials/evidence_card_expanded.jinja`, the open card |
| `HX-Request` and `?collapsed=1` | `_partials/evidence_card.jinja`, the shut card |

`HX-Request` is a header htmx sends on every request it makes, so reading it
needs no extra Python dependency. Both card partials render standalone, which is
what lets one URL serve the page and both halves of the toggle.

The expand control on a card is an ordinary link to that URL, upgraded with
`hx-get` into an in-place swap of the card, and `hx-push-url` puts the record's
URL in the address bar so it stays shareable. Close does the reverse. With
JavaScript off both are just links, one to the record's page and one back to the
listing. That is the whole of what Open Ownership asked for in A-S9: the record
opens where it sits, and it still has a URL a reader can send to someone.

`_partials/evidence_detail_body.jinja` holds the record's fields and is included
by both the page and the open card, so the two cannot show different things. A
shut card shows description, jurisdiction, topic and year only.

**Only one record is open at a time**, which `assets/_dev/js/components/evidence-cards.js`
enforces. Opening a record throws away its shut markup, so that markup is kept
in a `Map` and put back when another record opens. Shutting the others that way
costs no extra request, and nothing can race the opening card for the address
bar: with two open, shutting either one would put the listing URL back while a
record was still open.

Two things about that file are easy to get wrong. `htmx:afterSwap` reports the
element it *replaced*, not the new one, so which way a swap went has to be read
from the response rather than from the card's classes. And a card put back from
the `Map` needs `htmx.process` called on it, or its links are dead.

**Every control on the listing names the listing itself**, rather than being a
relative `?...` link or a form with no `action`. Once a record is open the
address bar holds that record's URL, so a relative control would aim at the
record and the reader would land on one entry instead of a filtered list. That
covers the filter form, "Clear filters", the facet chips and pagination. The
shared pagination partial takes an optional `pagination_base` for this and stays
relative everywhere else.

The view raises a 404 for anything `publishable()` excludes, so a record can
never be missing from the listing but reachable by URL.

### CSV export

`/<lang>/evidence.csv`, served by `EvidenceExportView`. It reads the same query
parameters as the listing, so no parameters gives the whole dataset and the
listing's own query gives exactly what is on screen. `evidence.all_records` is
the query layer's unpaginated counterpart to `results`; both go through one
`_matching` call, so a download cannot drift from the listing it started from.
The `page` parameter is deliberately ignored: an export is the lot.

The columns are the public field list and nothing else:

| Column | Source |
|---|---|
| Description | `description` |
| Summary | `summary`, whole, not the card's trimmed version |
| Year | `year` |
| Jurisdiction | `countries`, or "International" for a worldwide record |
| Region | `display_regions`, reached through the jurisdictions |
| Topic | `policy_areas` |
| Type | `data_users` |
| Type of resource | `resource_types` |
| Link | `source_url` |
| Record URL | the record's own page on the site |

Several values in one cell are separated by `; ` rather than a comma, because tag
names carry commas of their own and a reader splitting a cell should not have to
guess. The file is named `bot-evidence.csv`, or `bot-evidence-filtered.csv` when
the reader has narrowed it, so two downloads do not collide on disk. The whole
file is English, including "International", because its columns are named after
the Notion tracker and a half-translated data file is harder to work with.

Two things worth knowing:

* **The record URL is built from Wagtail's site record**, not from
  `request.build_absolute_uri`. `SECURE_PROXY_SSL_HEADER` is not configured, so
  Django sees plain http behind the TLS proxy and would otherwise write `http://`
  links into a file Open Ownership may hand out.
* **The download link is hidden while search is degraded.** With Meilisearch
  down there are no filters to carry, so the file would quietly be the whole
  dataset whatever the reader had asked for. Hitting the URL directly in that
  state still returns everything.
