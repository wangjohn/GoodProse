# Provisional final report: executive-writing model program

## Recommendation

Do not deploy any evaluated candidate for unsupervised production writing.
There is no production-qualified architecture, no finalist-ready candidate,
and therefore no defensible human-confirmed production recommendation yet.

Retain `qwen2.5-0.5b-retrieval-ledger-draft-v2` as the provisional local
research leader. It combines project-owned approved-example retrieval, a
compact source ledger, and one bounded draft pass. It leads accepted local
visible-development evidence at 87.1981 mean score, 12/24 hard gates,
2.850-second mean latency, and $0. This is a continuation anchor, not a
deployment recommendation.

The current production recommendation is “no deployment.” If a human operator
chooses to inspect the research leader, use the local interface and verify every
output line against the source.

## What was built and run

The repository contains a tested end-to-end system for source/right audits,
project-owned data compilation, privacy and contamination checks, MLX LoRA
training, local and bounded external inference, deterministic evaluation,
paired analysis, output audits, architecture frontier management, aggregate-
only B2/Tier C lifecycle handling, intended-audience human aggregation, and a
local application interface.

Completed real evidence includes:

- 24-case B1 v1 vertical slice across 14 task families and five formats;
- minimal, profile, retrieval, structured four-stage, and compact two-stage
  local baselines;
- one genuine 40-iteration smoke LoRA and one genuine 80-iteration unified
  profile-conditioned LoRA;
- matched direct and compact-ledger base/adapter evaluation;
- source-text-free coverage for all eleven descriptive profiles on neutral
  shared cases and three paired topic swaps;
- three bounded Ox Alpha architecture/ceiling candidates under exact provider
  provenance;
- one matched Qwen2.5 7B local scale probe;
- real-source acquisition/adaptation compatibility for six external suite IDs;
- a 15-candidate common frontier and exhausted high-value safe automated
  hypothesis registry.

## Main evidence

| Candidate/branch | Mean B1 score | Hard gates | Disposition |
| --- | ---: | ---: | --- |
| Minimal local prompt | 67.5522 | 6/24 | baseline only |
| Local profile prompt | 84.2839 | 5/24 | rejected/dominated |
| Local approved retrieval | 84.8283 | 9/24 | competitive baseline only |
| Four-stage ledger/draft/verify/revise | 81.3694 | 8/24 | rejected regression |
| Compact ledger/draft local leader | 87.1981 | 12/24 | provisional research leader |
| Smoke LoRA, direct / ledger | 67.9030 / 60.2537 | 0/24 / 1/24 | quality rejection |
| Unified LoRA, direct / ledger | 70.7185 / 74.5449 | 9/24 / 7/24 | quality/memorization rejection |
| Ox Alpha v2 | 93.5438 | 13/24 | grounding rejection |
| Ox Alpha source reviser | 93.3607 | 13/24 | grounding rejection |
| Qwen2.5 7B compact ledger | 90.6529 | 7/24 | hard-gate/grounding rejection |

The local leader improved +2.3698 paired points over retrieval v1 with a 95%
bootstrap interval of -2.0211 to +6.7390 and 13/4/7 wins/ties/losses. It still
omitted material content in 12 cases and failed half the hard gates.

The strongest automated scores were not accepted. Ox Alpha branches added
unsupported source expansions or artifact contamination. The 7B branch had 15
material source-expansion findings and regressed hard gates. The unified LoRA
introduced fictional training-scenario labels into 20/24 direct outputs and
15/24 ledger outputs. Negative evidence is preserved rather than optimized
away.

Paired source-profile controls were also negative: descriptive cards passed
0/6–3/6 hard gates, with mean absolute topic-pair score gaps of 2.2706–18.0289.
No profile card or standalone adapter is recommended.

## Scientific status

All reported model comparisons are exploratory visible-development evidence.
The repository records paired effects, bootstrap intervals where powered,
wins/ties/losses, repeated-selection caveats, failure analyses, output audits,
latency, tokens, memory, costs, exact model/config/data/evaluation hashes, and
negative decisions.

No LLM judge was used as decisive evidence, so judge-bias diagnostics and
judge-human calibration are not yet applicable. WritingBench execution remains
blocked because its judge is not pinned to an exact API model version. YapBench
remains blocked by missing dataset license metadata.

The external four-tier protocol is implemented but not falsely represented as
executed: there is no true separately controlled B2 operator, no genuinely
access-separated Tier C case set or signer, and no human packet or rating.

## Data and rights status

The smoke and unified datasets are project-owned synthetic architecture data.
They prove real training mechanics but not authentic task quality. No authentic
rough-to-final corpus is both available and `training_approved`.

All eleven named sources have source routes, provisional rights, availability,
descriptive profiles, evaluation coverage, and run configurations. None clears
both the frozen standalone sufficiency threshold and training-approved rights.
Their source-text-free coverage therefore satisfies the permitted low-cost
path, while standalone training remains blocked. The batched evidence and
questions are in `RIGHTS_DECISION_PACKET.md`.

Ox Alpha authored no training example. Its permitted work and candidate uses
remain isolated by exact provider/model/prompt/response provenance.

## Cost and deployment

Settled project spend is $0; remaining budget is $100; no spending envelope was
approved and no paid resource was started. The local leader uses a roughly
398 MB Q4_K_M model and averaged 2.850 seconds per B1 case across two calls on
an Apple M3 Pro. These figures do not establish hosted throughput or service
reliability.

No resource needs shutdown beyond normal local processes; every experiment
reported no remaining training process. Model caches and ignored artifacts can
be retained for reproduction under local storage policy.

## Exact use command

Run the committed fictional example on loopback Ollama:

```bash
uv run python -m goodprose.executive_writing apply \
  --request programs/executive-writing/configs/application/example-request-v1.json \
  --output programs/executive-writing/artifacts/application/example-result-v1.json
```

For private source material, copy the request into the ignored artifact
directory, never edit the committed example, and follow `APPLICATION.md`. The
result always says `production_qualified: false` and
`manual_factual_review_required: true`.

## Exact reproduction entry points

```bash
uv sync
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run python -m goodprose.executive_writing --help
```

`REPRODUCTION.md` gives exact commands and artifact prerequisites for B1,
baselines, smoke/unified data, genuine MLX training, matched evaluation,
profile controls, external adapters, B2/Tier C, human aggregation, and
application inference. Run-specific reports pin the original code revisions
and hashes.

## Conditions preventing completion

1. No candidate passes every fidelity, unsupported-claim, intent, privacy,
   rights, leakage, memorization, and deployment hard gate.
2. Zero strong candidates are eligible for the required three-to-five-finalist
   freeze.
3. A true access-separated Tier C holdout has not run exactly once.
4. Intended-audience human evaluation and production confirmation do not exist.
5. No authentic rights-approved task corpus exists for the highest-value next
   unified with/without-synthetic experiment.

The goal must remain active. The next valid trigger is a rights-cleared
authentic task-pair corpus. After a new candidate clears 24/24 B1 gates and a
clean full-output audit, freeze finalists, use B2, open Tier C once, and run the
blinded human protocol. Do not spend money, query hidden data, or recruit
raters before those gates.
