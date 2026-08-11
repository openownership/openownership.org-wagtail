# openownership.org

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/20145b7e6389409fa98ec02be4fe5b1b)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=hactar-is/openownership.org&amp;utm_campaign=Badge_Grade) [![Codacy Badge](https://app.codacy.com/project/badge/Coverage/20145b7e6389409fa98ec02be4fe5b1b)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=hactar-is/openownership.org&utm_campaign=Badge_Coverage)

This is a Wagtail site.

[Sprint planner](https://github.com/hactar-is/openownership.org/projects/1)


## First run

You'll probably want to do `sudo nano /etc/hosts` and add:

`0.0.0.0    openownership.test`


1. `git submodule update --init --recursive`
2. `goenv`
3. `gofab` (and then probably `cd ..`)
4. `docker pull ghcr.io/hactar-is/openownership:latest`
5. `docker-compose up --build -d`
6. `fab docker.fish` to get a shell inside the running web container


### If you don't have access to Hactar tooling...

You'll need all the project's environment variables in a .env file expanded into the shell session.

1. `docker-compose up --build -d`
2. `docker exec -it openownership_web_1 fish` or `docker exec -it openownership_web_1 zsh` depending on your preference

### Once you have a shell inside the web container

1. `manpy migrate`
2. `manpy createsuperuser`
3. `manpy populate_taxonomies`  # To create tags
4. `runserver`

Site should now be accessible at `http://openownership.org.test:5000` (or http://0.0.0.0.test:5000)

## Static assets

1. `cd app/asset/`
2. `npm install`
3. `npm run build`

By default, the admin JS and CSS will be output to `assets/dist/`


## Notion sync

Country, commitment, disclosure regime and impact data all come from Notion
databases. An external cron runs one management command:

```
manpy sync_notion
```

Useful flags: `--dry-run` fetches and validates without writing, `--force`
updates rows Notion has not touched, and `--only` limits the run to named
syncers (`countries`, `commitments`, `regimes`, `regimes_sub`, `impact`).

Each row schema declares the Notion columns it reads in `PROPERTIES`. The sync
checks those columns are still there before writing anything, and skips that
database with a loud message if any have gone. Without that check a renamed
column would decode to an empty value rather than an error, so the sync would
blank every field behind it and report success.

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


## Continuous Integration

Pushes to the `staging` branch are automatically deployed, including static assets, to the staging server.


## Build docker cache image

```
docker buildx bake -f docker-compose.test.yml web --set web.platform=linux/amd64,linux/arm64 --push
```
