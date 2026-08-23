# Ox Alpha B1 ceiling result

## Outcome

The one-step raw Ox Alpha candidate is rejected. Its corrected preregistered
deterministic comparison cleared the numerical advancement rule, but permitted
post-run review found agent/harness text before the requested artifact in 8 of
24 outputs and material source-expansion risk in 6 cases. It is retained only
as a visible-B1 quality-ceiling diagnostic and as evidence for a new, separately
preregistered harness hypothesis.

This is not a production, finalist, B2, sealed, or human-quality result.

## Frozen execution

- Experiment: `ox-alpha-b1-ceiling-v1`
- Candidate: `ox-alpha-b1-profile-v1`
- Model/provider: `stealth/ox-alpha` through OpenRouter
- Code revision: `aeb6e1f08dcf7eb74c886572de4118347b52e2c1`
- Run: `ox-alpha-b1-ceiling-v1-20260823T203037Z`
- Cases: 24 visible, project-authored B1 inputs
- Prompt: source and input-side constraints only; no expected answers, scorer,
  B2, Tier C, private material, prior outputs, or teacher/judge role
- Decoding/harness: high reasoning, temperature 0, top-p 1, one agent step,
  wildcard tool denial, OpenCode 1.18.21
- Sessions: 24 of 24 completed with finish reason `stop`, exact model/provider,
  zero file changes, and settled cost $0
- Tokens: 41,406 input, 8,865 output, 16,960 cache read, zero cache write
- Latency: 31,845 ms mean, 17,430 ms median, 113,853 ms p95; summed elapsed
  session time 764.287 seconds
- Run manifest SHA-256: `fae24fc4dc26e03e14c12f1a4f02a5c644ecdda0215de228c17d1cb74ff42ba6`
- Outputs SHA-256: `1092b9557f322577aa0b95a6bf55277fe15edd9a774da4d19c60575878ad6fb6`

Provider output bodies and event streams remain ignored. The committed evidence
contains only hashes, compact scores, case identifiers, and audit categories.

## Evaluator correction

The first publisher invocation used the compact-ledger run's original v1 score
and summary pins even though the Ox candidate and declared comparison used
deterministic scorer v1.1. That mixed-scorer comparison is invalid and is
preserved as
`../experiments/ox-alpha-b1-ceiling-v1-analysis-invalid-v1.json` with status
`completed_evaluator_invalidated_wrong_baseline_scores`.

Generation was not affected. The evaluator-only correction binds the frozen
Ox config and unchanged outputs to the compact-ledger candidate's already
published v1.1 rescore:

- Correction SHA-256: `6f4d200a9baae57aabdf5d2c37aa9cfd6ec9b352aebffb3918acb17915207b16`
- Corrected baseline scores SHA-256: `5513298692250c52fee959ebdbcba0014c2a875fd1bd234d3507335df1ad15db`
- Corrected baseline summary SHA-256: `786647dc745adca03fbeb9f66a56b07760c85e3355eb1c1cd1633a6f46579db4`
- Corrected analysis SHA-256: `e7c81e6cdf15038b20dac2d99e81debff7dad5a443de0b208993a017c968ce57`

The publisher now rejects a baseline whose score records or summary declare a
different scorer version, and it requires an exact hash-bound correction file
when corrected pins are used.

## Corrected preregistered score

| Measure | Ox Alpha | Compact ledger baseline | Difference |
| --- | ---: | ---: | ---: |
| Mean development score | 91.0738 | 87.1981 | +3.8757 |
| Median development score | 92.1565 | 90.1724 | +1.9841 |
| Hard-gate pass rate | 50.00% | 50.00% | 0.00 pp |

The paired 10,000-resample 95% interval was -0.8240 to +8.7727 points,
with 12 wins, one tie, and 11 losses. The frozen numerical rule required at
least +2 mean points and no hard-gate-rate regression, so the comparison
records `meets_advancement_gate: true`. The candidate did not pass every hard
gate and therefore was never finalist-ready.

Dimension means were 88.6310 fidelity, 96.5762 clarity/coherence, 97.7420
concision, 81.2500 organization/actionability, 88.8889 audience/format, and
100.0000 profile control. The lexical scorer recorded 12 omission, two poor-
actionability, and eight structural-failure labels.

## Post-run output audit

The score alone was insufficient. A separate hash-bound audit inspected the
permitted B1 outputs without publishing their bodies:

| Finding | Cases | Rate |
| --- | ---: | ---: |
| Agent or harness meta preamble | 8 | 33.33% |
| Introduced non-source placeholder | 3 | 12.50% |
| Introduced run-date metadata | 5 | 20.83% |
| Material source-expansion risk | 6 | 25.00% |
| Artifact-only outputs | 16 | 66.67% |
| Outputs with no audit flag | 9 | 37.50% |

The dominant failure was a step-limit/tool-status preamble before the artifact,
contradicting the frozen instruction to return only the finished artifact. The
source-grounding review also found unsupported process commitments, governance
owners, restrictions, or guarantees in six cases. Examples of the risk class
include inventing a board committee workflow, directing sensitive questions
away from HR, and upgrading cache-bypass evidence into an always-current
inventory guarantee. The committed audit records case IDs, output hashes, and
short rationales, not provider response text.

Audit config SHA-256:
`bbceef981bc910eed238866b07d22e3df9d63a75d0a120484beeb589d9eb8664`.
Audit result SHA-256:
`0f8204563efe7d05fb09ddcf5a33c22d274c8a52f8438854d600787579c0884d`.

## Decision and next experiment

Reject the raw v1 candidate for artifact contamination and source-grounding
risk. Retain its corrected deterministic score only as visible-B1 diagnostic
evidence showing that Ox Alpha can produce substantially stronger prose than
the small local model when the harness succeeds.

Do not strip or repair the evaluated outputs after the fact and present them as
the same candidate. The next high-value hypothesis is a new preregistered Ox
harness candidate that avoids the one-step finalization reminder while keeping
wildcard tool denial, exact provider/model/cost checks, source-only prompts, and
the same evaluation boundary. It must generate a fresh 24-case output set and
pass both the frozen score rule and the artifact/source-grounding audit before
entering the common architecture frontier.

The externally hosted stealth identifier, present zero price, private-input
acceptability, deployment durability, true B2 evidence, Tier C quarantine, and
intended-audience human ratings all remain unresolved.
