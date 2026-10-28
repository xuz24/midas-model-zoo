from datetime import datetime, timezone
from .database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    google_sub = db.Column(
        db.String(255),
        unique=True,
        nullable=False
    )
    email = db.Column(db.String(320))
    name = db.Column(db.String(255))

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )