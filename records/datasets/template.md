# Dataset Entry

A dataset entry describes one dataset and links back to its stable source. Save it as `datasets/<id>.yaml`.

| Field | Required | Allowed values or format | Notes |
|---|---|---|---|
| `id` | Yes | slug | Matches the filename |
| `name` | Yes | text | Display name |
| `summary` | Yes | 1 to 2 sentences | Written for the site |
| `modality` | Yes | `text`, `image`, `audio`, `video`, `tabular`, `multimodal` | Filter field |
| `license` | Yes | SPDX identifier or `custom` | |
| `last_updated` | Yes | date | |
| `task` | No | `pretraining`, `fine-tuning`, `evaluation`, `benchmark`, `other` | Filter field |
| `size` | No | text, such as `6 GB` | Human-readable |
| `authors` | No | list of people | Individual people, not teams |
| `collection_date` | No | date | When the data was collected |
| `languages` | No | list of ISO 639-1 codes | For example, `en` |
| `known_limitations` | No | text | Shown on the page when present |
| `source_url` | No | URL | Primary link, stable dataset URL |
| `hub_url` | No | URL | Hugging Face Hub page |