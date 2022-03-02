# openownership.org

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/20145b7e6389409fa98ec02be4fe5b1b)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=hactar-is/openownership.org&amp;utm_campaign=Badge_Grade) [![Codacy Badge](https://app.codacy.com/project/badge/Coverage/20145b7e6389409fa98ec02be4fe5b1b)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=hactar-is/openownership.org&utm_campaign=Badge_Coverage)

This is a Wagtail site.


## First run

You'll probably want to do `sudo nano /etc/hosts` and add:

`0.0.0.0    openownership.test`

### If you have access to the Hactar tooling

Make sure you have developer access to the EnvKey project and generate yourself an EnvKey. Save this to a `.env` file at the root of the project.

1. `git submodule update --init --recursive`
2. `goenv`
3. `gofab` (and then probably `cd ..`)
4. `docker-compose up --build -d`
5. `fab docker.fish` to get a shell inside the running web container


### If you don't have access to Hactar tooling...

You'll need all the project's environment variables in a .env file expanded into the shell session.

1. `docker-compose up --build -d`
2. `docker exec -it openownershiporg_web_1 fish` or `docker exec -it openownershiporg_web_1 zsh` depending on your preference

### Once you have a shell inside the web container

1. `manpy migrate`
2. `manpy createsuperuser`
3. `manpy populate_taxonomies`  # To create tags
3. `runserver`

Site should now be accessible at `http://openownership.org.test:5000` (or http://0.0.0.0.test:5000)

## Static assets

1. `cd app/asset/`
2. `npm install`
3. `npm run build`

By default, the admin JS and CSS will be output to `assets/dist/`


## Continuous Integration

Pushes to the `staging` branch are automatically deployed, including static assets, to the staging server. 
