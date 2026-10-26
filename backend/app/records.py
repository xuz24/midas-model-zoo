"""Load the editable YAML catalog without a database or generated data files."""
from datetime import date
from pathlib import Path
import re
from urllib.parse import quote, urlsplit

import yaml

RECORDS_ROOT = Path(__file__).resolve().parents[2] / "records"
KINDS = ("models", "datasets", "papers", "software")


def safe_url(value):
    if not isinstance(value, str):
        return None
    parsed = urlsplit(value)
    return value if parsed.scheme in {"http", "https"} and parsed.netloc else None


def load_records(kind):
    if kind not in KINDS:
        raise ValueError(f"Unknown record type: {kind}")
    records = []
    seen = set()
    folder = RECORDS_ROOT / kind
    for path in sorted([*folder.glob("*.yaml"), *folder.glob("*.yml")]):
        try:
            record = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(record, dict):
                raise ValueError("Record must be a mapping")
            for field in ("id", "title" if kind == "papers" else "name", "summary"):
                if not isinstance(record.get(field), str) or not record[field].strip():
                    raise ValueError(f"Missing or invalid {field}")
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", record['id']):
                raise ValueError("id must be a lowercase slug")
            if record['id'] in seen:
                raise ValueError(f"Duplicate id: {record['id']}")
            record['last_updated'] = date.fromisoformat(str(record['last_updated'])).isoformat()
            for field in ('authors', 'tags', 'models', 'datasets', 'papers', 'languages'):
                if field in record and (not isinstance(record[field], list) or not all(isinstance(v, str) for v in record[field])):
                    raise ValueError(f"{field} must be a list of strings")
            # Convert YAML dates and other scalars into JSON/template-safe values.
            record = {key: value.isoformat() if isinstance(value, date) else value for key, value in record.items()}
            seen.add(record['id'])
            records.append(record)
        except (yaml.YAMLError, ValueError, KeyError, TypeError) as exc:
            raise ValueError(f"Invalid record {path}: {exc}") from exc
    return records


def catalog_entries(kind):
    entries = []
    for record in load_records(kind):
        authors = record.get('authors', [])
        owner = ', '.join(authors) or record.get('institution') or 'Contributor not specified'
        tags = record.get('tags', [])
        if not tags:
            tags = [str(record[key]) for key in ('task', 'modality', 'license') if record.get(key)]
        entry = dict(
            id=record['id'], title=record.get('title', record.get('name')),
            name=record.get('name', record.get('title')), owner=owner,
            description=record['summary'], tags=tags, updated=record['last_updated'],
            detail_url=f"/{kind}/{record['id']}",
            category=str(record.get('category') or record.get('task') or record.get('registry') or record.get('venue') or 'Unspecified'),
            format=str(record.get('modality') or record.get('language') or record.get('year') or 'Unspecified'),
            task=str(record.get('task', 'Unspecified')), framework=str(record.get('framework', 'Unspecified')),
        )
        entries.append(entry)
    return entries


def research_entries():
    artifact_types = dict(models='Model', datasets='Dataset', papers='Paper', software='Code')
    return [dict(id=f"{kind}-{entry['id']}", title=entry['title'], description=entry['description'],
                 category=entry['category'], researcher=entry['owner'], tags=entry['tags'],
                 artifacts=[artifact_types[kind]], detail_url=entry['detail_url'], updated=entry['updated'])
            for kind in KINDS for entry in catalog_entries(kind)]


def record_details(kind, record):
    """Render all supplied fields, resolving known cross-record references."""
    rows = []
    related = {name: {r['id']: r for r in load_records(name)} for name in KINDS}
    for key, value in record.items():
        if key in {'id', 'title', 'name', 'summary'} or value is None:
            continue
        values = value if isinstance(value, list) else [value]
        cells = []
        for item in values:
            label = str(item)
            link = safe_url(label)
            target_kind = 'models' if key == 'base_model' else key
            if target_kind in related and label in related[target_kind]:
                target = related[target_kind][label]
                link = f"/{target_kind}/{label}"
                label = target.get('title', target.get('name', label))
            elif key == 'doi':
                link = 'https://doi.org/' + quote(label, safe='/')
            cells.append(dict(label=label, url=link))
        rows.append(dict(label=key.replace('_', ' ').capitalize(), values=cells))
    return rows
