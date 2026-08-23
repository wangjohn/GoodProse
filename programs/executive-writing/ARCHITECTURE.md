# Executive-writing program architecture

## System boundary

The program is a provenance-aware research and application system for turning
rough source material into executive writing. It is not a hosted service and
currently has no production-qualified candidate. All model execution is either
local or an explicitly preregistered external experiment; private application
inputs use the loopback-only local path.

Program ownership is split by artifact type:

| Boundary | Contents |
| --- | --- |
| `src/goodprose/executive_writing/` | Typed builders, runners, scorers, auditors, publishers, holdout lifecycle, human aggregation, and application interface |
| `tests/executive_writing/` | Deterministic unit and integrity tests; no live model calls |
| `data/executive-writing/` | Public metadata, rights/source manifests, dataset cards, and compact derived-data manifests |
| `evals/executive-writing/` | Visible B1 cases, external adapter registry, profile controls, holdout protocol, and human protocol |
| `programs/executive-writing/configs/` | Frozen model, prompt, training, evaluation, source-profile, Ox, and application configurations |
| `programs/executive-writing/experiments/` | Compact machine-readable preregistrations, analyses, hashes, frontier, hypotheses, and blocker state |
| `programs/executive-writing/reports/` | Human-readable decisions, negative results, costs, progress, and cards |
| `programs/executive-writing/artifacts/` | Ignored raw outputs, model adapters, provider events, and other sensitive or large local artifacts |

Raw data is never silently mutated. Committed metadata points to ignored raw or
derived bytes by exact hash. Model weights, adapters, private inputs, hidden
cases, provider caches, and raw candidate outputs remain outside git.

## End-to-end flow

| Stage | Input | Boundary and checks | Output |
| --- | --- | --- | --- |
| Source audit | Primary-source routes and terms evidence | HTTPS metadata, bounded text, conservative rights classification, frozen sufficiency thresholds | Eleven-person source and rights manifest plus descriptive profiles |
| Ingestion | Project-owned or locally acquired pinned source bytes | Pydantic parsing, provenance, privacy, lineage, rights, deduplication, train/eval isolation, exact and 12-word contamination checks | Reproducible ignored datasets and committed manifests |
| Training | Approved split JSONL and frozen MLX config | Exact base revision, config/data hashes, deterministic seed, bounded LoRA run, failure preservation | Ignored adapter plus compact run record and model card |
| Inference | Source-bound task, profile, model config | Loopback or preregistered provider, exact model pins, prompt isolation, deterministic decoding, per-stage hashes | Raw candidate artifact and runtime provenance |
| B1 evaluation | Visible project-owned cases | Deterministic v1.1 scorer, hard gates, paired bootstrap, full-output audits | Development evidence and architecture frontier |
| B2 evaluation | Quarantined shadow cases | Aggregate-only cadence, signed chained receipts, no item-level return | Shadow-development aggregate |
| Tier C | Frozen finalists and access-separated holdout | Burn-before-read, one-shot state, immutable aggregate receipt, retirement lifecycle | Confirmatory aggregate only |
| Tier D | Frozen opaque human packet | Intended-audience source-visible ratings, publish-readiness, critical-error veto, editing burden, pairwise preference | Human aggregate and calibration evidence |
| Application | Local JSON request | Exact provisional model/manifest/blob, selected descriptive profile, output non-overwrite, no raw source in result | Research-preview artifact with hashes and mandatory review warnings |

## Data model and trust boundaries

Pydantic models reject unknown fields at system boundaries. Every training or
evaluation record carries source identity, creation method, rights status,
lineage, split, and content hashes appropriate to its tier. Related scenarios
remain in one split. Evaluation expected fields and grader material never
enter model prompts.

The three-corpus training model separates:

- `task_pairs`: rough source to polished target;
- `style_targets`: descriptive-profile rendering targets;
- `preference_pairs`: source-bound chosen/rejected responses with reason labels.

The unified pilot compiler validates rational sampling ratios, unique lineage,
privacy, and B1 contamination before producing MLX chat rows. Its project-owned
synthetic data is authorized only for architecture testing and is not authentic
quality evidence.

Rights classifications are not inferred from public availability. Only the
user or qualified counsel can promote material to `training_approved`.
Source-text-free profile cards permit lower-cost coverage while affected
training runs remain blocked.

## Candidate architectures

The common frontier compares matched implementations of:

1. minimal single-pass prompting;
2. strong descriptive profile prompting;
3. approved-example retrieval;
4. four-stage ledger, draft, verify, and revise generation;
5. compact two-stage ledger and draft generation;
6. smoke and unified profile-conditioned LoRA adapters under direct and
   compact-ledger inference;
7. source-text-free profile-card controls for all eleven research sources;
8. external Ox Alpha ceiling, two-step, and isolated source-reviser systems;
9. a larger local Qwen2.5 7B compact-ledger probe.

The current directional local leader is the fifth architecture:
`qwen2.5-0.5b-retrieval-ledger-draft-v2`. It first extracts a bounded atomic
ledger, then drafts from the authoritative source while treating the ledger as
a fallible checklist. Approved project-owned examples influence structure only.
The candidate is not production-ready: it passes 12/24 visible B1 hard gates.

The contract's ideal structured architecture also calls for an explicit
audience-aware outline and deterministic claim verifier. The tested four-stage
variant implemented verification and minimal revision but regressed quality,
fidelity, and efficiency; it was rejected. The compact two-stage variant is an
evidence-driven simplification, not a claim that verification is unnecessary.

## Evaluation architecture

- B1 v1 contains 24 project-authored visible cases spanning 14 task families,
  five output formats, difficult fidelity controls, and scorer v1.1 correction.
- Source-profile v1 provides six neutral shared cases for every descriptive
  card. Topic-controls v2 adds three explicit paired topic swaps. Profile cards
  fit or retrieve no evaluated topic, so leave-topic-out holds by construction;
  dated leave-time-out remains mandatory for any future corpus-trained profile.
- External-v1 has seven pinned adapter definitions and tested local-file
  acquisition/adaptation boundaries. Six requested suite IDs have been adapted
  from exact real public source artifacts; no external benchmark score is
  claimed.
- Holdout-lifecycle-v1 implements B2 and Tier C schemas, signatures, aggregate
  receipts, one-shot state, verification, and retirement with synthetic
  fixtures. It does not pretend a real access-separated holdout exists.
- Human-evaluation-v1 implements the Tier D registration and aggregation
  contract. It does not create a packet before finalists pass readiness.

Automated metrics are search proxies. Final selection requires a truly
access-separated Tier C run and intended-audience human confirmation.

## Provenance and reproducibility

Run manifests bind code revision, model/provider/version, model artifacts,
prompt/config, decoding, dataset/evaluation bytes, stage order, latency,
tokens, cost, and artifact hashes. Publishers recompute deterministic scores
from raw outputs and refuse drift or overwrite. Compact committed records omit
raw private or provider output bodies.

The architecture frontier and hypothesis registry prevent rejected branches
from being silently retried or reported as winners. Confirmatory and
exploratory labels are explicit, and invalid evidence remains identifiable.

## Deployment posture

There is no recommended production deployment. The local application command
exists so the provisional research leader can be inspected under manual factual
review. It always marks results `production_qualified: false`, requires a
loopback model with exact hashes, and refuses output overwrite. The correct
production action today is no unsupervised use.
