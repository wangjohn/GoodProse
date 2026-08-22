# Data Rules

These instructions apply to everything under `data/`.

## Immutability and provenance

- Never edit a raw source in place. Update its pinned revision and manifest
  entry through a reproducible fetch or build step.
- Every derived record must preserve its source identifiers, content hashes,
  transformation history, creation method, rights status, and split lineage.
- Split by document, thread, event, author, organization, and time lineage as
  appropriate. Related material must not cross training and evaluation splits.
- Never move an example between splits to improve a result.

## Rights and privacy

- Public availability is not permission to train, redistribute, or publish
  model weights derived from a source.
- Only the user or qualified counsel may promote a source to
  `training_approved`. Agents may collect evidence, recommend a status, or
  conservatively exclude material.
- Exclude hacked, leaked, sealed, restricted, unverifiable, or accidentally
  exposed material.
- Do not commit private source material, raw email dumps, credentials, personal
  data, or unredacted litigation documents.
- Run the repository privacy workflow before annotation and again before
  compiling a dataset snapshot.

## Storage boundaries

- `raw/` contains exact, pinned public upstream material and its licenses.
- `executive-writing/` contains program-specific manifests and public metadata,
  not private corpus bodies.
- `derived/` contains generated or reviewed records and is ignored except for
  its documentation.
- Large artifacts, model weights, private holdouts, and local caches must remain
  ignored or live in documented external artifact storage.

## Validation

Run `make validate` after changing public source manifests or split assignments.
Add deterministic regression coverage when changing a schema or validator.
