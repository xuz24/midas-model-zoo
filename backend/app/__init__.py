import json
from pathlib import Path

from flask import Flask, abort, redirect, render_template, url_for

from .records import KINDS, load_records, research_entries, record_details
from .models import get_models
from .catalogs import get_datasets, get_papers, get_software

frontend = Path(__file__).resolve().parents[2] / "frontend"
app = Flask(
    __name__,
    template_folder=str(frontend / "templates"),
    static_folder=str(frontend / "static"),
)


@app.context_processor
def frontend_assets():
    manifest_path = frontend / "static/dist/.vite/manifest.json"
    if not manifest_path.exists():
        raise RuntimeError("Frontend assets are missing. Run: cd frontend && npm install && npm run build")
    manifest = json.loads(manifest_path.read_text())
    return {"assets": manifest["src/main.tsx"]}


@app.get("/")
def home():
    return render_template("home.html", title="Michigan Research Hub", research=research_entries())


@app.get("/models")
def models():
    return render_template("models.html", title="Models | Michigan Research Hub", models=get_models())


@app.get("/datasets")
def datasets():
    return render_template("datasets.html", title="Datasets | Michigan Research Hub", entries=get_datasets())


@app.get("/papers")
def papers():
    return render_template("papers.html", title="Papers | Michigan Research Hub", entries=get_papers())


@app.get("/software")
def software():
    return render_template("software.html", title="Software | Michigan Research Hub", entries=get_software())


@app.get("/<kind>/<record_id>")
def record_detail(kind, record_id):
    if kind not in KINDS:
        abort(404)
    record = next((r for r in load_records(kind) if r['id'] == record_id), None)
    if record is None:
        abort(404)
    return render_template("record.html", title=record.get('title', record.get('name')),
                           kind=kind, record=record, fields=record_details(kind, record))


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
