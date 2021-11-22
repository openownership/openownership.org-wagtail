# Meta: Setup

Firstly, set all this stuff up and make a note of all the API tokens:

1. AWS/Spaces
2. Bugsnag
3. Postmark


Then you'll probably need to replace the contents of `poetry.lock` with this:

```
[metadata]
lock-version = "1.0"
python-versions = ">=3.6,<3.9"
```

Other helpful stuff to get started after you've run `gofab`:

* `fab envkey.variables` gets you setup with Envkey defaults
* `fab utils.make_key` will generate deploy keys - if you've set up a `DEPLOY_USER_PASSWORD` in the step above and it's in your terminal session it will use that by default

Then you can delete everything above and use the below for your Readme

---

# openownership.org

This is a Wagtail site.


# First run

You'll probably want to do `sudo nano /etc/hosts` and add:

`0.0.0.0    openownership.org.test`

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


Site should now be accessible at `http://openownership.org.test:5000` (or http://0.0.0.0.test:5000)


# Static assets

1. `cd app/asset/`
2. `npm install`
3. `npm run build`

By default, the admin JS and CSS will be output to `assets/dist/`
