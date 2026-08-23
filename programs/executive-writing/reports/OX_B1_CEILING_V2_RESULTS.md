# Ox Alpha B1 ceiling v2 result

## Outcome

The v2 harness repair succeeded, but the v2 writing candidate is rejected.
Allowing two agent steps while continuing to deny all tools eliminated the v1
step-limit/tool-status preamble in every case. V2 also improved mean B1 score
and latency. It nevertheless failed the frozen all-hard-gates requirement,
introduced one non-source placeholder, and added material unsupported
commitments or guarantees in six cases.

The result remains visible-B1 diagnostic evidence. It is not a finalist, B2,
sealed, human-confirmed, deployable, or production candidate.

## Frozen execution and provenance correction

- Experiment/candidate: `ox-alpha-b1-ceiling-v2` /
  `ox-alpha-b1-profile-v2`
- Model/provider: OpenRouter / `stealth/ox-alpha`
- Effective code revision:
  `3ccce83f0d39556e90b57f88857b3af5261e8995`
- Run: `ox-alpha-b1-ceiling-v2-20260823T210528Z`
- Cases: 24 visible project-authored B1 inputs
- Harness: OpenCode 1.18.21, high reasoning, temperature 0, top-p 1, two
  maximum agent steps, wildcard tool denial, one fresh usable candidate per
  case
- Boundary: source and input-side task fields only; no expected answer,
  scorer, v1 output, audit finding, B2, Tier C, private material, teacher, or
  judge content
- Sessions: 24/24 completed with `stop`, exact provider/model/version, zero
  file changes, and settled cost $0
- Tokens: 26,478 input, 5,004 output, 29,632 cache read, zero cache write
- Latency: 18,073 ms mean, 9,936 ms median, 44,578 ms p95; 433.761 seconds
  summed session time
- Run manifest SHA-256: `a3ffabbd07911b8734629bfa50298749ee34c4441e22ab43b6048eebbc0c996a`
- Output SHA-256: `f3d2dff87a100ced260c94c315918508ccd26881372c0d02e17fd218036ba1fa`

The launch command supplied an incorrect 40-character expansion of the short
freeze revision. The clean worktree HEAD was verified during the active run,
before output review. Stopping and resampling two already usable responses
would have violated the frozen candidate rule, so the immutable manifest value
was preserved and a separate metadata-only correction was created. The
analysis records both values and correction SHA-256
`0101245dabc368a79e1fa74b06884ab0338df9a0f627a8d364132d487134770a`.
Model, code, config, prompts, sessions, and outputs were unaffected.

Provider outputs and event streams remain ignored. Only compact hashes, scores,
case identifiers, and audit categories are committed.

## Preregistered score

| Measure | Ox Alpha v2 | Compact ledger baseline | Difference |
| --- | ---: | ---: | ---: |
| Mean development score | 93.5438 | 87.1981 | +6.3457 |
| Median development score | 93.8691 | 91.2353 | +2.6338 |
| Hard-gate pass rate | 54.17% | 50.00% | +4.17 pp |

The paired median case effect was +3.7812 points. The paired 10,000-resample
95% interval was +1.7683 to +11.3288 points, with 14 wins, no ties, and 10
losses. The score-only comparison therefore records
`meets_advancement_gate: true`. V2 passed only 13 of 24 hard gates,
however, so the stricter candidate gate records
`candidate_meets_advancement_gate: false` and
`completed_no_automated_advancement`.

Dimension means were 90.4365 fidelity, 96.1204 clarity/coherence, 97.4091
concision, 91.6667 organization/actionability, 93.0556 audience/format, and
100.0000 profile control. The lexical scorer recorded 11 omission, three poor-
actionability, and five structural-failure labels.

Relative to v1, v2 gained 2.4700 mean points and 4.17 hard-gate percentage
points, with 13 case wins, three ties, and eight losses. Mean latency fell from
31.845 to 18.073 seconds, and output tokens fell from 8,865 to 5,004.

## Frozen output audit

| Finding | V1 | V2 |
| --- | ---: | ---: |
| Agent/harness meta preamble | 8/24 | 0/24 |
| Artifact-only output | 16/24 | 24/24 |
| Introduced non-source placeholder | 3/24 | 1/24 |
| Introduced run-date metadata | 5/24 | 0/24 |
| Material source-expansion risk | 6/24 | 6/24 |
| No audit flag | 9/24 | 18/24 |

The two-step hypothesis is supported: artifact-only compliance improved from
66.67% to 100%. The strengthened prompt also removed run-date insertion and
reduced non-source placeholders.

The remaining failure is semantic source discipline. One incident email added
`[date]` and promised a future update. Other flagged cases turned a status
report into a new launch decision point, invented launch-funding workflow,
added an overbroad confidentiality restriction, invented cache internals and
absolute freshness guarantees, or converted estimated working-capital need
into an approval request. These are material despite the stronger aggregate
score.

Audit config SHA-256:
`38fd7064240f559bb69c3906314da23924bfd4ca2c8a7c7311cd3d14d2d7c2f6`.
Audit result SHA-256:
`7dde3d936aff98c67f291522eabb9f9634448e7d44761852dfec76194b591ba5`.

## Decision and next hypothesis

Reject v2 as a writing candidate. Retain it as evidence that the harness repair
worked and that Ox Alpha is a much stronger prose ceiling than the small local
model. Do not repair or filter the evaluated outputs in place.

The remaining plausible high-value Ox hypothesis is a separately frozen
source-verifier/reviser pipeline: generate a fresh draft, then give only that
draft plus the same source and task fields to a second isolated Ox session that
must remove every non-entailed commitment and preserve operative source wording
for caveats, thresholds, decisions, and placeholders. This is one candidate
pipeline, not an evaluator or teacher, and it must receive no expected/scorer
material. It is justified only once the common architecture frontier and
hypothesis ledger show that the potential evidence gain exceeds another
visible-B1 iteration.
