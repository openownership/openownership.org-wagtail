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
  usability themes, impact types, resource types, source URL. Order matters,
  since Meilisearch ranks a match in an earlier attribute higher.
* **Filterable**: year, jurisdictions, regions, policy areas, usability themes,
  impact types, resource types. Values within one facet are ORed and the facets
  are ANDed.
* **Sortable**: year, `topic_sort` and `sort_title`. The last two exist only to
  sort on, because a record holds several policy areas and the raw description
  sorts case-sensitively.
* **Default order**: year descending, then topic, then title. Records with no
  policy area come last within their year.

Only entries with `publish` set and not soft-deleted are indexed, and only the
columns Open Ownership mark public in the tracker. Lessons, "OO outputs used in"
and "Presentations/slide decks used in" are deliberately left out: anything in
the index can end up in front of a reader.


## Continuous Integration

Pushes to the `staging` branch are automatically deployed, including static assets, to the staging server.


## Build docker cache image

```
docker buildx bake -f docker-compose.test.yml web --set web.platform=linux/amd64,linux/arm64 --push
```
