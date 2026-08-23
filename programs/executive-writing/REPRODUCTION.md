# Reproduction runbook

Run commands from the repository root. Raw datasets, model weights, adapters,
private inputs, hidden evaluations, and provider output bodies are intentionally
not committed. Reproduction therefore separates committed-byte validation from
executions that require an exact ignored source or model artifact.

## Environment and repository verification

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
git status --short
```

The test suite makes no live LLM calls. Review the branch and exact revision
before a real run; pass that 40-character revision into every experiment
command that exposes `--code-revision`.

## Rebuild the visible B1 benchmark

```bash
uv run python -m goodprose.executive_writing benchmark build \
  --source evals/executive-writing/goodprose-b1-v1/cases.source.json \
  --cases /tmp/goodprose-b1-v1-cases.jsonl \
  --manifest /tmp/goodprose-b1-v1-manifest.json \
  --schema /tmp/goodprose-b1-v1-case.schema.json

cmp /tmp/goodprose-b1-v1-cases.jsonl \
  evals/executive-writing/goodprose-b1-v1/cases.jsonl
cmp /tmp/goodprose-b1-v1-manifest.json \
  evals/executive-writing/goodprose-b1-v1/manifest.json
cmp /tmp/goodprose-b1-v1-case.schema.json \
  evals/executive-writing/goodprose-b1-v1/case.schema.json
```

Scorer v1.1 is the committed calibration correction applied offline to the
same output bytes. The reports record source and corrected score hashes so v1
and v1.1 evidence cannot be mixed.

## Run the three local prompt baselines

Start Ollama 0.9.6 on loopback and install the exact
`qwen2.5:0.5b-instruct` manifest/blob pinned in each config. Use a new ignored
output root for each reproduction:

```bash
REVISION=64ec4e3b0b748be31d2ee10f17b2979d6c979df7

uv run python -m goodprose.executive_writing baseline run \
  --config programs/executive-writing/configs/baselines/qwen2.5-0.5b-minimal-v1.json \
  --cases evals/executive-writing/goodprose-b1-v1/cases.jsonl \
  --benchmark-manifest evals/executive-writing/goodprose-b1-v1/manifest.json \
  --output-root programs/executive-writing/artifacts/baseline-reproduction \
  --code-revision "$REVISION"

uv run python -m goodprose.executive_writing baseline run \
  --config programs/executive-writing/configs/baselines/qwen2.5-0.5b-profile-v1.json \
  --cases evals/executive-writing/goodprose-b1-v1/cases.jsonl \
  --benchmark-manifest evals/executive-writing/goodprose-b1-v1/manifest.json \
  --output-root programs/executive-writing/artifacts/baseline-reproduction \
  --code-revision "$REVISION"

uv run python -m goodprose.executive_writing baseline run \
  --config programs/executive-writing/configs/baselines/qwen2.5-0.5b-retrieval-v1.json \
  --cases evals/executive-writing/goodprose-b1-v1/cases.jsonl \
  --benchmark-manifest evals/executive-writing/goodprose-b1-v1/manifest.json \
  --output-root programs/executive-writing/artifacts/baseline-reproduction \
  --code-revision "$REVISION"
```

The compact-ledger leader uses the same command with
`qwen2.5-0.5b-retrieval-ledger-draft-v2.json`. Historical result reports give
the exact execution revision and analysis commands for each comparison.

## Rebuild program-owned training data

Smoke data is rendered deterministically from code:

```bash
uv run python -m goodprose.executive_writing smoke-data build \
  --output-dir data/derived/executive-writing/smoke-v1-reproduction \
  --manifest /tmp/smoke-v1-manifest.json \
  --b1-cases evals/executive-writing/goodprose-b1-v1/cases.jsonl
```

The unified pilot requires the exact ignored project-authored source JSONL
whose SHA-256 is pinned in its manifest:

```bash
uv run python -m goodprose.executive_writing unified-data build \
  --source data/derived/executive-writing/unified-pilot-v1/source-records.jsonl \
  --output-dir data/derived/executive-writing/unified-pilot-v1-reproduction \
  --manifest /tmp/unified-pilot-v1-manifest.json \
  --b1-cases evals/executive-writing/goodprose-b1-v1/cases.jsonl
```

The compiler refuses existing outputs. If the hash-pinned ignored source is
absent, reacquire it from authorized project artifact storage; do not recreate
or substitute rows and claim byte-level reproduction.

## Reproduce the real unified LoRA pilot

The MLX config pins `mlx-lm` 0.31.3, MLX 0.32.1, the exact 4-bit base revision,
seed, LoRA rank, optimization settings, dataset hashes, and fixed final
checkpoint rule.

```bash
REVISION=370739dcae219480a75fc3571ee47e2f31a962bb

uv run python -m goodprose.executive_writing mlx-train run \
  --config programs/executive-writing/configs/training/qwen2.5-0.5b-mlx-lora-unified-pilot-v1.json \
  --data-dir data/derived/executive-writing/unified-pilot-v1 \
  --output-root programs/executive-writing/artifacts/training-runs-reproduction \
  --repo-root . \
  --code-revision "$REVISION" \
  --started-at 2026-08-23T19:09:36Z
```

The reproduced adapter is expected to remain a negative quality result. Do not
promote it based on loss. The original record binds 112 nonzero adapter tensors,
10,917 trained tokens, peak memory, timing, config/data hashes, and adapter
hash.

Matched B1 evaluation requires the reproduced adapter and exact cached base
model directory:

```bash
uv run python -m goodprose.executive_writing mlx-eval run \
  --config programs/executive-writing/configs/training/MLX_B1_UNIFIED_PILOT_EVAL_v1.json \
  --cases evals/executive-writing/goodprose-b1-v1/cases.jsonl \
  --adapter-path programs/executive-writing/artifacts/training-runs-reproduction/qwen2.5-0.5b-mlx-lora-unified-pilot-v1-20260823T190936Z/adapters \
  --model-path ~/.cache/huggingface/hub/models--mlx-community--Qwen2.5-0.5B-Instruct-4bit/snapshots/a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3 \
  --output-root programs/executive-writing/artifacts/mlx-evaluations-reproduction \
  --repo-root . \
  --code-revision "$REVISION" \
  --started-at 2026-08-23T19:17:17Z
```

If the model cache lives elsewhere, use the directory whose weight hash equals
the config pin. The runner rejects a mismatched base or adapter.

## Reproduce source-profile controls

Validate all eleven source/profile/config records:

```bash
uv run pytest tests/executive_writing/test_sources.py \
  tests/executive_writing/test_profile_coverage.py \
  tests/executive_writing/test_profile_controls.py
```

The exact paired-topic rebuild and run/publish commands are in
`evals/executive-writing/source-profile-topic-controls-v2/README.md` and the
corresponding result report. These prompts contain only project-authored cases
and descriptive profile metadata.

## External evaluation adapters

The committed registry and acquisition guide pin seven upstream suites and
their permitted local-file transformations:

```bash
uv run python -m goodprose.executive_writing external-evals validate-registry
uv run pytest tests/executive_writing/test_external_evals.py
```

Follow `evals/executive-writing/external-v1/README.md` to acquire exact upstream
artifacts into the ignored cache, verify their hashes, then run `external-evals
adapt`, `emit-candidates`, and `validate-predictions`. Do not execute YapBench
without rights clarification or claim WritingBench parity without an exact
judge pin.

## B2, Tier C, and human protocols

The repository can validate registrations, finalist freezes, receipts, chains,
retirement, and human ratings using synthetic fixtures:

```bash
uv run pytest tests/executive_writing/test_holdout.py \
  tests/executive_writing/test_human_evaluation.py
uv run python -m goodprose.executive_writing holdout --help
uv run python -m goodprose.executive_writing human-eval --help
```

True B2/Tier C execution must occur in a separately controlled environment.
Never place a real hidden case or signer key in this repository. Human
aggregation requires actual intended-audience ratings after a valid finalist
freeze; examples are not results.

## Apply the provisional local research leader

```bash
uv run python -m goodprose.executive_writing apply \
  --request programs/executive-writing/configs/application/example-request-v1.json \
  --output programs/executive-writing/artifacts/application/example-result-v1.json
```

See `APPLICATION.md`. The command is a research preview, not a production
deployment, and every artifact requires manual factual review.
