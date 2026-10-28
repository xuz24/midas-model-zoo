import re

from flask import Blueprint, request, abort, session, redirect, url_for, render_template, flash
from sqlalchemy.exc import IntegrityError

from .database import db
from .db_models import User

users_bp = Blueprint("users", __name__)

def current_user():
    user = db.session.get(User, session["username"])
    if user is None:
        session.clear()
        abort(401)
    return user


@users_bp.get("/profile")
def profile():
    if session.get("pending_user"):
        return redirect(url_for("users.setup_profile"))
    if session.get("username") is None:
        return redirect(url_for("home"))
    user = current_user()
    interests = [item.strip() for item in (user.research_interests or "").split(",") if item.strip()]
    return render_template("profile.html", user=user, interests=interests,
                           title="My profile | Michigan Research Hub")

@users_bp.get("/user/<username>")
def user(username):
    user = db.session.get(User, username.lower())
    if user is None:
        abort(404)
    if username != user.username:
        return redirect(url_for("users.user", username=user.username), code=301)
    interests = [item.strip() for item in (user.research_interests or "").split(",") if item.strip()]
    return render_template("user.html", user=user, interests=interests,
                           title=f"{user.name or 'Researcher'} | Michigan Research Hub")

@users_bp.route("/setup-profile", methods=["GET", "POST"])
def setup_profile():
    pending = session.get("pending_user")
    if session.get("username") is None and not pending:
        return redirect(url_for("home"))

    user = current_user() if session.get("username") else User(**pending)
    # A second tab may already have completed this Google account's setup.
    if pending:
        existing = db.session.execute(db.select(User).filter_by(
            google_sub=pending["google_sub"])).scalar_one_or_none()
        if existing:
            session.pop("pending_user", None)
            session["username"] = existing.username
            session["email"] = existing.email
            return redirect(url_for("users.profile"))
    fields = {name: getattr(user, name) or "" for name in
              ("username", "name", "institution", "role", "research_interests", "bio")}
    errors = {}

    if request.method == "POST":
        fields = {name: request.form.get(name, "").strip() for name in fields}
        fields["username"] = fields["username"].lower()
        if not re.fullmatch(r"[a-z][a-z0-9_]{2,29}", fields["username"]):
            errors["username"] = "Use 3–30 letters, numbers, or underscores, starting with a letter."
        elif fields["username"] != user.username and db.session.get(User, fields["username"]):
            errors["username"] = "That username is already taken. Choose another."
        for name, limit in {"name": 255, "institution": 255, "role": 255,
                            "research_interests": 1000, "bio": 2000}.items():
            if len(fields[name]) > limit:
                errors[name] = f"Use {limit} characters or fewer."
        if not fields["name"]:
            errors["name"] = "Enter your name."
        if not errors:
            for name, value in fields.items():
                setattr(user, name, value)
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                errors["username"] = "That username or account was just registered. Choose another username or sign in again."
            else:
                session.pop("pending_user", None)
                session["username"] = user.username
                session["email"] = user.email
                flash("Your profile has been saved.", "success")
                return redirect(url_for("users.profile"))

    return render_template("setup_profile.html", user=user, fields=fields, errors=errors,
                           editing=request.args.get("edit") == "1",
                           title="Your profile | Michigan Research Hub"), 400 if errors else 200
