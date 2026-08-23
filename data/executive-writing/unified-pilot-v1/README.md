# Unified three-corpus architecture pilot v1

This directory stores only public documentation and the frozen source-record
schema for the unified profile-conditioned architecture pilot. The real
provenance manifest (`manifest.json`) is **not committed yet**: it will be
generated only after the 90 project-authored source records are independently
authored and reviewed.

## Paths

- Source records: one ignored local JSONL file supplied by Codex (never
  committed). Each line must validate against `record-schema.json` exactly.
- Derived MLX chat files: ignored `data/derived/executive-writing/unified-pilot-v1/`
  (`train.jsonl`, `valid.jsonl`, `test.jsonl`, `preferences.jsonl`). They are
  rebuilt deterministically from the source; nothing derived is committed.
- Committed artifacts: this README, `record-schema.json`, and (later) the
  compact `manifest.json` with hashes, counts, ratios, contamination evidence,
  and limitations. No source records or chat rows are ever committed.

## Rights and intended use

- Dataset ID: `goodprose-project-authored-unified-pilot-v1`
- Rights status: `training_permitted_project_owned_architecture_pilot`
- Intended use: `unified_profile_conditioning_architecture_pilot_only`

The data is project-owned synthetic content authored by Codex for architecture
pilot purposes only. It must never be described as authentic human data,
named-source data, final model-quality evidence, or permission for external
redistribution.

## Corpus shape

90 records across exactly 30 independent lineage groups, split train 60 /
valid 15 / test 15 with no lineage group crossing splits:

- `task_pair`: 54 records
- `style_target`: 22 records
- `preference_pair`: 14 records (also emitted to `preferences.jsonl`)

Three profiles (`concise-decision-v1`, `technical-explanatory-v1`,
`operational-update-v1`) and seven genres are covered overall and in train,
with no pathological imbalance.

## Reproducible build

```sh
uv run python -m goodprose.executive_writing unified-data build \
  --source <ignored-source-records.jsonl> \
  --output-dir <ignored-derived-directory> \
  --manifest data/executive-writing/unified-pilot-v1/manifest.json \
  --b1-cases evals/executive-writing/goodprose-b1-v1/cases.jsonl
```

The compiler refuses existing outputs, validates every count, balance rule,
hash commitment, and B1 separation check before writing anything, uses atomic
writes only, and performs no network or model calls.

## Contamination checks

Against the B1 benchmark: lineage-group disjointness, normalized exact-hash
disjointness, and exact contiguous 12-word n-gram disjointness over every
user prompt, target/chosen response, and rejected response.

## Why this cannot establish model quality

This pilot validates training, evaluation, and provenance plumbing on a small
project-authored corpus under fixed profiles. Its results carry no evidence
about performance on authentic executive-writing tasks and must not be used
for model-quality or production claims.
