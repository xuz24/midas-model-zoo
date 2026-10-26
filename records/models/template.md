# Model Entry

A model entry describes one trained model and links to its datasets and papers. Save it as `models/<id>.yaml`.

| Field | Required | Allowed values or format | Notes |
|---|---|---|---|
| `id` | Yes | slug | Matches the filename |
| `name` | Yes | text | Display name |
| `summary` | Yes | 1 to 2 sentences | Written for the site |
| `task` | Yes | `text-classification`, `text-generation`, `image-classification`, `object-detection`, `speech-recognition`, `translation`, `other` | Filter field |
| `modality` | Yes | `text`, `image`, `audio`, `video`, `tabular`, `multimodal` | Filter field |
| `framework` | Yes | `pytorch`, `tensorflow`, `jax`, `onnx`, `other` | Filter field |
| `license` | Yes | SPDX identifier or `custom` | |
| `last_updated` | Yes | date | |
| `authors` | No | list of people | Individual people, not teams |
| `institution` | No | text | |
| `base_model` | No | model id | Model this was fine-tuned from |
| `datasets` | No | list of dataset ids | |
| `papers` | No | list of paper ids | |
| `source_url` | No | URL | Primary link, stable project or repo |
| `hub_url` | No | URL | Hugging Face Hub page |