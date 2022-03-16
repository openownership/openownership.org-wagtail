import pytest

from django.test import Client


pytestmark = pytest.mark.django_db

client = Client()


def test_card_blurb(team_profile_page):
    "card_blurb should use the role"
    team_profile_page.blurb = "My blurb"
    team_profile_page.role = "My role"
    assert team_profile_page.card_blurb == "My role"
