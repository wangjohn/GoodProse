# GoodProse annotation and dataset workflow

This runbook applies three gates before a record becomes training data:

1. A privacy report is bound to the exact annotation-seed bytes.
2. One author produces the proposed title and body, followed by a separate seven-part review.
3. The compiler enforces provenance, approved references, lineage isolation, length limits, and immutable snapshotting.

The local Argilla stack is intended for a research workstation, not production deployment.

## 1. Install and start Argilla

```bash
uv sync
make argilla-up
```

Optional Presidio scanning and model-specific tokenization use:

```bash
uv sync --extra privacy --extra tokenizers
```

Load the private environment without printing it:

```bash
set -a
source infra/argilla/.env
set +a
```

Create the versioned `goodprose-authoring-v1` and `goodprose-review-v1` datasets:

```bash
uv run goodprose annotation setup
```

An existing pre-pivot `.env` may still use a legacy workspace name. Update that value privately or create a new environment file before setup. Do not print or commit its credentials. Legacy datasets can remain as an archive; GoodProse uses new dataset names and schemas.

## 2. Prepare annotation seeds

Create newline-delimited records conforming to [`data/schemas/annotation-seed.schema.json`](../data/schemas/annotation-seed.schema.json). Each seed specifies source material, channel, audience, objective, constraints, voice profile, provenance, and lineage.

Source-document IDs may reference only registered `train_reference` sources. Style-reference IDs must point to `approved_examples`, not merely ranked external references. The voice profile must exist in [`data/voice-profiles/index.json`](../data/voice-profiles/index.json).

Scan the exact seed file:

```bash
uv run goodprose privacy scan \
  data/derived/staging/annotation-seeds.jsonl \
  --report data/derived/privacy-reports/annotation-seeds.json
```

To create a separate redacted candidate:

```bash
uv run goodprose privacy scan \
  data/derived/staging/annotation-seeds.jsonl \
  --report data/derived/privacy-reports/annotation-seeds-initial.json \
  --redacted-output data/derived/staging/annotation-seeds-redacted.jsonl
```

Inspect and rescan the final file. A report for an earlier byte sequence is not valid evidence for the revised file.

## 3. Author and review

Import seeds only with a matching clean report:

```bash
uv run goodprose annotation import-authoring \
  data/derived/staging/annotation-seeds.jsonl \
  --privacy-report data/derived/privacy-reports/annotation-seeds.json
```

In `goodprose-authoring-v1`, one author writes an optional title or email subject and the complete body. Author notes record uncertainty, omissions, redactions, or decisions that the reviewer should inspect.

Prepare the independent review queue:

```bash
uv run goodprose annotation prepare-review
```

In `goodprose-review-v1`, one reviewer submits every gate:

- privacy and secret handling;
- factual fidelity;
- objective fulfillment;
- audience fit;
- channel fit;
- GoodProse house style;
- overall communication quality.

Export all completed reviews:

```bash
uv run goodprose annotation export-reviewed \
  --output data/derived/staging/reviewed.jsonl
```

Failed records remain in the export for audit, but dataset validation rejects them. Correct material under a new stable record ID rather than silently rewriting a reviewed example.

## 4. Back up and snapshot

```bash
uv run goodprose annotation backup \
  --dataset goodprose-authoring-v1 \
  --output data/derived/argilla-backups/authoring-YYYYMMDD

uv run goodprose annotation backup \
  --dataset goodprose-review-v1 \
  --output data/derived/argilla-backups/review-YYYYMMDD
```

Scan, validate, and compile the reviewed export:

```bash
uv run goodprose privacy scan \
  data/derived/staging/reviewed.jsonl \
  --report data/derived/privacy-reports/reviewed.json

uv run goodprose dataset validate data/derived/staging/reviewed.jsonl

uv run goodprose dataset snapshot \
  data/derived/staging/reviewed.jsonl \
  --privacy-report data/derived/privacy-reports/reviewed.json
```

Before a real training run, use the exact base-model tokenizer and an immutable revision:

```bash
uv run goodprose dataset snapshot \
  data/derived/staging/reviewed.jsonl \
  --privacy-report data/derived/privacy-reports/reviewed.json \
  --tokenizer MODEL_OR_LOCAL_PATH \
  --tokenizer-revision IMMUTABLE_REVISION \
  --max-tokens MODEL_CONTEXT_LIMIT
```

Back up both annotation datasets before upgrades. Add a new versioned workflow name for material schema or rubric changes; never mutate historical judgments in place.
