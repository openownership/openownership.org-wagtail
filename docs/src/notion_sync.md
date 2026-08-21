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

### Sync now

The page carries a **Sync now** button, gated on the same permission: anyone who
can see the status can ask for a fresh one. It runs the same pair of steps as the
management command, a full sync followed by an evidence reindex, through
`runner.sync_and_index`.

Three things about it:

* **It is a POST, not a link.** A sync costs several hundred calls to Notion's
  API, so it must never be reachable by a crawler, a link prefetch or a
  bookmark. A GET returns 405.
* **The work happens on a thread**, so the request returns immediately and the
  run appears in the listing as `running`. This project has no task queue, and
  holding a request open for a fourteen second sync would risk gunicorn's
  timeout and tie up a worker for no reason. It degrades safely: the run row is
  written before the work starts, so a thread lost to a worker restart is reaped
  as "Did not finish" on the next run rather than disappearing. What it does not
  give you is a retry, which is the trade for not adding Celery.
* **A second sync is refused while one is running**, and the button reads "Sync
  running" and is disabled. Two syncs writing the same tables at once is worth
  preventing, and clicking twice is the obvious way to cause it.

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
excluded from the sync, so it never becomes a country on the site. An entry
pointing at it is marked `worldwide` instead, which is what lets the record still
report a jurisdiction and a region of "Global" rather than nothing at all. Six
published records are like this.

`worldwide` is not the same as the tracker's older `International` checkbox,
which is synced to `international` and used only for a record marked that way and
nothing else. Where both are set, "Global" wins, because that is what the tracker
itself shows in the jurisdiction column.


## Evidence search

Published impact entries have their own Meilisearch index, `evidence`, built by
`modules/notion/search.py`.

`sync_notion` rebuilds it automatically once a sync finishes, so the index never
drifts from the data. It always rebuilds, not only when impact entries changed,
because a change to a country's region alters evidence documents too. That is
`CountryTag.notion_region`, described under [Two lists of regions](#two-lists-of-regions). A dry run
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
  break a tie within a year, because a record holds several policy areas and the
  raw description sorts case-sensitively.
* **Default order**: year descending, then topic, then title. Records with no
  policy area come last within their year.

The index holds the whole summary so a term late in the text is still findable.
Cards show `display_summary`, which trims to `ImpactEntry.SUMMARY_WORDS` (50).
Open Ownership aim for that length but Notion cannot enforce it, and a character
count reads differently at every font width, so the limit is applied on words at
display time rather than relied on at their end.

### How current the listing is

Under the title, the page says: "The BOT Evidence Centre is updated on an ongoing
basis. Last updated: 19 August 2026". Open Ownership asked for this to stand on
its own rather than sit inside the body copy, where it was easy to miss.

The date is `ImpactEntry.objects.last_updated()`, the newest `notion_updated`
across the tracker. Two things follow from that choice:

* It is Notion's own timestamp, not the time of the last sync. The sync runs
  whether anything changed or not, so a sync time would tell a reader when the
  site last looked rather than when the tracker last moved.
* Every row counts, including the ones a reader never sees. Open Ownership edit
  rows before publishing them, and the sentence is about the tracker rather than
  about the visible subset.

Before the first sync there are no rows and no date, so the whole line is left
out rather than claiming anything. The date is rendered inside `time` with an
ISO `datetime`, so it is readable by something other than a person.

The sentence itself is fixed text in the template. Moving it into a page field
would let Open Ownership reword it; nobody has asked for that yet.

### Filtering, search and sort

`modules/notion/evidence.py` is the public query layer: it owns the URL parameter
names, the sort options, and turning GET parameters into a page of results.
`search.py` stays a plain Meilisearch adapter and knows nothing about URLs.

Five facets are exposed, and `FACETS` is both the naming map and the allowlist, so
an attribute missing from it cannot be reached from a URL at all:

| URL parameter | Index attribute | Shown as |
|---|---|---|
| `year` | `year` | Year |
| `jurisdiction` | `jurisdictions` | Jurisdiction |
| `region` | `regions` | Region |
| `topic` | `policy_areas` | Topic |
| `resource` | `resource_types` | Type of resource |

`usability_themes` and `data_users` stay filterable in the index but are not
exposed. `usability_themes` is populated on only 29 of 237 rows, and Open
Ownership asked for the resource type rather than the data user, so a
hand-written `?type=` is simply ignored. Sort is `?sort=` with `newest` (the
default, and left out of URLs) or `oldest`. Both are by date: Open Ownership
asked for the title orders to come out, and an old `?sort=az` link now lands on
the default rather than on an error.

Everything is a plain GET form, so filtering, searching, sorting and pagination
all work with JavaScript off. There is deliberately no hidden `page` field:
unchecked boxes submit nothing, so changing a filter starts again at page one
without a line of code.

**Clearing a keyword takes one click.** A `type="search"` field gets an "x" from
the browser which empties the box and submits nothing, so dropping a search used
to mean pressing Apply as well. A "Clear search" link sits under the field
whenever there is a keyword, pointing at `Query.without_terms()`: the keyword
goes, the filters and the sort stay. It is a plain link, so it needs no
JavaScript, and its label is fixed because a keyword can run to `MAX_TERMS`, 200
characters, and would be no use as the text of a control.

`components/evidence-search.js` then makes the browser's own "x" follow that
same link, so the reader's instinct is right rather than fought. It listens for
the `search` event and acts only when the box is empty, since that event also
fires on Enter, which the form already handles. Firefox draws no clear button at
all, which is the other reason the link is the real fix and the script only
polish.

**The values shown on a record are filters.** The year, a topic tag, a
jurisdiction, a region and a type of resource each set the same thing as their
box in the filter panel, so a click adds
that value to whatever the reader has already chosen, and clicking a value they
have already chosen takes it off again. `Query.toggled` builds the link and
`evidence.facet_query` is the template global that calls it, through
`_partials/facet_link.jinja`. The keyword, the other facets and the sort are all
kept; the page goes back to one. What is active stays visible in the chips above
the results, so the change can be seen and undone in a click.

They carry `nofollow`, because every combination of filters is a URL of its own
and `noindex` is only read once a crawler is already down there. A record's own
page has no listing state behind it, so its values filter the listing by
themselves alone.

Each link carries hidden text saying what it does, because "Kenya" on its own
reads as a label rather than as something that will change the page. Two things
on a record are deliberately not links: "Global" and "International", which are
what the tracker calls a worldwide record rather than values anyone can filter a
jurisdiction by, and "Type", the data user, which is no longer a facet.

The card takes underlines off its links, which suits a card title but not these:
they sit inline among plain text, where colour on its own does not tell a reader
that something can be clicked. `bot-centre.css` puts the underline back for them,
and drops it on hover as the rest of the site does. Topic tags are chips rather
than text, so they keep the chip look and darken instead.

Opening a record renders the open card in `EvidenceDetailView`, which knows
nothing about the listing, so the expand control's `hx-get` carries the reader's
query and the view parses it back out. `href` and `hx-push-url` stay clean: those
are what a reader shares.

**Facet counts are recounted per facet.** Meilisearch counts against the filtered
results, so ticking one topic would make every other topic vanish and a second
one could never be chosen. Each ticked facet is queried again with its own filter
dropped. That is what keeps "filter by multiple topics" usable, and it is the
first thing to check if the facet lists ever start collapsing.

Filtered views are served `noindex` and `no-cache`. Five facets over 48
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
URL in the address bar so it stays shareable. It carries a chevron,
`svg/expand.jinja`, because "Read more" on its own does not say which way the
record is about to move. The same chevron sits on "Close" and the stylesheet
turns it over, so one asset covers both directions. It is `aria-hidden`: the word
beside it already says what happens. Close does the reverse. With
JavaScript off both are just links, one to the record's page and one back to the
listing. That is the whole of what Open Ownership asked for in A-S9: the record
opens where it sits, and it still has a URL a reader can send to someone.

`_partials/evidence_detail_body.jinja` holds the record's fields and is included
by both the page and the open card, so the two cannot show different things. A
shut card shows description, jurisdiction, topic and year only.

Two rows in that partial, Topic and Type, are commented out at the moment. A
record's own page therefore lists no topics; the open card still shows its topic
chips beside the title, because those are in the card rather than in this
partial.

**The link to the source is not on a shut card.** Open Ownership asked for it to
wait until a reader opens the record, so a card carries one control rather than
two and the reader sees the summary before they leave the site. It costs a click
to reach a source from the listing, which was put to them as the trade and
accepted. One consequence worth watching: outbound clicks can only start from an
open record now, so the `Evidence: Source click` numbers are not comparable with
those from before this changed.

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
| Jurisdiction | `countries`, or "Global" for a worldwide record |
| Region | `display_regions`, the tracker's region for each jurisdiction |
| Topic | `policy_areas` |
| Type | `data_users` |
| Type of resource | `resource_types` |
| Link | `source_url` |
| Record URL | the record's own page on the site |

Several values in one cell are separated by `; ` rather than a comma, because tag
names carry commas of their own and a reader splitting a cell should not have to
guess. The file is named `bot-evidence.csv`, or `bot-evidence-filtered.csv` when
the reader has narrowed it, so two downloads do not collide on disk. The whole
file is English, including "Global", because its columns are named after
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

### Two lists of regions

The site holds two different groupings of the world, and the evidence listing
uses the tracker's:

* `notion.Region`, the site's own editorial records. Six continents, each with a
  blurb and a page at `/region/<slug>/`, and set on a country by hand in Wagtail.
  The impact section and the country listings use these.
* `CountryTag.notion_region`, a copy of the `Region` select on the country
  tracker in Notion. Eight values in the World Bank style, including "Europe and
  Central Asia" and "Latin America and the Caribbean".

`ImpactEntry.display_regions` reads the second. A reader who has the tracker open
beside the listing sees the same region names in both, which is what Open
Ownership asked for. The two lists genuinely disagree: Notion puts Ukraine in
"Europe and Central Asia" where the site's own records say "Europe".

The value is stored as the tracker's own text rather than matched to a record on
this side, so a region added or renamed in Notion arrives with the next sync and
needs no work here.

Worldwide records have no country to reach a region through, so they report
"Global", the region the tracker rolls them up to. On a record's own page that
sits under a "Region" label beside its "Global" jurisdiction. A shut card labels
neither, so `display_card_regions` drops the repeat and the word appears once.

**A row the sync has already seen is skipped unless Notion has changed it**, so
both `notion_region` and `worldwide` start empty on an existing database. Fill
them once with a forced sync, which reindexes as it finishes:

```
manpy sync_notion --force
```

Until that runs the listing shows no regions at all.

### The edge of a card

Every card carries a 6px edge down its left side in the site's blue,
`blue-medium`. It marks a record out from the page and stands for nothing, so it
is the same on every record and the colour lives in `bot-centre.css` rather than
being passed in from a template.

**Regions were colour coded and are not any more.** Each region had a colour from
Open Ownership's secondary palette, shown as that edge and as a dot beside the
region's name. Open Ownership asked for it to come out: it did not help a reader
and read as though the colours meant something they did not. Region names are now
plain text beside the other facts.

`modules/notion/colours.py` and its tests are kept although nothing calls them,
in case Open Ownership want the colours back.

Taking the colours out also removed the parts built to make them safe: the split gradient
for a record spanning two regions, the contrast test behind using dots rather
than filled chips, and the rule about setting the colour inline because
`postcss-css-variables` resolves custom properties at build time.

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
