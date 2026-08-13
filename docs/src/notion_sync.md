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

### Sync history

Every run is recorded as a `SyncRun`, and the Wagtail admin shows them at
**Reports > Notion sync**. Before this the only record of a run was a Slack
message, which Open Ownership cannot see and which scrolls away, so a sync that
stopped firing three weeks ago looked exactly like one that succeeded an hour
ago.

The banner above the table is the point of the page. It says one of three
things: nothing has been recorded yet; the last full sync completed N hours ago,
noting any rows that could not be read; or there has been no completed full sync
in the last `NOTION_SYNC_STALE_AFTER` (36 hours by default, set to comfortably
more than one cycle of the cron). Below it, one row per run, with the failures
for that run in a `details` block built from the run's own stored JSON, so
opening one costs no query and nobody has to navigate away to find out what
broke.

**Completed, not perfect.** `last_completed_full()` counts a run that rejected
some rows, because such a run still worked: it reached Notion, fetched
everything and wrote what it could. A row Notion holds badly is data for Open
Ownership to fix. Counting those as failures would have left the warning on
permanently while a single bad row sat in the tracker, and nobody reads a banner
that is always red. Only a run that did not finish is excluded.

Four things worth knowing:

* **The row is written before the work starts**, with status `running`, and any
  run left open is closed off at the start of the next one. Without that, a run
  killed by a deploy or the OOM killer would sit as `running` forever, and "the
  sync has been hanging for three days" would read exactly like "the sync never
  fired".
* **A crash is recorded and then re-raised.** Whatever the run gathered before
  the exception is kept, with status `error` and the reason, and the exception
  carries on so the cron still reports it.
* **Dry runs are recorded and flagged.** A dry run that turns up twelve invalid
  rows is worth keeping, and it is how the tracker gets checked after a change.
  A dry run and an `--only` run never count as the last successful full sync.
* **Only the last 200 runs are kept** (`NOTION_SYNC_RUN_HISTORY`), counted rather
  than aged so the history survives the sync being switched off for a fortnight,
  which is exactly the situation the report exists to reveal. The last successful
  full run is always kept whatever its age, because the banner is measured
  against it.

Access is the `notion.view_syncrun` permission, granted to `Editors` and
`Moderators` by a data migration and adjustable per group in the admin
afterwards. It is a permission rather than a superuser check because making this
visible to Open Ownership was the reason for building it.

`report.py` holds the serialisation. `as_dict` is a persisted format, so it is
written out field by field rather than with `dataclasses.asdict`, and `from_dict`
is deliberately forgiving in both directions: a run stored before a counter
existed still has to render, and one stored after a counter was dropped must not
raise. Stored failure detail is capped at `MAX_STORED_INVALID` per database, with
the true count kept alongside, because a deleted Notion column fails every row
and would otherwise put megabytes of near-identical JSON in the database.

### The layers

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
  `request.build_absolute_uri`. Both give an https URL now that
  `SECURE_PROXY_SSL_HEADER` is set, but the site record gives the canonical
  address rather than whichever hostname the reader happened to arrive on, and
  this is a file Open Ownership may hand out.
* **The download link is hidden while search is degraded.** With Meilisearch
  down there are no filters to carry, so the file would quietly be the whole
  dataset whatever the reader had asked for. Hitting the URL directly in that
  state still returns everything.

### Topic icons

Each topic shows an icon beside its name, mapped in `modules/notion/icons.py`.
The map is code-side rather than driven from Notion, as agreed with OO (A-S8):
the icon set stays consistent and an editor cannot break the visuals. The cost is
that a topic added or renamed in the tracker needs a line here to get its own
icon. Until then it gets `FALLBACK`, drawn to look deliberate rather than broken.

**The icon never appears without the topic name**, so a topic we have not drawn
yet costs a reader nothing, and the icons are `aria-hidden` because the name
beside them already says everything.

Three of the ten topics in the tracker are placeholders while OO supply the
artwork: `aml-cft.svg`, `natural-resources.svg` and `organised-crime.svg`. They
are deliberately identical to the fallback, so the site looks finished rather
than half-built. Replacing those three files is the whole job; the map does not
change.

Icons arrive from Illustrator carrying an XML declaration, `id="Layer_1"` and
generic `.cls-1` class names. Two on one page would restyle each other, and the
site logo uses `.cls-1` too, so it was never only a collision between icons. Each
file is therefore cleaned on the way in: the classes are namespaced to the
filename, the id and declaration are dropped, and `aria-hidden` is added. The
artwork itself is untouched. `modules/notion/tests/test_icons.py` checks every
file in the directory for all of that, so the next batch cannot slip through
dirty.

### When there is nothing to show

Three different situations, three different messages, because telling a reader
to remove a filter they never set is worse than saying nothing:

| Situation | What the reader sees |
|---|---|
| Nothing published at all | "There are no records here yet." No advice, because there is nothing to undo |
| A search or filter matched nothing | "Try removing a filter, or searching for something broader" |
| Meilisearch unreachable | Every record, filters hidden, and a notice saying filtering is unavailable |

`Query.is_restricted` is what tells the first two apart. It is deliberately
narrower than `is_narrowed`: a sort counts as narrowing for caching and crawling
purposes but hides nothing, so an empty listing under a sort is still an empty
listing. The download link is hidden in all three cases.

### Keyboard and screen readers

* **Card titles are `h3`**, sitting under the results section's own heading. As
  `h2` they were siblings of that heading, which left anyone navigating by
  heading with a flat list and no structure.
* **Focus is moved deliberately after every htmx swap**, in
  `assets/_dev/js/components/evidence-cards.js`. Swapping a card destroys the
  element that was clicked, which drops focus to the top of the document; a
  keyboard user would have to tab back through the whole page after opening a
  record. Opening moves focus to the record's heading, so the reader hears which
  record opened before its controls. Closing hands focus back to that card's own
  "Read more".
* **`aria-expanded` is set by JavaScript, not in the template.** The control is
  an ordinary link until JavaScript arrives, and only then does it behave as a
  disclosure. In the markup it would be a lie.
* **The result count carries `role="status"`.** Filtering is a full page load,
  so the count is what reports the change.

### Region colours

Open Ownership's secondary brand palette holds six colours and the tracker has
six regions, so each region takes one. The palette's own meaning is the six
stages of implementing beneficial ownership transparency, nothing to do with
regions, so the pairing in `modules/notion/colours.py` is arbitrary: regions
alphabetically against the palette in printed order. Reproducible and easy to
explain, which is the most that can be said for any assignment.

A record's colour shows twice: a bar down the side of its card, and a dot beside
each region's name.

**The colours are never put behind text.** Measured against white and against the
body colour, five of the six only reach AA one way round, and `#DB00C9` reaches
it neither way (4.33 and 3.59, against the 4.5 AA needs). That is why regions are
dots rather than filled chips like the topics, and it is also what was promised
on accessibility grounds when this was agreed: the region name is always beside
the colour, so colour is never the only signal. A test pins that contrast finding,
so if OO change the palette it fails and a chip becomes worth revisiting.

Two edge cases the data actually contains:

* **Fourteen records span two regions**, mostly Asia and Europe. The bar splits
  evenly between them with hard stops rather than picking one and misreporting
  the record. `colours.region_bar` builds the gradient.
* **Six records carry no jurisdiction at all**, so they have no region. No bar
  element is rendered, rather than a grey one implying a region they do not have.

**The colour is set inline on a real element, not through a CSS custom property.**
`postcss-css-variables` in this project's build resolves custom properties at
compile time, so one set from a template arrives in `main.min.css` as
`background: undefined`. It fails quietly, because every other declaration in the
same rule still applies. A test checks `--region-bar` never appears in the
rendered page.

Open Ownership's guidelines print `RGB 245, 245, 245` beside `Hex #1BB0A7` on the
last swatch. Those are two different colours. The hex matches the printed swatch
and is what is used; worth raising with them.

### Analytics

Open Ownership asked for twelve metrics (A-S6 in the sprint brief). Most are
native Plausible and need nothing. Three are custom events, sent by
`assets/_dev/js/components/evidence-analytics.js`:

| Event | Properties | When |
|---|---|---|
| `Evidence: Search` | `results`, and `term` only if switched on | The listing loads with a keyword |
| `Evidence: Filter` | `facet`, `value` | The listing loads with a facet ticked, one event per ticked value |
| `Evidence: Source click` | `topic`, `jurisdiction`, `region` | A reader clicks through to a record's source |

Total outbound clicks are counted by Plausible's `outbound-links` extension on
its own; the `Source click` event exists to add the breakdown OO asked for.
`file-downloads` was already enabled and is kept.

Four things worth knowing:

* **`window.plausible` is defined in `_partials/analytics.jinja` before the
  script loads**, and in every environment. Without it an early event would
  throw and be lost. In development the script itself never loads, so events
  queue on `window.plausible.q` where they can be read without being sent.
* **Filters and searches are counted on page load, not on click.** Both are
  plain GET forms, so an event fired at submit time would race the navigation.
  The active facets are read off the ticked checkboxes, so the list of facets
  lives only in `evidence.py` and never has to be repeated in JavaScript.
* **Paging does not count a filter twice.** The query string with `page`
  removed is remembered in `sessionStorage`, so clicking through to page two of
  the same filtered results reports nothing further.
* **Search terms are recorded**, under `EVIDENCE_RECORD_SEARCH_TERMS`. This was
  put to OO as a privacy call rather than a technical one (A-S6) and they asked
  for the terms, not just the counts. The term is lowercased before it is sent so
  the same search groups together whatever case it was typed in, and it arrives
  already trimmed and capped at `evidence.MAX_TERMS` because the input holds the
  parsed query rather than the raw one. Search counts keep working if this is
  turned back off.

`topic`, `jurisdiction` and `region` on the click event carry every value a
record holds, joined with `; `, so a record with three topics is one property
value rather than three. That keeps the number of distinct property values down,
which matters because custom properties count towards a Plausible plan's limits.
OO have confirmed their plan covers the volume.
