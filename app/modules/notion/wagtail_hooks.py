"""
    notion.wagtail_hooks

    Adds the Notion menu to the Wagtail sidebar
"""

# Wagtail
from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register
)

from .models import Commitment, DisclosureRegime, CountryTag, CoverageScope, Region


class ReadOnlyPermissionHelper(PermissionHelper):

    def user_can_list(self, user):
        return True

    def user_can_edit_obj(self, user, obj):
        return False

    def user_can_delete_obj(self, user, obj):
        return False

    def user_can_create(self, user):
        return False


################################################################################
# ModelAdmin
################################################################################


class CountryTagModelAdmin(ModelAdmin):
    model = CountryTag
    menu_order = 100
    menu_icon = 'site'
    add_to_settings_menu = True
    list_display = ('name', )
    search_fields = ('name', )
    list_filter = ('archived', 'oo_support', )
    prepopulated_fields = {"slug": ("name",)}
    inspect_view_enabled = True


class RegionModelAdmin(ModelAdmin):
    model = Region
    menu_order = 150
    menu_icon = 'site'
    add_to_settings_menu = True
    list_display = ('name', )
    search_fields = ('name', )
    prepopulated_fields = {"slug": ("name",)}


class CommitmentModelAdmin(ModelAdmin):
    model = Commitment
    menu_order = 200
    menu_icon = 'fa-link'
    add_to_settings_menu = True
    list_display = ('country', )
    search_fields = ('country', )
    list_filter = ('country', )
    inspect_view_enabled = True
    permission_helper_class = ReadOnlyPermissionHelper


class DisclosureRegimeModelAdmin(ModelAdmin):
    model = DisclosureRegime
    menu_order = 300
    menu_icon = 'fa-link'
    add_to_settings_menu = True
    list_display = ('title', )
    search_fields = ('title', )
    list_filter = ('title', )
    inspect_view_enabled = True
    permission_helper_class = ReadOnlyPermissionHelper


class CoverageScopeModelAdmin(ModelAdmin):
    model = CoverageScope
    menu_order = 300
    menu_icon = 'fa-link'
    add_to_settings_menu = True
    list_display = ('name', )
    search_fields = ('name', )
    list_filter = ('name', )
    inspect_view_enabled = True
    permission_helper_class = ReadOnlyPermissionHelper


################################################################################
# Wagtail Menu customisation
################################################################################


class NotionAdminGroup(ModelAdminGroup):
    menu_label = 'Notion'
    menu_icon = 'fa-sticky-note'
    menu_order = 1000
    items = (
        CountryTagModelAdmin,
        RegionModelAdmin,
        CommitmentModelAdmin,
        DisclosureRegimeModelAdmin,
        CoverageScopeModelAdmin,
    )


modeladmin_register(NotionAdminGroup)
