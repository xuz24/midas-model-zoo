from datetime import datetime, timezone
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
    institution = db.Column(db.String(255))
    role = db.Column(db.String(255))
    research_interests = db.Column(db.String(1000))
    bio = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
