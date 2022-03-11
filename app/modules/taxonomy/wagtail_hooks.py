"""
    taxonomy.wagtail_hooks

    Adds the Taxonomy menu to the Wagtail sidebar
"""

# Wagtail
from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, ModelAdminGroup, modeladmin_register
)


from modules.taxonomy.models import (
    PublicationType, FocusAreaTag, SectorTag, SectionTag
)


################################################################################
# ModelAdmin
################################################################################


class PublicationTypeModelAdmin(ModelAdmin):
    model = PublicationType
    menu_order = 100
    menu_icon = 'tag'
    add_to_settings_menu = True
    list_display = ('name', )
    search_fields = ('name', )
    prepopulated_fields = {"slug": ("name",)}


class FocusAreaTagModelAdmin(ModelAdmin):
    model = FocusAreaTag
    menu_order = 200
    menu_icon = 'tag'
    add_to_settings_menu = True
    list_display = ('name', )
    search_fields = ('name', )
    prepopulated_fields = {"slug": ("name",)}


class SectorTagModelAdmin(ModelAdmin):
    model = SectorTag
    menu_order = 200
    menu_icon = 'tag'
    add_to_settings_menu = True
    list_display = ('name', )
    search_fields = ('name', )
    prepopulated_fields = {"slug": ("name",)}


class SectionTagModelAdmin(ModelAdmin):
    model = SectionTag
    menu_order = 300
    menu_icon = 'tag'
    add_to_settings_menu = True
    list_display = ('name', )
    search_fields = ('name', )
    prepopulated_fields = {"slug": ("name",)}


################################################################################
# Wagtail Menu customisation
################################################################################


class TaxonomyAdminGroup(ModelAdminGroup):
    menu_label = 'Taxonomy'
    menu_icon = 'tag'
    menu_order = 900
    items = (
        PublicationTypeModelAdmin,
        FocusAreaTagModelAdmin,
        SectorTagModelAdmin,
        SectionTagModelAdmin
    )


modeladmin_register(TaxonomyAdminGroup)
