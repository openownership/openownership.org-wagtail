from statham.sources import BaseSeoSource

from modules.core.models import SocialMediaSettings

PAGE_DESCRIPTION_FALLBACK = """Open Ownership is driving the global shift towards transparency over
who owns and controls companies. So far over 150 countries have committed to beneficial ownership
transparency"""


class ProjectSeoSource(BaseSeoSource):
    def search_url_template(self):
        return "https://openownership.org/en/search/?q={search_term_string}"

    def social_profiles(self):
        s = SocialMediaSettings.for_site(self.site)
        res = []
        if hasattr(s, "twitter") and s.twitter:
            res.append(f"https://twitter.com/{s.twitter}")

        if hasattr(s, "instagram") and s.twitter:
            res.append(f"https://instagram.com/{s.instagram}")

        if hasattr(s, "facebook") and s.facebook:
            res.append(s.facebook)

        if hasattr(s, "github") and s.github:
            res.append(s.github)

        if hasattr(s, "youtube") and s.youtube:
            res.append(s.youtube)

        return res

    def default_description(self):
        return PAGE_DESCRIPTION_FALLBACK

    def organization_type(self):
        return "Organization"
