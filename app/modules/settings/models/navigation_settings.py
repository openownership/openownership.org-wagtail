# 3rd party
from cacheops import CacheMiss, cache, invalidate_all
from django.conf import settings
from wagtailcache.cache import clear_cache
from wagtail.admin.panels import ObjectList, TabbedInterface
from django.utils.translation import gettext_lazy as _
from wagtail.contrib.settings.models import register_setting

# Module
from .mixins import Footer, NavBar


@register_setting(icon="bars")
class NavigationSettings(NavBar, Footer):

    class Meta:
        verbose_name = _('Navigation settings')

    def build_nav_items(self, block, menu):
        menu.append({
            'type': 'nav_item',
            'value': (block.value.href, block.value.label),
            'page': block.value.get('link_page', None),
        })
        return menu

    def build_nav(self):
        menus = {}
        for nav_menu in self.get_nav_fields():
            menu = menus[nav_menu] = []
            for block in getattr(self, nav_menu):
                if block.block_type == 'mega_menu':
                    self.build_mega_menu(block, menu)
                elif block.block_type == 'nav_item':
                    self.build_nav_items(block, menu)
        for nav_menu in self.get_footer_nav_fields():
            menu = menus[nav_menu] = []
            for block in getattr(self, nav_menu):
                if block.block_type == 'nav_item':
                    self.build_nav_items(block, menu)
        return menus

    @classmethod
    def get_nav_context(cls, site):
        obj = cls.for_site(site)
        cache_key = cls.get_cache_key_nav(site.pk)

        try:
            cached = cache.get(cache_key)
        except CacheMiss:
            obj = cls.for_site(site)
            data = obj.build_nav()
            cache.set(cache_key, data, settings.MONTH_IN_SECONDS)  # month
            return data
        else:
            return cached

    @classmethod
    def get_cache_key_nav(cls, site_id):
        return f'{site_id}_site_nav_settings'

    def save(self, *args, **kwargs):
        cache.delete(self.get_cache_key_nav(self.site_id))
        clear_cache()
        invalidate_all()
        return super().save(*args, **kwargs)

    base_tabs = [
        ObjectList(NavBar.navbar_panels, heading=_('Navbar')),
        ObjectList(Footer.footer_panels, heading=_('Footer')),
    ]

    edit_handler = TabbedInterface(base_tabs)
