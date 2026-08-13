"""Tests for how Django is told about the TLS proxy in front of it.

Caddy terminates TLS and proxies to Django over plain http, so without being
told, Django treats every request as insecure. That is not cosmetic: it writes
`http://` links into anything built with `build_absolute_uri`, and it makes
`SECURE_SSL_REDIRECT` impossible to enable without an endless redirect loop.
"""

from django.test import RequestFactory, override_settings

from config.settings import remote

EXPECTED = ("HTTP_X_FORWARDED_PROTO", "https")

factory = RequestFactory()


####################################################################################################
# The setting itself
####################################################################################################


def test_the_proxy_header_is_trusted_where_a_proxy_is_in_front():
    """`remote` is imported by production and staging, the two environments
    behind Caddy.
    """
    assert remote.SECURE_PROXY_SSL_HEADER == EXPECTED


def test_the_proxy_header_is_not_trusted_by_default():
    """Local development and the tests have nothing in front of Django, so
    trusting this header there would let anyone claim their request was secure.
    """
    from django.conf import settings

    assert getattr(settings, "SECURE_PROXY_SSL_HEADER", None) is None


####################################################################################################
# What it changes
####################################################################################################


@override_settings(SECURE_PROXY_SSL_HEADER=EXPECTED)
def test_a_forwarded_request_is_seen_as_secure():
    request = factory.get("/", headers={"x-forwarded-proto": "https"})

    assert request.is_secure() is True
    assert request.build_absolute_uri("/en/evidence.csv").startswith("https://")


@override_settings(SECURE_PROXY_SSL_HEADER=EXPECTED)
def test_a_request_without_the_header_is_still_insecure():
    request = factory.get("/")

    assert request.is_secure() is False


@override_settings(SECURE_PROXY_SSL_HEADER=EXPECTED)
def test_a_forwarded_plain_http_request_is_still_insecure():
    request = factory.get("/", headers={"x-forwarded-proto": "http"})

    assert request.is_secure() is False
