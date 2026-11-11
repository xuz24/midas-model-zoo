import re
from math import ceil
from sqlalchemy import func, or_

from flask import Blueprint, request, abort, session, redirect, url_for, render_template, flash
from sqlalchemy.exc import IntegrityError

from .auth import sign_in_user
from .database import db
from .db_models import User
from .profile_options import UNIVERSITY_AFFILIATIONS, RESEARCH_INTERESTS

users_bp = Blueprint("users", __name__)

def current_user():
    user = db.session.get(User, session["username"])
    if user is None:
        session.clear()
        abort(401)
    return user


@users_bp.get("/users")
def directory():
    query = request.args.get("q", "").strip()[:200]
    page = max(1, request.args.get("page", 1, type=int))
    statement = db.select(User)
    if query:
        statement = statement.where(or_(*[
            column.icontains(query, autoescape=True) for column in
            (User.name, User.username, User.institution, User.role, User.research_interests, User.bio)
        ]))
    total = db.session.scalar(db.select(func.count()).select_from(statement.subquery()))
    per_page = 24
    pages = max(1, ceil(total / per_page))
    page = min(page, pages)
    researchers = db.session.execute(statement.order_by(
        func.lower(func.coalesce(User.name, User.username)), User.username
    ).offset((page - 1) * per_page).limit(per_page)).scalars().all()
    return render_template("users.html", researchers=researchers, query=query,
                           total=total, page=page, pages=pages,
                           title="Researchers | Michigan Research Hub")


@users_bp.get("/profile")
def profile():
    if session.get("pending_user"):
        return redirect(url_for("users.setup_profile"))
    if session.get("username") is None:
        return redirect(url_for("home"))
    user = current_user()
    return redirect(url_for("users.user", username=user.username))

@users_bp.get("/user/<username>")
def user(username):
    user = db.session.get(User, username.lower())
    if user is None:
        abort(404)
    if username != user.username:
        return redirect(url_for("users.user", username=user.username), code=301)
    return render_template("profile.html", user=user, interests=user.interest_list,
                           is_owner=session.get("username") == user.username,
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
            sign_in_user(existing)
            return redirect(url_for("users.profile"))
    fields = {name: getattr(user, name) or "" for name in
              ("username", "name", "institution", "role", "research_interests", "bio")}
    selected_interests = user.interest_list
    errors = {}

    if request.method == "POST":
        fields = {name: request.form.get(name, "").strip() for name in fields}
        submitted = request.form.getlist("research_interests")
        custom_interest = request.form.get("custom_interest", "").strip()
        if custom_interest:
            submitted.append(custom_interest)
        canonical = {interest.casefold(): interest for interest in RESEARCH_INTERESTS}
        selected_interests = []
        seen = set()
        for value in submitted:
            value = " ".join(value.split())
            value = canonical.get(value.casefold(), value)
            if value.casefold() not in seen:
                selected_interests.append(value)
                seen.add(value.casefold())
        fields["research_interests"] = ", ".join(selected_interests)
        if fields["institution"] and fields["institution"] not in UNIVERSITY_AFFILIATIONS:
            errors["institution"] = "Choose a university affiliation from the list."
        if len(selected_interests) > 20:
            errors["research_interests"] = "Choose up to 20 research interests."
        elif any(not interest or len(interest) > 80 or re.search(r"[,\x00-\x1f\x7f]", interest) for interest in selected_interests):
            errors["research_interests"] = "Use 1–80 characters per interest, without commas or control characters."
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
                sign_in_user(user)
                flash("Your profile has been saved.", "success")
                return redirect(url_for("users.profile"))

    return render_template("setup_profile.html", user=user, fields=fields, errors=errors,
                           editing=request.args.get("edit") == "1",
                           university_affiliations=UNIVERSITY_AFFILIATIONS,
                           research_interest_options=RESEARCH_INTERESTS,
                           selected_interests=selected_interests,
                           custom_interests=[interest for interest in selected_interests if interest not in RESEARCH_INTERESTS],
                           title="Your profile | Michigan Research Hub"), 400 if errors else 200
