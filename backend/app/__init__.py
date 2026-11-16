import os
import json
import secrets
from pathlib import Path

from flask import Flask, abort, redirect, render_template, url_for
from dotenv import load_dotenv

from .records import catalog_entries, KINDS, load_records, research_entries, record_details
from .github import repository_path, fetch_repository
from .auth import auth_bp
from .database import db, migrate
from .users import users_bp

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")

frontend = Path(__file__).resolve().parents[2] / "frontend"
app = Flask(
    __name__,
    instance_path=str(BASE_DIR / "instance"),
    template_folder=str(frontend / "templates"),
    static_folder=str(frontend / "static"),
)

app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config["GOOGLE_CLIENT_ID"] = os.environ.get("GOOGLE_CLIENT_ID", "")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL",
    "sqlite:///research.db"
)

db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)

from .demo import prepare_demo
app.cli.add_command(prepare_demo)


@app.context_processor
def frontend_assets():
    manifest_path = frontend / "static/dist/.vite/manifest.json"
    if not manifest_path.exists():
        raise RuntimeError("Frontend assets are missing. Run: cd frontend && npm install && npm run build")
    manifest = json.loads(manifest_path.read_text())
    return {"assets": manifest["src/main.tsx"],
            "google_client_id": app.config["GOOGLE_CLIENT_ID"]}

@app.get("/")
def home():
    return render_template("home.html", title="Michigan Research Hub", research=research_entries())


def render_catalog(kind):
    catalog_title = kind.capitalize()
    singular = kind[:-1] if kind != "software" else kind
    share_label = "Share software" if kind == "software" else f"Share a {singular}"
    return render_template("catalog.html", title=f"{catalog_title} | Michigan Research Hub",
                           kind=kind, catalog_title=catalog_title, share_label=share_label,
                           introduction="", entries=catalog_entries(kind))


@app.get("/models")
def models():
    return render_catalog("models")


@app.get("/datasets")
def datasets():
    return render_catalog("datasets")


@app.get("/papers")
def papers():
    return render_catalog("papers")


@app.get("/software")
def software():
    return render_catalog("software")


@app.get("/<kind>/<record_id>")
def record_detail(kind, record_id):
    if kind not in KINDS:
        abort(404)
    record = next((r for r in load_records(kind) if r['id'] == record_id), None)
    if record is None:
        abort(404)
    github_path = repository_path(record)
    repository = fetch_repository(github_path) if github_path else None
    fields = record_details(kind, record)
    resource_keys = {'github_url', 'repository_url', 'repo_url', 'github', 'source_url', 'hub_url', 'arxiv_url', 'doi', 'package_url', 'docs_url'}
    related_keys = {'base_model', 'models', 'datasets', 'papers'}
    tags = [str(value) for key in ('task', 'modality', 'framework', 'language', 'license', 'tags')
            for value in (record.get(key) if isinstance(record.get(key), list) else [record.get(key)])
            if value]
    return render_template("record.html", title=record.get('title', record.get('name')),
                           author_values=next((field['values'] for field in fields if field['key'] == 'authors'), []),
                           kind=kind, record=record, tags=tags, repository=repository, github_path=github_path,
                           detail_fields=[field for field in fields if field['key'] not in resource_keys | related_keys | {'last_updated', 'tags', 'description', 'known_limitations'}],
                           resource_fields=[field for field in fields if field['key'] in resource_keys],
                           related_fields=[field for field in fields if field['key'] in related_keys])


@app.get("/submit")
def submit_research():
    return render_template("submit.html", title="Submit Research | Michigan Research Hub")


@app.get("/coming-soon/<feature>")
def coming_soon(feature):
    if feature == "submit":
        return redirect(url_for('submit_research'))
    if feature in {"models", "datasets", "papers"}:
        return redirect(url_for(feature))
    features = {
        "software": ("Demonstration software", "This fictional entry illustrates the software catalog. Repository links, documentation, and releases will be available when submissions are implemented."),
        "login": ("UMich sign-in", "University of Michigan SSO is planned. Sign-in is not available in this prototype."),
        "project": ("Demonstration project", "This is an illustrative research entry, not a real published submission. Project detail pages are coming soon."),
        "github": ("GitHub", "A project repository link and GitHub integration will be added here."),
        "contact": ("Contact", "Contact information will be added when the platform launches."),
        "docs": ("Documentation", "Guides for discovering and sharing research are coming soon."),
        "model": ("Demonstration model", "This fictional model illustrates the catalog layout. Model cards and downloadable artifacts will be available when uploads are implemented."),
        "dataset": ("Demonstration dataset", "This fictional entry illustrates the dataset catalog. Dataset details and downloads will be available when submissions are implemented."),
        "paper": ("Demonstration paper", "This fictional entry is not a published paper. Paper details and publication links will be available when submissions are implemented."),
    }
    if feature not in features:
        abort(404)
    title, description = features[feature]
    return render_template("placeholder.html", title=title, description=description)

