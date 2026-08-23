# Executive-writing evaluations

This namespace contains GoodProse program evaluation definitions and adapters.
Use public development cases for iteration, a sealed private holdout exactly
once per version after finalists are frozen, and a blinded human evaluation for
the final production recommendation.

Public definitions and acquisition adapters may be committed. Hidden answers,
private cases, and generated result payloads belong in the ignored `private/`
and `results/` directories. Follow `evals/AGENTS.md` for every evaluation.

For aggregate-only hidden-evaluation boundaries (Tier B2 shadow development
and the Tier C one-shot holdout), use the frozen protocol at
[`holdout-lifecycle-v1/`](holdout-lifecycle-v1/README.md). Everything in that
directory is explicitly synthetic; no true hidden content exists here.

For external benchmark adapters and acquisition metadata (WritingBench,
IteraTeR/EditEval, Revision for Concision, YapBench), see
[`external-v1/`](external-v1/README.md). Six suite IDs have been exercised
against exact real-source pins in the ignored cache, but no candidate benchmark
run exists; no external benchmark rows, references, criteria, predictions, or
results are committed.

For the blinded intended-audience Tier D protocol, rating schema, critical-
error veto, and aggregate boundary, see
[`human-evaluation-v1/`](human-evaluation-v1/README.md). The protocol is tested,
but no study or packet exists because the current frontier has no candidate
that passes the finalist-readiness gate.

For all-eleven descriptive profile-card evaluation, see `source-profiles-v1/`
for neutral shared-case coverage and `source-profile-topic-controls-v2/` for
three project-authored paired topic swaps. The prompt-only cards fit or retrieve
no evaluation topic or source body. Dated leave-time-out evaluation remains a
future requirement for any corpus-trained profile.
