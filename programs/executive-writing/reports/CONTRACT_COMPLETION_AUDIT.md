# Contract completion audit

## Outcome

The goal is not complete. The repository now satisfies 24 of 28 enumerated
deliverables and 13 of 18 stopping conditions. Four deliverables and five
stopping conditions remain conditional, failed, blocked, or necessarily
provisional.

The full 28-by-18 evidence matrix is machine-readable at
`../experiments/contract-completion-audit-v1.json`. Its validator checks the
schema, exact requirement counts, unique IDs, existence of every evidence path,
and hashes of the key final documents and result artifacts.

```bash
uv run python -m goodprose.executive_writing contract-audit \
  --audit programs/executive-writing/experiments/contract-completion-audit-v1.json \
  --repo-root .
```

## Deliverable exceptions

| Deliverable | Status | Reason |
| --- | --- | --- |
| Best-of-N distillation/rejection sampling | Conditional, not triggered | No authentic training-approved corpus or rights-safe teacher path exists; Ox Alpha is prohibited from authoring training examples |
| Frozen finalists and human packet | Failed gate | Zero of 15 frontier candidates is finalist-ready |
| Final human results | Externally blocked | No packet can be valid before finalist readiness, and real intended-audience ratings cannot be fabricated |
| Recommended production architecture | Failed gate | Evidence supports “do not deploy”; compact ledger/draft is only a research leader |

All other minimum deliverables are implemented and evidenced, including the
application command, architecture, reproduction runbook, model and dataset
cards, rights packet, topic swaps, experiment registry, and provisional report.

## Stopping-condition matrix

| Condition | Status | Evidence conclusion |
| --- | --- | --- |
| External evaluation integration | Satisfied | Seven tested adapters and reproducible acquisition; six suite IDs adapted from real pinned sources |
| Four-tier program | Satisfied | B1 plus typed/tested B2, Tier C, and Tier D protocols |
| First-evidence slice | Satisfied | 24 cases, baselines, real smoke train, shared result, failures |
| Eleven source packages | Satisfied | Audit, rights, profile, coverage, and config for every source |
| Eligible standalone/lower-cost profile runs | Satisfied | Zero standalone-eligible; all eleven received neutral and paired-topic coverage |
| Real unified run | Satisfied | Genuine 80-iteration LoRA, rejected honestly |
| Architecture ladder | Satisfied | Prompt, retrieval, direct, structured, unified LoRA, external, and scale branches compared |
| Selected candidate hard gates | Failed gate | Local leader passes only 12/24 |
| Two improvement iterations | Satisfied | Multiple preregistered positive and negative iterations completed |
| Statistical reporting | Satisfied | Paired effects, intervals where powered, caveats, negative results |
| Engineering verification | Satisfied | Final suite: 219 tests, Ruff, format, and Pyright pass |
| Genuine Tier C | Externally blocked | No eligible finalists or access-separated operator/holdout |
| Finalist freeze | Failed gate | Zero finalist-ready candidates |
| Human confirmation | Externally blocked | No valid packet or intended-audience ratings |
| Reproducibility | Satisfied | Committed-byte rebuilds, exact ignored-artifact prerequisites and hashes |
| Costs, rights, limitations, blocked runs | Satisfied | Reported honestly in the rights, costs, and provisional-final evidence |
| Paid resources, spend, remaining budget | Satisfied | $0 settled, $100 unapproved remaining, no paid process/resource |
| Final report and commands | Partial | Provisional no-deployment report and exact commands exist; human-confirmed production recommendation cannot |

## Why the leader cannot be promoted

`qwen2.5-0.5b-retrieval-ledger-draft-v2` is the best accepted local research
candidate, but its 50% hard-gate pass rate is a direct veto. Higher-scoring
external and larger-model candidates failed semantic source audits. Both real
LoRA branches failed quality or memorization controls. Topic-control coverage
did not identify a robust descriptive profile. No automated score can override
those failures.

## Safe-work exhaustion

The audit records no remaining safe autonomous repository task that could
materially satisfy a missing stopping condition without new evidence or
authority. The following are not valid autonomous continuations:

- inventing authentic training examples or promoting unresolved data rights;
- repeating rejected prompt/model branches to manufacture a win;
- creating hidden B2/Tier C cases inside the agent-readable repository;
- freezing candidates that fail readiness;
- fabricating a human packet, ratings, or judge-human calibration;
- spending money before data and candidate gates justify a scoped envelope.

## External continuation trigger

The first useful trigger is a rights-cleared authentic rough-to-final corpus as
specified in `RIGHTS_DECISION_PACKET.md`. A new candidate must then pass 24/24
B1 hard gates and a clean full-output audit. Only after three to five strong
candidates exist should a separate operator run B2 and Tier C and intended-
audience raters complete Tier D.

Until those inputs arrive, the correct status is goal active, no production
deployment, no paid action, and no false completion claim.
