# Meta: Setup

You'll want to find/replace the following variables across the project before starting

* `TEMPLATEPROJECT_FULL_NAME` - ie. `London Anti-Fascists Alliance`
* `TEMPLATEPROJECT_SHORT_NAME` - ie. `lafa`
* `TEMPLATEPROJECT_DOMAIN` - ie. `londonantifa.org.uk`
* `TEMPLATEPROJECT_REPO` - ie. `git@github.com:hactar-is/londonantifa.org.uk.git`

Then you can delete everything above and use the below for your Readme

---

# TEMPLATEPROJECT_FULL_NAME

This is a Wagtail site.


# First run

You'll probably want to do `sudo nano /etc/hosts` and add:

`0.0.0.0    TEMPLATEPROJECT_SHORT_NAME.test`

If you are setting up from scratch:
`git submodule add git@github.com:hactar-is/fabfile.git fabfile`
`git submodule add git@github.com:hactar-is/ansible-roles.git devops/roles`

If you are working on an existing project:

`git submodule update --init --recursive`

Then...

1. `goenv`
2. `gofab` (and then probably `cd ..`)
3. `docker-compose up --build -d`
4. `fab docker.fish`
5. `manpy migrate`
6. `manpy site_scaffold`
7. `manpy createsuperuser`
8. `runserver`


Site should now be accessible at `http://TEMPLATEPROJECT_SHORT_NAME.test:5000` (or http://0.0.0.0.test:5000)


# Static assets

1. `cd app/asset/`
2. `npm install`
3. `npm run build`

By default, the admin JS and CSS will be output to `assets/dist/`
