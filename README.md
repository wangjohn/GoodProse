# GoodProse

GoodProse builds provenance-aware datasets and evaluations for models that turn rough source material into clear executive emails, internal memos, and blog posts.

The project focuses on transformation rather than named-person imitation. Each example specifies an audience, channel, objective, constraints, and an original versioned voice profile. Factual fidelity, privacy, and uncertainty preservation are independent gates from writing quality.

## Quick start

```bash
uv sync
make corpus
make validate
make test
```

The current raw corpus is the technical-source collection created before the GoodProse pivot. It remains useful for testing factual compression and audience adaptation, but it is not a representative executive-writing dataset. Add permissioned rough-to-final executive revisions before training a production model.

## Training task

```text
source material + audience + channel + objective + constraints + voice profile
    -> factual, channel-appropriate executive communication
```

Supported channels are `email`, `internal_memo`, and `blog_post`. A canonical record uses the schemas under [`data/schemas/`](data/schemas/) and records source lineage, licensing, review status, and the exact voice profile.

## Annotation and dataset compilation

GoodProse includes a pinned local Argilla workflow with separate authoring and review queues, deterministic secret and personally identifiable information scans, typed JSONL boundaries, lineage-leakage checks, token reports, and immutable content-addressed snapshots.

```bash
make argilla-up
set -a
source infra/argilla/.env
set +a
uv run goodprose annotation setup
```

Open `http://127.0.0.1:6900`, then follow [`docs/ANNOTATION_WORKFLOW.md`](docs/ANNOTATION_WORKFLOW.md). Legacy pre-pivot Argilla datasets are intentionally not reused because their questions describe a different task.

## Repository map

```text
data/
  executive-writing/      program-specific data manifests and collection boundaries
  raw/                    exact, pinned upstream source documents and licenses
  content-foundation/     source documents with useful reasoning and decision content
  style-references/       approved examples, candidate references, and house-style rules
  voice-profiles/         versioned original voice definitions
  derived/                generated supervised examples and immutable snapshots
  schemas/                canonical provider-neutral record formats
  sources.json            provenance, checksums, splits, and selection rationale
docs/
  DATASET_STRATEGY.md      collection, pairing, splitting, and evaluation plan
  ANNOTATION_WORKFLOW.md   privacy, authoring, review, and snapshot runbook
  goals/                   durable autonomous research goal
evals/
  executive-writing/      program-specific public, private, and human eval definitions
infra/argilla/             pinned local annotation stack
programs/executive-writing/ configs, manifests, experiment registry, and reports
src/goodprose/             shared typed data, privacy, annotation, and snapshot tooling
src/goodprose/executive_writing/ program-specific training, evaluation, and inference code
tests/                     deterministic unit and schema tests
```

To start the autonomous research program, paste the command from
[`docs/goals/launch-executive-writing-model.md`](docs/goals/launch-executive-writing-model.md)
into Codex. The short launcher points to the versioned scientific, safety,
budget, autonomy, and completion contract in
[`docs/goals/executive-writing-model.md`](docs/goals/executive-writing-model.md).
Review and commit contract changes before starting or resuming a run.
Program-specific work should stay inside the namespaces above unless a shared
contract genuinely needs to change.

## Evaluation philosophy

Start with a strong prompted frontier-model baseline. Fine-tune only when a fixed, human-calibrated eval shows a meaningful improvement in consistency, editing effort, cost, latency, or local-model quality. See [`evals/RUBRIC.md`](evals/RUBRIC.md).

## Licensing and privacy

GoodProse's code is MIT-licensed. Files under `data/raw/` retain their upstream licenses; the root license does not relicense them. Public availability alone does not establish permission to redistribute text, derived datasets, or trained weights. Review [`data/NOTICE.md`](data/NOTICE.md), preserve source metadata, and prefer permissioned or organization-owned rough-to-final writing pairs.

Internal notes, emails, and memos can contain credentials, personal data, financial information, and confidential strategy. Scan both annotation seeds and reviewed exports, and never commit private derived data.
