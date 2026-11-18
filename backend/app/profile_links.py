import re
from urllib.parse import urlsplit


PROFILE_LINK_FIELDS = (
    ("github_url", "GitHub", "https://github.com/username"),
    ("google_scholar_url", "Google Scholar", "https://scholar.google.com/citations?user=…"),
    ("researchgate_url", "ResearchGate", "https://www.researchgate.net/profile/…"),
    ("orcid_url", "ORCID iD", "0000-0000-0000-000X or https://orcid.org/…"),
    ("website_url", "Website / portfolio", "https://your-website.com"),
)


def normalize_profile_link(value, field):
    """Return a web URL safe to render, or None for an invalid value."""
    if field == "orcid_url" and re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dXx]", value):
        value = "https://orcid.org/" + value.upper()
    if not value or len(value) > 2048 or re.search(r"[\s\x00-\x1f\x7f\\]", value):
        return None
    try:
        parsed = urlsplit(value)
        if (parsed.scheme not in {"http", "https"} or not parsed.hostname
                or parsed.username is not None or parsed.password is not None):
            return None
        parsed.port  # Reject malformed ports as well as malformed hosts.
    except ValueError:
        return None
    return value
