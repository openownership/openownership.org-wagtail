"""
    notion.wagtail_hooks

    Adds the Notion menu to the Wagtail sidebar
"""

# 3rd party
from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin, ModelAdminGroup, modeladmin_register

# Module
from .models import Region, Commitment, CountryTag, CoverageScope, DisclosureRegime


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
    list_display = ('name', 'icon', 'deleted')
    search_fields = ('name', )
    list_filter = ('archived', 'oo_support', 'deleted')
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
    list_display = (
        'country', 'commitment_type_name', 'central_register', 'public_register', 'deleted'
    )
    search_fields = ('country__name', )
    list_filter = ('commitment_type_name', 'central_register', 'public_register', 'deleted')
    inspect_view_enabled = True
    permission_helper_class = ReadOnlyPermissionHelper


class DisclosureRegimeModelAdmin(ModelAdmin):
    model = DisclosureRegime
    menu_order = 300
    menu_icon = 'fa-link'
    add_to_settings_menu = True
    list_display = ('title', 'country', 'stage', 'deleted')
    search_fields = ('title', 'country__name')
    list_filter = ('stage', 'country', 'deleted')
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
