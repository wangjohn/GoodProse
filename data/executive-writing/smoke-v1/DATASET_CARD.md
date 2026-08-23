# Dataset card: project-authored smoke corpus v1

## Intended use

`goodprose-project-authored-smoke-v1` is a small synthetic, project-owned
dataset used only to prove the GoodProse data, MLX LoRA training, inference,
evaluation, and manifest path. It is not authentic human writing, named-source
data, a production training corpus, or evidence of writing quality.

Its rights status is `training_permitted_project_owned_smoke`. This permission
is limited to the GoodProse smoke test and does not grant external redistribution
rights for rows, adapters, or derived model artifacts.

## Composition

- 48 chat records from 12 independent fictional scenario lineages.
- 32 train, eight validation, and eight test records.
- Four deterministic template clusters.
- Twelve records each for email, memo, document, and short-post output.
- Corpus ratios: 100% task pairs, 0% style targets, 0% preference pairs.
- Dataset SHA-256:
  `0fd45daddbd67dbb616866fea099f421ca2e8c3470f6e268f0a70431e6a05f15`.

The corpus is rendered by `goodprose-smoke-template-v1`. It contains no named
source, imported source, private record, B2 case, or Tier C case.

## Provenance, isolation, and privacy

The committed manifest binds compiler/schema, split, dataset, and B1 hashes.
Every scenario lineage remains in one split. Against all 24 B1 cases, the
compiler found zero shared lineages, normalized exact hashes, or exact
contiguous 12-word n-grams.

Inputs are fictional project-authored facts. The dataset must still pass the
repository privacy workflow before any rebuilt snapshot is used. Raw compiled
rows remain under ignored `data/derived/`; only compact metadata is committed.

## Limitations

- Twelve lineages and four templates have very low effective diversity.
- Synthetic targets cannot establish behavior on authentic rough material.
- The distribution encourages template fitting and can produce repetition or
  shortcut learning.
- Validation/test splits are plumbing checks, not independent model evidence.
- Training loss and nonzero adapter tensors demonstrate a real update, not a
  useful update.

The completed smoke LoRA was rejected for quality: its direct profile variant
passed 0/24 B1 hard gates and its compact-ledger variant passed 1/24.

## Reproduction

```bash
uv run python -m goodprose.executive_writing smoke-data build \
  --output-dir data/derived/executive-writing/smoke-v1-reproduction \
  --manifest /tmp/smoke-v1-manifest.json \
  --b1-cases evals/executive-writing/goodprose-b1-v1/cases.jsonl
```

Compare the rebuilt manifest's dataset, compiler, schema, split, and B1 hashes
with `manifest.json`. The compiler refuses existing outputs; use a fresh path.
