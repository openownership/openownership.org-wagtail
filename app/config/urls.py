# 3rd party
from django.conf import settings
from django.http import HttpResponse
from wagtail.core import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from django.conf.urls import url, include
from wagtail.documents import urls as wagtaildocs_urls
from django.conf.urls.static import static
from wagtail.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Module
from .views import (
    robots, error_400_view, error_403_view, error_404_test, error_404_view, error_500_view
)


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
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


handler400 = error_400_view
handler403 = error_403_view
handler404 = error_404_view
handler500 = error_500_view

urlpatterns += [
    url(r'', include(wagtail_urls)),
]
