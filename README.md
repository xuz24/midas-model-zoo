# Michigan Research Hub

A Flask/Jinja site with React/TypeScript catalog components. The homepage and
`/models`, `/datasets`, `/papers`, and `/software` read the YAML files in `records/`.
No database, SSO, or GitHub credentials are required.

## Run locally

Use Python 3.10+ and Node.js 22.18+.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm --prefix frontend install
bin/app start
```

Open http://localhost:5001. Port 5001 avoids the macOS service that may occupy 5000.
Use `bin/app stop` to stop the app, `bin/app restart` to stop and start it again,
and `bin/app status` to check whether it is running. Later starts only need
`bin/app start`; the script uses `.venv` directly, builds the frontend, and starts
Flask in the background. Logs are written to `.run/app.log`. The script also works
when called from outside the project directory.

For foreground development with automatic Python reloads, stop the background
app, activate `.venv`, and run `flask --app backend.app run --debug --host localhost --port 5001`.

After frontend changes, run `npm --prefix frontend run build`, or run
`npm --prefix frontend run watch` in another terminal for continuous rebuilds.
Refresh the browser after edits. Flask serves all routes and compiled assets.

## Editing records

Add or edit `.yaml` or `.yml` files inside `records/models`, `records/datasets`,
`records/papers`, or `records/software`. Markdown templates are ignored.
Records are read on each page request: YAML edits require only a browser refresh,
not a frontend rebuild. IDs determine URLs, so filenames may contain spaces.

Every record needs a unique lowercase slug `id` within its catalog, a `name`
(`title` for papers), `summary`, and an ISO `last_updated` date (`YYYY-MM-DD`).
Optional authors, tags, languages, and related records must be lists of strings.
Missing contributors are labeled “Contributor not specified”; no affiliation or
publication type is inferred. Malformed records fail with the source filename
and a validation message rather than silently disappearing.

Each card links to `/<catalog>/<id>`. The detail page displays supplied metadata,
HTTP(S) links, DOI links, and links to related IDs when those records exist.
Unresolved related IDs remain plain text. Install commands are displayed as text,
never executed. YAML metadata is contributor-supplied and is not independently
verified or corrected by the application.

Filters use the available record fields:

- Models: task and framework.
- Datasets: task and modality.
- Papers: venue and year.
- Software: registry and language.

The homepage combines all four catalogs. Search, sorting, and empty states work
without a database. The `/submit` page previews the research submission fields;
it does not save or send entries yet. Its submit button currently has no action.
The planned submission workflow will create a GitHub pull request for the research
record. Authentication remains a placeholder.

## Structure

- `backend/app/records.py`: YAML loading, validation, catalog normalization, related links.
- `backend/app/models.py`, `catalogs.py`: data-provider functions used by routes.
- `backend/app/__init__.py`: Flask catalog and detail routes, Vite manifest integration.
- `frontend/templates/base.html`: shared navigation, footer, and assets.
- `frontend/templates/record.html`: shared record detail page.
- `frontend/templates/catalog.html`: shared dataset/paper/software listing layout.
- `frontend/src/components/`: React search, filters, and cards.
- `frontend/vite.config.js`: compiles assets into `frontend/static/dist/`.

## Checks

```sh
npm --prefix frontend run build
npm --prefix frontend test
.venv/bin/python -m unittest discover -s tests -v
```

Checks cover TypeScript, searching/filtering/sorting, YAML parsing and validation,
all catalog/detail routes, related links, JSON escaping, and compiled asset serving.

The homepage hero rotates through the six most recently updated records every
six seconds. It uses `last_updated`, since upload timestamps are not currently
stored. Visitors can pause/play, step through cards, or choose a card directly.
Hovering or hiding the browser tab suspends rotation; interacting with a card or
navigation control pauses it until Play is selected. Reduced-motion preferences
start the carousel paused. YAML changes appear after refreshing the page.
