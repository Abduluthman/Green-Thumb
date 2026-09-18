"""Green Thumb: waste classification and a searchable disposal dictionary."""

from datetime import timedelta
from contextlib import closing, contextmanager
from functools import wraps
from pathlib import Path
import json
import os
import secrets
import sqlite3

from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.security import check_password_hash

from classifier import Classifier, InvalidImage, ModelUnavailable

ROOT = Path(__file__).resolve().parent
PUBLIC_PAGES = {
    "Home.html",
    "Camera.html",
    "Upload.html",
    "WasteDictionary.html",
    "Search-Template.html",
    "Feedback.html",
    "Welcome.html",
}
ADMIN_PAGES = {"AdminHome.html", "AdminFeedback.html"}


@contextmanager
def database(path):
    """Commit or roll back each transaction and always release the connection."""
    with closing(sqlite3.connect(path, timeout=10)) as connection:
        with connection:
            yield connection


def create_app(test_config=None):
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
        ADMIN_USERNAME=os.environ.get("ADMIN_USERNAME", "admin"),
        ADMIN_PASSWORD_HASH=os.environ.get("ADMIN_PASSWORD_HASH", ""),
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,
        TEMPLATES_AUTO_RELOAD=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        DATABASE=str(ROOT / "instance" / "feedback.sqlite3"),
        MODEL_PATH=os.environ.get("MODEL_PATH", str(ROOT / "model.h5")),
        RATELIMIT_STORAGE_URI=os.environ.get("RATELIMIT_STORAGE_URI", "memory://"),
    )
    if test_config:
        app.config.update(test_config)
    if app.config["ADMIN_PASSWORD_HASH"] and not (os.environ.get("SECRET_KEY") or test_config):
        raise RuntimeError("Set a persistent SECRET_KEY before enabling admin login.")
    CSRFProtect(app)
    limiter = Limiter(get_remote_address, app=app, default_limits=[])
    # Decorated views hold weak references; retain the instance even when disabled in tests.
    app.extensions["rate_limiter"] = limiter
    classifier = Classifier(app.config["MODEL_PATH"])
    app.extensions["classifier"] = classifier
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    with database(app.config["DATABASE"]) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY, issue TEXT NOT NULL, description TEXT NOT NULL,
            timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
        )""")

    def admin_required(view):
        @wraps(view)
        def protected(*args, **kwargs):
            if not session.get("admin"):
                if request.path == "/get_feedback":
                    return jsonify(error="Authentication required."), 401
                return redirect(url_for("login"))
            return view(*args, **kwargs)

        return protected

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "camera=(self), microphone=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data: blob:; media-src 'self' blob:; "
            "object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
        )
        if request.endpoint != "static":
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return jsonify(error="Your session expired. Refresh the page and try again."), 400

    @app.errorhandler(413)
    def too_large(error):
        return jsonify(error="Image exceeds the 8 MB upload limit."), 413

    @app.errorhandler(429)
    def rate_limited(error):
        return jsonify(error="Too many requests. Please wait before trying again."), 429

    @app.get("/")
    def index():
        return render_template("Home.html")

    @app.get("/<page_name>")
    def page(page_name):
        if page_name in ADMIN_PAGES:
            return admin_page(page_name)
        if page_name == "AdminLog.html":
            return redirect(url_for("login"))
        if page_name not in PUBLIC_PAGES:
            abort(404)
        return render_template(page_name)

    @admin_required
    def admin_page(page_name):
        return render_template(page_name)

    @app.get("/dictionary.json")
    def dictionary():
        return jsonify(json.loads((ROOT / "dictionary.json").read_text(encoding="utf-8")))

    @app.post("/classify/upload")
    @app.post("/classify/realtime")
    @limiter.limit("60 per minute")
    def classify():
        file = request.files.get("file")
        if file is None or not file.filename:
            return jsonify(error="Select a JPEG, PNG or WebP image."), 400
        try:
            return jsonify(classifier.classify(file.stream))
        except InvalidImage as error:
            return jsonify(error=str(error)), 400
        except ModelUnavailable:
            app.logger.exception("Model could not perform inference")
            return jsonify(
                error="Classification is currently unavailable. You can still browse the waste dictionary."
            ), 503

    @app.post("/submit_feedback")
    @limiter.limit("5 per minute")
    def submit_feedback():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="Provide an issue and description."), 400
        issue, description = data.get("issue"), data.get("description")
        if (
            not isinstance(issue, str)
            or not isinstance(description, str)
            or not 1 <= len(issue.strip()) <= 100
            or not 1 <= len(description.strip()) <= 2000
        ):
            return jsonify(error="Issue must be 1–100 characters and description 1–2,000 characters."), 400
        with database(app.config["DATABASE"]) as db:
            db.execute("INSERT INTO feedback (issue, description) VALUES (?, ?)", (issue.strip(), description.strip()))
        return jsonify(message="Thank you. Your feedback has been saved."), 201

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit("5 per minute", methods=["POST"])
    def login():
        error, status = None, 200
        if request.method == "POST":
            configured_hash = app.config["ADMIN_PASSWORD_HASH"]
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            if not configured_hash:
                error, status = "Admin access has not been configured.", 503
            elif (
                1 <= len(username) <= 100
                and 1 <= len(password) <= 200
                and check_password_hash(configured_hash, password)
                and secrets.compare_digest(username.encode("utf-8"), app.config["ADMIN_USERNAME"].encode("utf-8"))
            ):
                session.clear()
                session["admin"] = True
                session.permanent = True
                return redirect(url_for("home"))
            else:
                error, status = "Invalid username or password.", 401
        return render_template("AdminLog.html", error=error), status

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    @app.get("/home")
    @admin_required
    def home():
        return render_template("AdminHome.html")

    @app.get("/get_feedback")
    @admin_required
    def get_feedback():
        with database(app.config["DATABASE"]) as db:
            db.row_factory = sqlite3.Row
            rows = db.execute(
                "SELECT issue, description, timestamp FROM feedback ORDER BY id DESC LIMIT 100"
            ).fetchall()
        return jsonify([dict(row) for row in rows])

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
