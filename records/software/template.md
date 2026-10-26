# Software Entry

A software entry describes one package or library, such as a Python or R package. It links to the stable repository and to the package registry page. Save it as `software/<id>.yaml`. This section is a first draft for review.

| Field | Required | Allowed values or format | Notes |
|---|---|---|---|
| `id` | Yes | slug | Matches the filename, usually the package name |
| `name` | Yes | text | Display name |
| `summary` | Yes | 1 to 2 sentences | Written for the site |
| `language` | Yes | `python`, `r`, `julia`, `other` | Filter field |
| `license` | Yes | SPDX identifier or `custom` | |
| `last_updated` | Yes | date | |
| `source_url` | Yes | URL | Primary link, stable repository URL |
| `registry` | No | `pypi`, `cran`, `conda`, `other` | Where the package is published |
| `package_url` | No | URL | Registry page, such as PyPI or CRAN |
| `install` | No | text | Install command, such as `pip install scikit-learn` |
| `docs_url` | No | URL | Documentation site |
| `authors` | No | list of people | Individual people, not teams |
| `papers` | No | list of paper ids | Papers that describe the software |
| `models` | No | list of model ids | Models the software trains or runs |
| `datasets` | No | list of dataset ids | Datasets the software ships with or loads |
| `tags` | No | list of text | Free-form |