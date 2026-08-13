# -*- coding: utf-8 -*-

"""
Django settings for the openownership.org project.
"""

import os
from pathlib import Path

import arrow
from django.utils.translation import gettext_lazy as _
from loguru import logger as guru
from phaser import secrets  # noqa

SHELL_PLUS = "ipython"
PROJECT_DIR_NAME = "app"
BENZO_API_KEY = os.environ.get("BENZO_API_KEY", "")

DJANGO_ROOT = Path("./").resolve()

MONTH_IN_SECONDS = 2628000

TIME_IN_A_YEAR = arrow.now().shift(years=+1).datetime


guru.add(
    "/var/log/openownership.org/output.log",
    rotation="100 MB",
    backtrace=True,
    retention="30 days",
    compression="zip",
    level="WARNING",
)

guru.add(
    "/var/log/openownership.org/notion.log",
    filter="modules.notion",
    rotation="100 MB",
    backtrace=True,
    retention="30 days",
    compression="zip",
    level="WARNING",
)


WHITENOISE_MANIFEST_STRICT = False

WAGTAILEMBEDS_RESPONSIVE_HTML = True


# Tell the stats module to store view counts in Redis
STATS_USE_REDIS = True

TESTING = False

CSRF_USE_SESSIONS = True
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1500

####################################################################################################
# Statham SEO
####################################################################################################

STATHAM_SEO = {
    # Feature switches
    "ENABLE_META_TAGS": True,
    "ENABLE_TITLE": True,  # emit the <title> tag (off = the project owns it)
    "ENABLE_OPENGRAPH": True,
    "ENABLE_TWITTER_CARDS": True,
    "ENABLE_JSON_LD": True,
    "USE_GRAPH": True,  # one @graph vs. separate <script> blocks
    "STRICT_VALIDATION": None,  # None = raise in DEBUG, drop-and-log in production
    # Defaults & formatting
    "DEFAULT_TITLE_FORMAT": "{page} | {site_name}",
    "TITLE_OVERRIDE": "title_override",  # context var that overrides the title verbatim
    "DEFAULT_OG_TYPE": "website",
    "DEFAULT_TWITTER_CARD": "summary_large_image",
    "IMAGE_RENDITION_SPEC": "fill-1200x630",
    # Code-level Organization defaults - used before anything is set in the admin
    "ORGANIZATION_DEFAULTS": {"name": "Open Ownership"},
    # Site-data sourcing (see below)
    "SITE_SOURCE": "config.seo.ProjectSeoSource",
    # "MANAGED_ELSEWHERE": ["social_profiles", "default_image", "default_description"],
}


####################################################################################################
# Feature Flags
####################################################################################################


FFLAGS = {
    "legislation": False,
}


####################################################################################################
# I18N
####################################################################################################


WAGTAIL_I18N_ENABLED = True
LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/London"
USE_L10N = True
USE_I18N = True
USE_TZ = True

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ("en", _("English")),
    ("fr", _("French")),
    ("es", _("Spanish")),
    ("id", _("Bahasa Indonesia")),
    ("de", _("German")),
    ("ru", _("Russian")),
    ("hy", _("Armenian")),
    ("mn", _("Mongolian")),
    ("uk", _("Ukrainian")),
]


LOCALE_PATHS = (
    Path(DJANGO_ROOT) / "locale",
    Path(DJANGO_ROOT) / "locale_extra",
)

####################################################################################################
# Installed Apps
####################################################################################################

DJANGO_APPS = [
    "whitenoise.runserver_nostatic",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sitemaps",
    "rest_framework",
    "django_extensions",
    "modelcluster",
    "taggit",
    "storages",
    "django.contrib.staticfiles",
    "dbbackup",
    "cacheops",
]

WAGTAIL_APPS = [
    "wagtailautocomplete",
    "wagtailcache",
    "wagtail.api.v2",
    "wagtail.contrib.redirects",
    "wagtail.embeds",
    "wagtail.sites",
    "wagtail.users",
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.search.backends.database",
    "wagtail.admin",
    "wagtail",
    "wagtail_localize",
    "wagtail.locales",
    "wagtail.contrib.forms",
    "wagtail_modeladmin",
    "wagtail.contrib.settings",
    "wagtail.contrib.table_block",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.search_promotions",
    # Enable styleguide to see icons available for use in blocks etc:
    "wagtail.contrib.styleguide",
    "wagtailfontawesomesvg",
    "wagtailmodelchooser",
    "wagtools",
    "wagtail_meilisearch",
    "statham",
]

SITE_APPS = [
    "modules.cli",
    "modules.content",
    "modules.core",
    "modules.feedback",
    "modules.notion",
    "modules.settings",
    "modules.stats",
    "modules.taxonomy",
    "modules.users",
]

INSTALLED_APPS = DJANGO_APPS + WAGTAIL_APPS + SITE_APPS


####################################################################################################
# Middleware
####################################################################################################

MIDDLEWARE = [
    "modules.stats.middleware.ViewCountMiddleware",
    "middleware.csrf.CSRFCookieMiddleware",
    "wagtailcache.cache.UpdateCacheMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "middleware.devpanel.DebugMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # 'django.middleware.locale.LocaleMiddleware',
    "middleware.locale.LocaleMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
    "wagtailcache.cache.FetchFromCacheMiddleware",
]


####################################################################################################
# Core Django config
####################################################################################################

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
BASE_URL = "https://openownership.org"
WAGTAILADMIN_BASE_URL = "https://openownership.org"

# Whether a reader's search term is sent to Plausible alongside the search count.
# Open Ownership were asked, because it is a privacy call rather than a technical
# one (A-S6 in the sprint brief), and chose to record them: what people search
# for and do not find is the most useful thing this tool can report. The term is
# already capped and trimmed by `evidence.parse` before it reaches the page.
# Search counts are unaffected if this is turned back off.
EVIDENCE_RECORD_SEARCH_TERMS = True
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
INTERNAL_IPS = ["127.0.0.1"]
APPEND_SLASH = True
AUTH_USER_MODEL = "users.User"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"


################################################################################
# Django DB Backup
################################################################################

now = arrow.now()
month = now.format("MM")

server_env = os.environ.get("SERVER_ENV", "dev")


def backup_filename(databasename, servername, datetime, extension, content_type):  # noqa: ARG001
    return f"{server_env}-{datetime}.{extension}"


DBBACKUP_GPG_ALWAYS_TRUST = True
DBBACKUP_GPG_RECIPIENT = "Hactar"
DBBACKUP_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
DBBACKUP_FILENAME_TEMPLATE = backup_filename
DBBACKUP_STORAGE_OPTIONS = {
    "access_key": os.environ.get("BACKUPS_AWS_ACCESS_KEY_ID", ""),
    "secret_key": os.environ.get("BACKUPS_AWS_SECRET_ACCESS_KEY", ""),
    "bucket_name": "hactar-backups",
    "region_name": "eu-west-1",
    "location": f"postgres/openownership/{now.year}/{month}/",
    "default_acl": "private",
    "endpoint_url": "https://s3-eu-west-1.amazonaws.com",
}

# Check the path to python and add this to cron...
# 0 3 * * * (/srv/www/app/.venv/bin/python /srv/www/app/manage.py dbbackup -ezq --noinput) &>> /var/log/cronjob.log  # NOQA

# Or run it manually...
# manpy dbbackup -ezq --noinput


####################################################################################################
# Database
####################################################################################################

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", 5432),
    },
}

REDIS_CONNECTION = "redis://{}:6379/0".format(os.environ.get("REDIS_HOST"))


####################################################################################################
# Cache
####################################################################################################

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
WAGTAIL_CACHE = True
WAGTAIL_CACHE_BACKEND = "wagtailcache"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/0",
    },
    "wagtailcache": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:6379/1",
        "TIMEOUT": 60 * 60 * 24 * 7,
    },
}

CACHEOPS_REDIS = {
    "host": os.environ.get("REDIS_HOST"),
    "port": 6379,
    "db": 2,
    "socket_timeout": 3,
    "password": os.environ.get("REDIS_PASSWORD", None),
}


CACHEOPS = {
    "users.User": {"ops": "all", "timeout": 60 * 60},
    "auth.Group": {"ops": "all", "timeout": 60 * 60},
    "core.SiteImage": {"ops": "all", "timeout": 60 * 60},
    "core.SiteimageRendition": {"ops": "all", "timeout": 60 * 60},
    "migrations.*": {"ops": (), "timeout": 0},
    "*.*": {"ops": (), "timeout": 60 * 60},
}

CACHEOPS_ENABLED = True
CACHEOPS_DEGRADE_ON_FAILURE = True


####################################################################################################
# Search
####################################################################################################

WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail_meilisearch.backend",
        "HOST": os.environ.get("MEILISEARCH_HOST"),
        "PORT": os.environ.get("MEILISEARCH_PORT"),
        "MASTER_KEY": os.environ.get("MEILI_MASTER_KEY", ""),
        "QUERY_LIMIT": 1000,
    },
}


####################################################################################################
# Template
####################################################################################################

JINJA2_EXTENSIONS = [
    "wagtail.jinja2tags.core",
    "wagtail.admin.jinja2tags.userbar",
    "wagtail.images.jinja2tags.images",
    "jinja2.ext.i18n",
    "wagtail.contrib.settings.jinja2tags.settings",
    "config.template.TemplateGlobalsExtension",
    "jinja2.ext.do",
    "jinja2.ext.loopcontrols",
    "cacheops.jinja2.cache",
    "statham.jinja2.SEOExtension",
]

DEFAULT_JINJA2_TEMPLATE_EXTENSION = ".jinja"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [
            Path(DJANGO_ROOT) / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "extensions": JINJA2_EXTENSIONS,
        },
    },
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            Path(DJANGO_ROOT) / "templates" / "django",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.static",
            ],
        },
    },
]


####################################################################################################
# Assets
####################################################################################################

STATIC_ROOT = Path(DJANGO_ROOT / "static")
STATIC_URL = "/static/"

MEDIA_ROOT = Path(DJANGO_ROOT / "media")
MEDIA_URL = "/media/"


STATICFILES_DIRS = [
    Path(DJANGO_ROOT) / "assets" / "dist",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]


STORAGES = {
    "default": {
        "BACKEND": "utils.storages.CDNNGOStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


####################################################################################################
# AWS
####################################################################################################

AWS_HEADERS = {
    "Expires": TIME_IN_A_YEAR.strftime("%a, %d %b %Y %H:%M:%S"),
    "Cache-Control": "max-age=2628000",
}

AWS_S3_OBJECT_PARAMETERS = {
    "Expires": TIME_IN_A_YEAR.strftime("%a, %d %b %Y %H:%M:%S"),
    "CacheControl": "max-age=2628000",
}

# AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY']
# AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_KEY']
# AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_BUCKET')
# AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL')


AWS_ACCESS_KEY_ID = os.environ.get("CDNNGO_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.environ.get("CDNNGO_SECRET_KEY")
AWS_STORAGE_BUCKET_NAME = os.environ.get("CDNNGO_BUCKET")
AWS_S3_ENDPOINT_URL = os.environ.get("CDNNGO_ENDPOINT")


AWS_S3_FILE_OVERWRITE = False
AWS_IS_GZIPPED = True
AWS_S3_SECURE_URLS = True
AWS_PRELOAD_METADATA = False
AWS_DEFAULT_ACL = "public-read"

####################################################################################################
# Email
####################################################################################################

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST_URL", None)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", None)
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", None)
EMAIL_USE_TLS = True
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = ""

WAGTAILADMIN_NOTIFICATION_FROM_EMAIL = "wagtail@openownership.org"


####################################################################################################
# ReCaptcha§
####################################################################################################

RECAPTCHA_PUBLIC_KEY = os.environ.get("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = os.environ.get("RECAPTCHA_PRIVATE_KEY")


####################################################################################################
# Project specific settings
####################################################################################################

WAGTAILMENUS_USE_BACKEND_SPECIFIC_TEMPLATES = True
# AUTH_USER_MODEL = 'users.User'
WAGTAILDOCS_DOCUMENT_MODEL = "core.SiteDocument"
WAGTAILIMAGES_IMAGE_MODEL = "core.SiteImage"
IMAGE_MODEL = WAGTAILIMAGES_IMAGE_MODEL
DOCUMENT_MODEL = "core.SiteDocument"


SITE_NAME = "openownership.org"
WAGTAIL_SITE_NAME = SITE_NAME

slideshare = {
    "endpoint": "https://www.slideshare.net/api/oembed/2",
    "urls": [
        "^http[s]?://www\\.slideshare\\.net/.+$",
    ],
}

soundcloud = {
    "endpoint": "https://soundcloud.com/oembed",
    "urls": [
        "^https://(?:m\\.)?soundcloud\\.com/[^#?/]+/.+$",
    ],
}

WAGTAILEMBEDS_FINDERS = [
    {
        "class": "wagtail.embeds.finders.oembed",
        "providers": [slideshare, soundcloud],
    },
    {
        "class": "wagtail.embeds.finders.oembed",
    },
]

DEFAULT_OBJECTS_PER_PAGE = 20

CSRF_COOKIE_HTTPONLY = True

ERROR_400_TEMPLATE_NAME = "errors/500.html"
ERROR_404_TEMPLATE_NAME = "errors/404.html"
ERROR_500_TEMPLATE_NAME = "errors/500.html"

PRIVATE_FOLDER = "/srv/private/"

THEME_CHOICES = []

ICON_CHOICES = []

SOCIAL_MEDIA_CHOICES = [
    "Facebook",
    "Twitter",
    "LinkedIn",
    "GitHub",
]


# Which features do we allow in which kinds of richtext fields?
RICHTEXT_INLINE_FEATURES = [
    "bold",
    "italic",
    "small",
    "link",
    "document-link",
]

RICHTEXT_BODY_FEATURES = [
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "bold",
    "italic",
    "small",
    "ol",
    "ul",
    "link",
    "document-link",
]

RICHTEXT_SUMMARY_FEATURES = [
    "bold",
    "italic",
    "small",
    "ol",
    "ul",
    "link",
    "document-link",
]

FONTAWESOME_ICONS = [
    "solid/external-link-square-alt.svg",
    "solid/th-large.svg",
    "solid/link.svg",
    "solid/columns.svg",
    "solid/file-image.svg",
    "solid/bell.svg",
    "solid/quote-left.svg",
    "solid/money-bill.svg",
    "solid/chart-bar.svg",
    "solid/newspaper.svg",
    "solid/address-card.svg",
    "solid/th.svg",
    "solid/icons.svg",
    "solid/align-left.svg",
    "solid/map-pin.svg",
    "solid/user-check.svg",
    "solid/mail-bulk.svg",
    "solid/sitemap.svg",
    "solid/cogs.svg",
    "solid/hashtag.svg",
    "solid/anchor.svg",
    "solid/clock.svg",
    "solid/sticky-note.svg",
    # 'brands/notion.svg',
    "solid/database.svg",
    "solid/note-sticky.svg",
]


# This gives us a place to put a list of strings that will need translations but may not
# get picked up by makemessages (ie: they might be added through the CMS)

TRANS_STRINGS = [
    # Primary nav
    _("Home"),
    _("Research"),
    _("Implementation"),
    _("Technology"),
    _("Impact"),
    _("Register"),
    _("Search"),
    _("About"),
    # Nested Nav
    _("Publications"),
    _("Reports"),
    _("Briefings"),
    _("Guidance"),
    _("Consultations"),
    _("Other publication categories"),
    _("News"),
    _("Blog"),
    _("Videos"),
    _("Full list"),
    _("Topics"),
    _("Financial Action Task Force"),
    _("Opening Extractives"),
    _("Procurement"),
    _("Private sector"),
    _("Open Ownership Principles"),
    _("Robust definition"),
    _("Comprehensive coverage"),
    _("Sufficient detail"),
    _("A central register"),
    _("Public access"),
    _("Structured data"),
    _("Verification"),
    _("Up to date and auditable"),
    _("Sanctions and enforcement"),
    _("Implementation guide"),
    _("Implementation tools"),
    _("Beneficial ownership disclosure workbook"),
    _("Sample data collection forms"),
    _("Glossary"),
    _("Beneficial Ownership Data Standard"),
    _("Open Ownership Register"),
    _("Technical guidance"),
    _("Technology tools"),
    _("Data analysis notebook and dashboards"),
    _("Data analysis tools"),
    _("Data review tool"),
    _("Data standard feature tracker"),
    _("BODS data generator"),
    _("Data visualiser"),
    _("RDF vocabulary for beneficial ownership data"),
    _("Technology showcases"),
    _("Map"),
    _("Case studies"),
    _("The Beneficial Ownership Leadership Group"),
    _("What is beneficial ownership transparency?"),
    _("What we do"),
    _("Working with us"),
    _("Helpdesk"),
    _("Team"),
    _("Governance"),
    _("Jobs"),
    _("Funding"),
    _("Who funds Open Ownership?"),
    _("Why fund Open Ownership? Why we do the work we do"),
    _("Joining us - what you could support as a partner"),
    # Footer items
    _("Legal"),
    _("Terms"),
    _("Privacy"),
    _("Press mentions"),
    _("Helpdesk"),
    _("Jobs with Open Ownership"),
    _("Contact us"),
    _("Follow us"),
    _("Content rights"),
    _("This work by Open Ownership, unless otherwise noted, is licensed under a"),
    _("Creative Commons Attribution 4.0 International License"),
    # Misc
    _("Open Ownership newsletter"),
    _("Sign up to receive our latest reports, news and updates"),
    _("Sign up"),
]


SLACK_HOOK_WAGBOT = os.environ.get("SLACK_HOOK_WAGBOT")
SLACK_HOOK_NOTIONBOT = os.environ.get("SLACK_HOOK_NOTIONBOT")


####################################################################################################
# Notion sync
####################################################################################################


NOTION_WAGTAIL_TOKEN = os.environ.get("NOTION_WAGTAIL_TOKEN", "")

# Source database ids. These are not secret, so they default to the live values
# and can be overridden per environment.
NOTION_DATABASES = {
    "countries": os.environ.get("NOTION_DB_COUNTRIES", "a7d0fc79-decf-4851-a8f7-8916e23862ba"),
    "commitments": os.environ.get("NOTION_DB_COMMITMENTS", "995e7787-e85f-45df-8fa5-68684f30d16b"),
    "regimes": os.environ.get("NOTION_DB_REGIMES", "85e52f2f-03c5-4d2a-b93f-1acbee5918f1"),
    "regimes_sub": os.environ.get("NOTION_DB_REGIMES_SUB", "4e596712-c912-4821-8ecd-1e272f781d0b"),
    "bot": os.environ.get("NOTION_DB_BOT", "7111bc1e-d10d-4882-8e04-d7f639297c75"),
}

# Rows in the countries database that are not countries. "Global" is used on the
# impact tracker to mean worldwide, so it must never become a country on the
# site; impact entries carry their own `International` flag for that instead.
NOTION_NON_COUNTRY_ROWS = [
    os.environ.get("NOTION_ROW_GLOBAL", "3b2880fb-edf9-80d8-a9b6-c21b95ff791f"),
]
