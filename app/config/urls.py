# 3rd party
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponse
from django.urls import path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

# Module
from .views import (
    robots, error_400_view, error_403_view, error_404_test, error_404_view, error_500_view
)
from modules.taxonomy.views import FocusAreaView, SectorView, PublicationTypeView
from modules.content.views import CountryView, SearchView


urlpatterns = [
    # Django and Wagtail views
    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^404/$', error_404_test, ),
    url(r'^500/$', error_500_view, ),
    # Server / Robots / Verification etc
    url(r'^robots\.txt$', robots),
    url(r'^sitemap\.xml$', sitemap, {'template_name': 'sitemap.xml.html'}),
    url(r'^googleverfication\.html$',
        lambda r: HttpResponse(
            "google-site-verification: foo.html", content_type="text/plain")),
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
    path(
        '<slug:section_slug>/focus-areas/<str:tag_slug>/',
        FocusAreaView.as_view(),
        name="focusarea-tag"
    ),
    path(
        '<slug:section_slug>/sectors/<str:tag_slug>/',
        SectorView.as_view(),
        name="sector-tag"
    ),
    path(
        '<slug:section_slug>/types/<str:tag_slug>/',
        PublicationTypeView.as_view(),
        name="publicationtype-category"
    ),
    path('impact/country/<str:slug>/', CountryView.as_view(), name="country-tag"),
    path("search/", SearchView.as_view(), name="search"),
    url(r'', include(wagtail_urls)),
)
