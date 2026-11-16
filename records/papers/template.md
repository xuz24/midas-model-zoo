# Paper Entry

A paper entry describes one publication and links to the models and datasets it introduces or uses. Save it as `papers/<id>.yaml`. Use the convention `firstauthor-year-keyword` for IDs.

| Field | Required | Allowed values or format | Notes |
|---|---|---|---|
| `id` | Yes | slug, such as `devlin-2018-bert` | Matches the filename |
| `title` | Yes | text | |
| `authors` | Yes | list of names or quoted `@username` strings | Username credits link to researcher profiles and populate their research lists. |
| `year` | Yes | four-digit year | |
| `summary` | Yes | 1 to 2 sentences | Written for the site, not copied from the abstract |
| `last_updated` | Yes | date | |
| `doi` | Conditional | DOI | Required unless `arxiv_url` is given. Preferred primary link |
| `arxiv_url` | Conditional | URL | Required unless `doi` is given |
| `venue` | No | text | Venue name without a year, such as `NAACL-HLT`; put the publication year in `year`. Keep workshop or track names when applicable. |
| `models` | No | list of model ids | |
| `datasets` | No | list of dataset ids | |
| `tags` | No | list of text | Free-form |
