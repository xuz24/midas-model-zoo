import hmac

from flask import Blueprint, request, abort, session, redirect, url_for, current_app
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .database import db
from .db_models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/google")
def google_login():
    csrf_cookie = request.cookies.get("g_csrf_token")
    csrf_body = request.form.get("g_csrf_token")

    if not csrf_cookie or not csrf_body:
        abort(400)

    if not hmac.compare_digest(csrf_cookie, csrf_body):
        abort(400)

    token = request.form.get("credential")
    if not token:
        abort(400)

    try:
        user = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            current_app.config["GOOGLE_CLIENT_ID"]
        )
    except ValueError:
        abort(401)

    session.clear()

    db_user = db.session.execute(
        db.select(User).filter_by(google_sub=user["sub"])
    ).scalar_one_or_none()
    
    if db_user is None:
        session["pending_user"] = {
            "google_sub": user["sub"],
            "email": user.get("email"),
            "name": user.get("name"),
        }
        return redirect(url_for("users.setup_profile"))

    session["username"] = db_user.username
    session["email"] = db_user.email
    return redirect(url_for("home"))


@auth_bp.post("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))
