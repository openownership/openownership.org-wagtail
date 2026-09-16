from statham.sources import BaseSeoSource

from modules.settings.models import SiteSettings

PAGE_DESCRIPTION_FALLBACK = """Open Ownership is driving the global shift towards transparency over
who owns and controls companies. So far over 150 countries have committed to beneficial ownership
transparency"""


class ProjectSeoSource(BaseSeoSource):
    def search_url_template(self):
        return "https://openownership.org/en/search/?q={search_term_string}"

    def social_profiles(self):
        social = SiteSettings.get_social_context(self.site)
        return list(social.get("social_links", {}).values())

    def default_description(self):
        return PAGE_DESCRIPTION_FALLBACK

    def organization_type(self):
        return "Organization"
