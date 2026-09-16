# 3rd party
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

# Module
from modules.notion.models import (
    DataUserTag,
    ImpactEntry,
    ImpactTypeTag,
    PolicyAreaTag,
    ResourceTypeTag,
    UsabilityThemeTag,
)

VOCABULARIES = [DataUserTag, PolicyAreaTag, UsabilityThemeTag, ImpactTypeTag, ResourceTypeTag]


@pytest.fixture
def admin(client):
    user = get_user_model().objects.create_superuser(
        "tagadmin@example.com",
        "notarealpassword",
    )
    client.force_login(user)
    return client


def index_url(model):
    return reverse(f"notion_{model._meta.model_name}_modeladmin_index")


def create_url(model):
    return reverse(f"notion_{model._meta.model_name}_modeladmin_create")


####################################################################################################
# Vocabularies
####################################################################################################


@pytest.mark.parametrize("model", VOCABULARIES)
def test_vocabulary_listing_renders(admin, model):
    model.objects.create(name="AML/CFT")

    response = admin.get(index_url(model))

    assert response.status_code == 200
    assert b"AML/CFT" in response.content


@pytest.mark.parametrize("model", VOCABULARIES)
def test_vocabulary_cannot_be_added_to(admin, model):
    """The sync rebuilds these from Notion, so editing here would be undone."""
    response = admin.get(create_url(model))

    assert response.status_code != 200


def test_vocabulary_listing_shows_how_many_entries_use_a_tag(admin):
    tag = PolicyAreaTag.objects.create(name="Corruption")
    for index in range(3):
        entry = ImpactEntry.objects.create(notion_id=f"e{index}", description=f"Entry {index}")
        entry.policy_areas.add(tag)

    response = admin.get(index_url(PolicyAreaTag))

    assert response.status_code == 200
    assert b"Corruption" in response.content


####################################################################################################
# Entries
####################################################################################################


def test_impact_entry_listing_renders(admin):
    ImpactEntry.objects.create(
        notion_id="e1",
        description="Kenyan FIU used BO data in an investigation",
        year=2024,
    )

    response = admin.get(index_url(ImpactEntry))

    assert response.status_code == 200
    assert b"Kenyan FIU used BO data" in response.content


def test_impact_entries_cannot_be_added_by_hand(admin):
    response = admin.get(create_url(ImpactEntry))

    assert response.status_code != 200
