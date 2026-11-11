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
