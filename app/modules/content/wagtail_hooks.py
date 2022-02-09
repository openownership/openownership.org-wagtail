from wagtail.contrib.modeladmin.options import (
    ModelAdmin, modeladmin_register
)
from .models import Author



# class NewsCategoryModelAdmin(ModelAdmin):
#     add_to_settings_menu = False
#     list_display = ('name', )
#     search_fields = ('name', )
#     prepopulated_fields = {"slug": ("name",)}
#     menu_order = 400
#     menu_icon = 'tag'
#     menu_label = 'Categories'
#     model = NewsCategory


# modeladmin_register(NewsCategoryModelAdmin)


class AuthorModelAdmin(ModelAdmin):
    "Add 'Authors' item to admin sidebar"
    model = Author
    menu_icon = 'fa-user'
    list_display = ('name',)
    ordering = ('name',)
