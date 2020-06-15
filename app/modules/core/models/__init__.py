# -*- coding: utf-8 -*-

"""
    core.models
    ~~~~~~~~~~~
    We have to import stuff here because Django magic.
"""

from .pages import (  # NOQA
    HomePage
)

from .documents import DocumentDownload, SiteDocument  # NOQA
from .images import SiteImage  # NOQA

from .inlines import InlinePage, ImageLink  # NOQA

from .navigation import (  # NOQA
    PrimaryNavigationMenu, FooterNavigationMenu, PrimaryNavItem,
    PrimaryNavSubItem, FooterNavigationMenu
)

from .settings import (  # NOQA
    MetaTagSettings, AnalyticsSettings, SocialMediaSettings
)
