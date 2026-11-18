from datetime import datetime, timezone
from urllib.parse import urlsplit


def profile_picture_url(value):
    if not isinstance(value, str) or len(value) > 2048:
        return None
    try:
        parsed = urlsplit(value)
        return value if parsed.scheme == "https" and parsed.hostname and not parsed.username and not parsed.password else None
    except ValueError:
        return None

from .database import db
from .profile_links import PROFILE_LINK_FIELDS, normalize_profile_link


class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(30), primary_key=True)
    google_sub = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )
    email = db.Column(db.String(320))
    name = db.Column(db.String(255))
    picture_url = db.Column(db.String(2048))
    institution = db.Column(db.String(255))
    role = db.Column(db.String(255))
    research_interests = db.Column(db.String(1000))
    bio = db.Column(db.Text)
    github_url = db.Column(db.String(2048))
    google_scholar_url = db.Column(db.String(2048))
    researchgate_url = db.Column(db.String(2048))
    orcid_url = db.Column(db.String(2048))
    website_url = db.Column(db.String(2048))
    other_url = db.Column(db.String(2048))
    additional_links = db.Column(db.JSON)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    @property
    def avatar_url(self):
        return profile_picture_url(self.picture_url)

    @property
    def interest_list(self):
        return [item.strip() for item in (self.research_interests or "").split(",") if item.strip()]

    @property
    def additional_link_list(self):
        links = list(self.additional_links or [])
        # Keep previously saved Other links editable in More links.
        if self.other_url and not any(link.get("url") == self.other_url for link in links):
            links.insert(0, {"label": "", "url": self.other_url})
        return links

    @property
    def profile_links(self):
        return [(label, url) for field, label, _ in PROFILE_LINK_FIELDS
                if (url := normalize_profile_link(getattr(self, field) or "", field))] + [
                    (link.get("label") or "Other", url) for link in self.additional_link_list
                    if (url := normalize_profile_link(link.get("url", ""), "other_url"))]
