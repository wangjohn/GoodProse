# GoodProse B1 v1 search-development benchmark

This visible benchmark is the first-evidence plumbing and candidate-screening
set. Its 24 cases were authored for this repository by Codex from fictional
business facts. They contain no imported prose, private material, or named
person's writing and are approved only for evaluation.

The cases span email, memo, engineering and strategy documents, revision,
announcement, sensitive communication, short-form, blog, audience adaptation,
and content-controlled rendering. Closely related audience-adaptation cases
share a lineage group so later split logic cannot separate them.

This set is not authentic human rough-to-final material, is visible to the
development agent, and has low statistical power. It can validate the system
and provide directional search evidence; it cannot establish publish readiness,
human preference, broad generalization, or a production recommendation.

## Artifacts

- `cases.source.json`: reviewed authoring source.
- `case.schema.json`: generated frozen program-specific case schema.
- `cases.jsonl`: deterministic content-hashed evaluation records.
- `manifest.json`: file hashes, counts, weights, and limitations.
- `PREREGISTRATION.md`: metrics, gates, comparison set, and analysis policy.

## Rebuild and validate

```bash
uv run python -m goodprose.executive_writing benchmark build \
  --source evals/executive-writing/goodprose-b1-v1/cases.source.json \
  --cases evals/executive-writing/goodprose-b1-v1/cases.jsonl \
  --manifest evals/executive-writing/goodprose-b1-v1/manifest.json \
  --schema evals/executive-writing/goodprose-b1-v1/case.schema.json

uv run python -m goodprose.executive_writing benchmark validate \
  --cases evals/executive-writing/goodprose-b1-v1/cases.jsonl
```

Rebuilding must be byte-for-byte deterministic. Any source, schema, scoring, or
rubric change creates a new benchmark version; do not rewrite v1 after results
are observed.
