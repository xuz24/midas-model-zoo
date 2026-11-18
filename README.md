# Michigan Research Hub

A Flask/Jinja site with React/TypeScript catalog components. The homepage and
`/models`, `/datasets`, `/papers`, and `/software` read the YAML files in `records/`.
Researcher profiles use a local SQLite database created during demo setup.
The separately supplied `.env_demo` configures demo data and Google sign-in.
No separate database server or GitHub token is needed.

## Quick start with demo data

Install Python 3.10+ and Node.js 22.18+ (including npm). The commands below use
macOS/Linux shell syntax.

### 1. Rename the supplied configuration file

Place the `.env_demo` file sent to you in the repository root, alongside
`README.md`, `requirements.txt`, and `bin/`. Open a terminal in that directory
and rename it to `.env`:

```sh
mv -i .env_demo .env
```

**The filename must be exactly `.env`.** The app automatically reads `.env` from
the repository root; it does not read `.env_demo` or `.env.txt`. If you already
have a `.env`, back it up before replacing it; the command prompts before
overwriting an existing file. Dotfiles may be hidden in your file browser.

The supplied file should contain `FLASK_SECRET_KEY`, `GOOGLE_CLIENT_ID`, and
`DEMO_DATA=1`. Keep the supplied values. `DEMO_DATA=1` enables database
migrations and demo profile loading when you start the app. No manual export or
`source .env` command is needed. Keep the configuration file private.

### 2. Install dependencies and start the app

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm --prefix frontend ci
bin/app start
```

Open http://localhost:5001. The start command builds the frontend, applies database
migrations, and inserts six fictional researcher profiles from
`demo/researchers.yaml`. Four linked sample research entries are already included
in `records/`. SQLite data is stored in `instance/research.db` by default; an
existing `DATABASE_URL` in your environment or `.env` overrides that location.
Configuration already exported in your terminal takes precedence over `.env`;
make sure an existing `DEMO_DATA=0` environment variable is not disabling setup.

Port 5001 avoids a macOS service that may occupy 5000.
Use `bin/app stop` to stop the app, `bin/app restart` to stop and start it again,
and `bin/app status` to check whether it is running. Later starts only need
`bin/app start`; the script uses `.venv` directly, builds the frontend, and starts
Flask in the background. Logs are written to `.run/app.log`. The script also works
when called from outside the project directory.

### 3. Try Google sign-in

Open **Sign in with Google** at http://localhost:5001 and use your own Google
account. On your first sign-in, complete the profile setup form and save it.
You can then visit your profile and edit it. Your account and edits are stored
in your local database.

The fictional `demo_*` researchers are browsing examples; you cannot sign in as
them. Google sign-in requires internet access and an account allowed by the
demo's Google OAuth configuration. Use `localhost:5001` consistently because the
sign-in callback is configured for that address.

## Development

For foreground development with automatic Python reloads, stop the background
app and run these commands from the repository root:

```sh
source .venv/bin/activate
flask --app backend.app prepare-demo
flask --app backend.app run --debug --host localhost --port 5001
```

Press Ctrl+C to stop the foreground server. Running Flask directly does not build
the frontend or prepare the database, so complete the quick start first.

After frontend changes, run `npm --prefix frontend run build`, or run
`npm --prefix frontend run watch` in another terminal for continuous rebuilds.
Refresh the browser after edits. Flask serves all routes and compiled assets.

## Demo

After the one-time setup above, update and start the demo with:

```sh
git pull
bin/app restart
```

Startup builds the frontend, applies database migrations, and automatically loads
six fictional researcher profiles from `demo/researchers.yaml` when `.env` contains
`DEMO_DATA=1`. No separate seed command or database copy is needed. Existing
accounts and profile edits are preserved on subsequent starts. Keep your `.env`
in place for later starts and Google sign-in.

Suggested walkthrough:

1. Open http://localhost:5001 and search for `demo` to find the sample research.
2. Open [Great Lakes Water Quality Forecast (Demo)](http://localhost:5001/models/demo-lake-forecast), then follow its dataset
   and paper links.
3. Click `@demo_maya` to see research credits grouped by catalog on a profile.
4. Open [the researcher directory](http://localhost:5001/users) and try the Climate
   science tag, Professor role, name search, and recently joined sorting. Visit
   [@demo_priya](http://localhost:5001/user/demo_priya) for all four research types.

The four sample research entries live in `records/*/demo-*.yaml` and refresh when
the browser reloads. All sample people and projects are explicitly labeled as
fictional; they make no claims about actual university research. Their detail
pages work without GitHub requests. These profiles support public browsing, not
demo sign-in or profile editing.

Set `DEMO_DATA=0` in the environment or `.env` to disable automatic migrations and
profile seeding at startup. This does not remove profiles already loaded or hide
the YAML catalog entries. For a deployment without sample content, remove the
`demo-*.yaml` records and seeded `demo_*` profiles as well. Profile fixture changes
apply to newly inserted accounts; existing profiles are never overwritten.

Demo profile links use `example.org` placeholders. To add or refresh these links
on existing fictional demo accounts, run
`.venv/bin/python -m flask --app backend.app prepare-demo --refresh-links`.
This updates only the links on accounts with matching demo identities.

## Troubleshooting startup

- **Missing `.venv` or Python dependencies:** repeat the virtual environment and
  `pip install` commands in the quick start.
- **Google sign-in button is missing:** confirm the supplied `.env_demo` was
  renamed to `.env` in the repository root, contains `GOOGLE_CLIENT_ID`, and is
  not named `.env.txt`. Run `bin/app restart` after changing configuration.
- **Google sign-in is rejected:** use http://localhost:5001 and ask the demo
  organizer to check the OAuth configuration and whether your account is allowed.
- **Frontend build fails:** check `node --version` and run
  `npm --prefix frontend ci`, then retry startup.
- **Port 5001 is in use:** stop any earlier server with `bin/app stop`. If it was
  started in the foreground, stop it with Ctrl+C in that terminal.
- **Researcher directory is empty or reports missing tables:** run
  `DEMO_DATA=1 .venv/bin/python -m flask --app backend.app prepare-demo` and refresh.
- **Server fails to start:** inspect `.run/app.log`; `bin/app status` reports
  whether the background server is running.

## Reset the database

Run `bin/db reset` to delete all tables and data in the configured database and
reapply the migrations. It uses `DATABASE_URL` from the environment or `.env`,
defaulting to `instance/research.db`. The command uses `.venv` and works from
outside the project directory. Stop the app before resetting, then start it again:

```sh
bin/app stop
bin/db reset
bin/app start
```

The next app start restores the fictional demo profiles unless `DEMO_DATA=0`.

## Editing records

Add or edit `.yaml` or `.yml` files inside `records/models`, `records/datasets`,
`records/papers`, or `records/software`. Markdown templates are ignored.
Records are read on each page request: YAML edits require only a browser refresh,
not a frontend rebuild. IDs determine URLs, so filenames may contain spaces.

Every record needs a unique lowercase slug `id` within its catalog, a `name`
(`title` for papers), `summary`, and an ISO `last_updated` date (`YYYY-MM-DD`).
Optional authors, tags, languages, and related records must be lists of strings.
Authors can mix full names and quoted `@username` credits:

```yaml
authors:
  - Alex Smith
  - '@researcher'
```

Username credits link to `/user/researcher` and automatically list the record in
that researcher's profile under Models, Datasets, Papers, or Software. Matches
are case-insensitive and require the full username; ordinary names are not matched
to accounts. Profiles reflect record edits on refresh, with the newest reviewed
records first in each group. Use the researcher's current username; update credits
if an account changes its username. Credits for accounts that have not registered
yet still load, but their profile links return 404 until the account exists.

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

The homepage research grid and all four catalogs show 24 records per page, with
Previous/Next controls and a visible result range when there is more than one
page. Search and filters apply to the full collection before pagination. Changing
search, filters, or sort order returns to page one. Catalog pagination runs in the
browser and resets on refresh; the researcher directory uses `?page=` links.

The homepage combines all four catalogs. Search, sorting, and empty states work
without a database. The `/submit` page previews the research submission fields;
it does not save or send entries yet. Its submit button currently has no action.
The planned submission workflow will create a GitHub pull request for the research
record. Google sign-in and local profile creation are available with the supplied
demo configuration.

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

Record pages enrich public GitHub repository links in `source_url`, `github_url`,
`repository_url`, `repo_url`, or `github` with repository metadata and a sanitized
README. The backend uses GitHub's repository and README REST endpoints
(https://docs.github.com/en/rest/repos). Successful responses are cached in each
server process for 15 minutes; failures are cached for one minute. GitHub outages,
rate limits, and missing READMEs leave the catalog record accessible.
README rendering preserves validated image dimensions, image alignment, and
paragraph/div/table-cell alignment. Images are constrained to the content width.
Arbitrary inline styles, scripts, and event handlers are removed; the site applies
its own typography, so rendering may still differ from GitHub.
Optionally set `GITHUB_TOKEN` in the server environment to increase API rate
limits. The token is used only by the backend. Install the updated
`requirements.txt` before starting the server.
