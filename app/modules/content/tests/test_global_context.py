import pytest

from helpers import context as context_helpers

pytestmark = pytest.mark.django_db


def _break_site_lookup(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("connection already closed")

    monkeypatch.setattr(context_helpers.Site.objects, "get", boom)


def test_global_context_keeps_existing_keys_when_lookup_fails(monkeypatch):
    _break_site_lookup(monkeypatch)
    page = object()

    ctx = context_helpers.global_context({"page": page, "self": page})

    assert ctx["page"] is page
    assert ctx["self"] is page


def test_global_context_does_not_share_state_between_calls():
    first = context_helpers.global_context()
    first["leak"] = True

    assert "leak" not in context_helpers.global_context()
