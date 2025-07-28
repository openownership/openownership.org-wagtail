# 3rd party
from benzo.urls import urlpatterns as benzo_urls
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse
from django.urls import path, re_path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from modules.content.views import CountryView, RegionView, SearchView

# Module
from modules.core.views import (
    error_400_view,
    error_403_view,
    error_404_test,
    error_404_view,
    error_500_view,
    robots,
)
from modules.notion.views import CountriesExport, CountryExport, serve_csv_file

urlpatterns = [
    # Django and Wagtail views
    re_path(r"^admin/", include(wagtailadmin_urls)),
    path("django-admin/", admin.site.urls),
    re_path(r"^documents/", include(wagtaildocs_urls)),
    path("benzo/", include(benzo_urls)),
    re_path(r"^404/$", error_404_test),
    re_path(r"^500/$", error_500_view),
    # Server / Robots / Verification etc
    re_path(r"^robots\.txt$", robots),
    re_path(r"^sitemap\.xml$", sitemap),
    re_path(
        r"^googleverfication\.html$",
        lambda r: HttpResponse(  # noqa: ARG005
            "google-site-verification: foo.html",
            content_type="text/plain",
        ),
    ),
    path("metadata.csv", serve_csv_file, name="serve_metadata"),
]

if settings.DEBUG:
    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler400 = error_400_view
handler403 = error_403_view
handler404 = error_404_view
handler500 = error_500_view

urlpatterns = urlpatterns + i18n_patterns(
    path("map/country/<str:slug>/", CountryView.as_view(), name="country-tag"),
    path("map/country/<str:slug>.csv", CountryExport.as_view(), name="country-export"),
    path("map/region/<str:slug>/", RegionView.as_view(), name="region"),
    path("map/oo_all_country_data.csv", CountriesExport.as_view(), name="countries-export"),
    path("search/", SearchView.as_view(), name="search"),
    re_path(r"", include(wagtail_urls)),
)
