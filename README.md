# openownership.org

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/20145b7e6389409fa98ec02be4fe5b1b)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=hactar-is/openownership.org&amp;utm_campaign=Badge_Grade) [![Codacy Badge](https://app.codacy.com/project/badge/Coverage/20145b7e6389409fa98ec02be4fe5b1b)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=hactar-is/openownership.org&utm_campaign=Badge_Coverage)

This is a Wagtail site.

[Sprint planner](https://github.com/orgs/openownership/projects/13)


### If you don't have access to Hactar tooling...

You'll need all the project's environment variables in a .env file expanded into the shell session.

1. `docker compose up --build -d`
2. `docker exec -it openownership_web_1 fish` or `docker exec -it openownership_web_1 zsh` depending on your preference

### Once you have a shell inside the web container

1. `manpy migrate`
2. `manpy createsuperuser`
3. `manpy populate_taxonomies`  # To create tags
4. `manpy sync_notion`  # Sync data from Notion
5. `manpy index_evidence`  # Update the custom search index used on BOT Evidence Centre
6. `manpy update_index`  # Update the search index
6. `runserver`

Site should now be accessible at `https://openownership.test` (or http://127.0.0.1:5000)

The https domain is provided by localias which is managed by `mise`.

## Static assets

1. `cd app/asset/`
2. `npm install`
3. `npm run build`

By default, the admin JS and CSS will be output to `assets/dist/`


## Continuous Integration

Pushes to the `staging` branch are automatically deployed, including static assets, to the staging server.


## Build docker cache image

```
docker buildx bake -f docker-compose.test.yml web --set web.platform=linux/amd64,linux/arm64 --push
```
