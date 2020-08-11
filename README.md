# Meta: Setup

You'll want to find/replace the following variables across the project before starting

* `TEMPLATEPROJECT_FULL_NAME` - ie. "London Anti-Fascists Alliance"
* `TEMPLATEPROJECT_SHORT_NAME` - ie. "lafa"
* `TEMPLATEPROJECT_DOMAIN` - ie. "londonantifa.org.uk"
* `TEMPLATEPROJECT_REPO` - ie. "git@github.com:hactar-is/londonantifa.org.uk.git"

Then you can delete everything above and use the below for your Readme

---

# TEMPLATEPROJECT_FULL_NAME

This is a Wagtail site.


# First run

You'll probably want to do `sudo nano /etc/hosts` and add:

`0.0.0.0    TEMPLATEPROJECT_SHORT_NAME.test`

1. `git submodule update --init --recursive`
2. `goenv`
3. `gofab` (and then probably `cd ..`)
4. `docker-compose up --build -d`
5. `fab docker.fish`
6. `manpy migrate`
7. `manpy site_scaffold`
8. `manpy createsuperuser`
9. `runserver`

Site should now be accessible at `http://TEMPLATEPROJECT_SHORT_NAME.test:5000` (or http://0.0.0.0.test:5000)


# Static assets

1. `cd app/asset/`
2. `npm install`
3. `npm run build`

By default, the admin JS and CSS will be output to `assets/dist/`
