"""
notion.wagtail_hooks

Adds the Notion menus to the Wagtail sidebar
"""

# 3rd party
from django.utils.translation import gettext_lazy as _
from wagtail_modeladmin.helpers import PermissionHelper
from wagtail_modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

# Module
from .models import (
    Commitment,
    CountryTag,
    CoverageScope,
    DataUserTag,
    DisclosureRegime,
    ImpactEntry,
    ImpactTypeTag,
    PolicyAreaTag,
    Region,
    ResourceTypeTag,
    UsabilityThemeTag,
)


class ReadOnlyPermissionHelper(PermissionHelper):
    def user_can_list(self, user):  # noqa: ARG002
        return True

    def user_can_edit_obj(self, user, obj):  # noqa: ARG002
        return False

    def user_can_delete_obj(self, user, obj):  # noqa: ARG002
        return False

    def user_can_create(self, user):  # noqa: ARG002
        return False


################################################################################
# ModelAdmin
################################################################################


class CountryTagModelAdmin(ModelAdmin):
    model = CountryTag
    menu_order = 100
    menu_icon = "site"
    add_to_settings_menu = True
    list_display = ("name", "icon", "deleted")
    search_fields = ("name",)
    list_filter = ("archived", "oo_support", "deleted")
    prepopulated_fields = {"slug": ("name",)}
    inspect_view_enabled = True


class RegionModelAdmin(ModelAdmin):
    model = Region
    menu_order = 150
    menu_icon = "site"
    add_to_settings_menu = True
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class CommitmentModelAdmin(ModelAdmin):
    model = Commitment
    menu_order = 200
    menu_icon = "link"
    add_to_settings_menu = True
    list_display = (
        "country",
        "commitment_type_name",
        "central_register",
        "public_register",
        "deleted",
    )
    search_fields = ("country__name",)
    list_filter = ("commitment_type_name", "central_register", "public_register", "deleted")
    inspect_view_enabled = True
    permission_helper_class = ReadOnlyPermissionHelper


class DisclosureRegimeModelAdmin(ModelAdmin):
    model = DisclosureRegime
    menu_order = 300
    menu_icon = "link"
    add_to_settings_menu = True
    list_display = ("title", "country", "stage", "deleted")
    search_fields = ("title", "country__name")
    list_filter = ("stage", "country", "deleted")
    inspect_view_enabled = True
    permission_helper_class = ReadOnlyPermissionHelper


class CoverageScopeModelAdmin(ModelAdmin):
    model = CoverageScope
    menu_order = 300
    menu_icon = "link"
    add_to_settings_menu = True
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)
    inspect_view_enabled = True
    permission_helper_class = ReadOnlyPermissionHelper


class ImpactEntryModelAdmin(ModelAdmin):
    model = ImpactEntry
    menu_order = 400
    menu_icon = "doc-full"
    add_to_settings_menu = True
    list_display = ("description", "year", "publish", "tangible_impact", "deleted")
    search_fields = ("description", "summary", "lessons")
    list_filter = ("publish", "year", "tangible_impact", "international", "deleted")
    inspect_view_enabled = True
    permission_helper_class = ReadOnlyPermissionHelper


################################################################################
# Impact tracker vocabularies
################################################################################


class ImpactTagModelAdmin(ModelAdmin):
    """Listing for one of the impact tracker's multi-select vocabularies.

    These are read-only on purpose. Every sync rebuilds them from Notion by
    matching on name, so a name edited here would be recreated under its old
    name on the next run and the edited one left behind with nothing pointing
    at it. Tidying an option list has to happen in Notion.
    """

    menu_icon = "tag"
    add_to_settings_menu = True
    list_display = ("name", "slug", "entry_count")
    search_fields = ("name",)
    inspect_view_enabled = True
    permission_helper_class = ReadOnlyPermissionHelper

    def entry_count(self, obj):
        return obj.impact_entries.count()

    entry_count.short_description = _("Entries")


class DataUserModelAdmin(ImpactTagModelAdmin):
    model = DataUserTag
    menu_order = 100


class PolicyAreaModelAdmin(ImpactTagModelAdmin):
    model = PolicyAreaTag
    menu_order = 200


class UsabilityThemeModelAdmin(ImpactTagModelAdmin):
    model = UsabilityThemeTag
    menu_order = 300


class ImpactTypeModelAdmin(ImpactTagModelAdmin):
    model = ImpactTypeTag
    menu_order = 400


class ResourceTypeModelAdmin(ImpactTagModelAdmin):
    model = ResourceTypeTag
    menu_order = 500


################################################################################
# Wagtail Menu customisation
################################################################################


class NotionAdminGroup(ModelAdminGroup):
    menu_label = "Notion"
    menu_icon = "globe"
    menu_order = 1000
    items = (
        CountryTagModelAdmin,
        RegionModelAdmin,
        CommitmentModelAdmin,
        DisclosureRegimeModelAdmin,
        CoverageScopeModelAdmin,
        ImpactEntryModelAdmin,
    )


class ImpactVocabularyAdminGroup(ModelAdminGroup):
    menu_label = "Impact tags"
    menu_icon = "tag"
    menu_order = 1010
    items = (
        DataUserModelAdmin,
        PolicyAreaModelAdmin,
        UsabilityThemeModelAdmin,
        ImpactTypeModelAdmin,
        ResourceTypeModelAdmin,
    )


modeladmin_register(NotionAdminGroup)
modeladmin_register(ImpactVocabularyAdminGroup)
