# Paper Entry

A paper entry describes one publication and links to the models and datasets it introduces or uses. Save it as `papers/<id>.yaml`. Use the convention `firstauthor-year-keyword` for IDs.

| Field | Required | Allowed values or format | Notes |
|---|---|---|---|
| `id` | Yes | slug, such as `devlin-2018-bert` | Matches the filename |
| `title` | Yes | text | |
| `authors` | Yes | list of people | Individual people |
| `year` | Yes | four-digit year | |
| `summary` | Yes | 1 to 2 sentences | Written for the site, not copied from the abstract |
| `last_updated` | Yes | date | |
| `doi` | Conditional | DOI | Required unless `arxiv_url` is given. Preferred primary link |
| `arxiv_url` | Conditional | URL | Required unless `doi` is given |
| `venue` | No | text | For example, `NAACL 2019` |
| `models` | No | list of model ids | |
| `datasets` | No | list of dataset ids | |
| `tags` | No | list of text | Free-form |