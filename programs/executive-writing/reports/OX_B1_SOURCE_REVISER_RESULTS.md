# Ox Alpha B1 source-verifier/reviser result

## Decision

Reject `ox-alpha-b1-source-reviser-v1` as a writing candidate. The second
source-only session materially improved the scorer-blind grounding audit, but
the frozen all-or-nothing gate failed: only 13 of 24 deterministic hard gates
passed and two final outputs still contained material unsupported expansion.
The evaluated outputs will not be revised, filtered, or resampled in place.

Retain the run only as visible-B1 diagnostic evidence that a source-only
reviser can remove many unsupported additions while leaving important lexical
and semantic failures. It is not a finalist, production recommendation,
teacher, judge, or source of training data.

## Frozen execution and provenance

- Candidate/config: `ox-alpha-b1-source-reviser-v1`, config SHA-256
  `9c8638b…`; preregistration `ef4652d…`; agent config `aaedc442…`
- Frozen code revision: `3bcecc4ccfbce1439438ce9e1727ab5407f58640`
- Provider/model: OpenRouter / `stealth/ox-alpha`; high reasoning;
  temperature 0; top-p 1; two maximum steps; wildcard tool denial
- Run: `ox-alpha-b1-source-reviser-v1-20260823T213606Z`; 24 fresh drafts and
  24 separately isolated revisions; 48 unique sessions; all finish reason
  `stop`; zero tool events, file changes, or reported cost
- Input boundary: sanitized project-authored visible B1 task fields and source
  only for drafting; the same fields, source, and that case's fresh draft only
  for revision. No expected answer, scorer, rubric, prior Ox candidate, audit
  finding, B2, Tier C, private material, or training example crossed the
  provider boundary.
- Run manifest SHA-256 `c031a7e…`; final outputs `e6ec2d4d…`; analysis
  `79da9c5…`; case results `3ee647e…`; audit `8eee1d3…`

The live inventory reported the exact model, a 1,048,576-token context,
131,072 maximum completion tokens, all required parameters, and zero prompt
and completion prices. Settled project spend remains $0.

## Preregistered comparison

The primary baseline is the directly pinned 24-case deterministic-v1.1 result
for `qwen2.5-0.5b-retrieval-ledger-draft-v2`.

| Metric | Source-reviser | Compact ledger | Paired result |
| --- | ---: | ---: | ---: |
| Mean development score | 93.3607 | 87.1981 | +6.1626 |
| Aggregate median | 94.3413 | 91.2353 | — |
| Paired median effect | — | — | +3.7654 |
| Hard-gate passes | 13/24 | 12/24 | +1 case |
| Hard-gate rate | 54.17% | 50.00% | +4.17 points |
| Wins / ties / losses | — | — | 15 / 2 / 7 |
| 10,000-resample 95% interval | — | — | +2.0563 to +10.5460 |

The score-only +2-point/no-regression rule passed. Candidate advancement did
not: the preregistration required all 24 hard gates plus a clean output audit.

Dimension means were 98.5879 clarity/coherence, 95.1323 concision, 93.7500
organization/actionability, 93.0556 audience/format, 88.5863 fidelity, and
100.0000 profile control. Deterministic errors comprised 11 omissions, five
structural failures, and two poor-actionability findings.

## Direct Ox v2 comparison

Holding model/provider and visible cases fixed, the source-reviser scored
0.1831 paired mean points below Ox v2 and had a paired median effect of
-0.1923, with 8/3/13 wins/ties/losses. Both passed 13 hard gates; h10 gained
three v2 failures and lost three v2 passes. Its aggregate median was 0.4722
points higher, which is distinct from the negative paired median effect.

The qualitative change was favorable: material source-expansion findings fell
from six cases to two; introduced placeholders fell from one to zero; and
no-audit-flag outputs rose from 18 to 22. Both v2 and h10 returned 24/24
artifact-only responses with no run-date insertion. The reviser changed 22 of
24 draft output hashes and removed clear draft additions such as a fabricated
incident date, unsupported launch rationale, and overbroad confidentiality
instructions.

The improvement was not free in deployment terms. Versus v2, total prompt
tokens rose from 26,478 to 83,094 (3.14×), output tokens from 5,004 to 12,304
(2.46×), and mean end-to-end latency from 18.073 to 21.232 seconds (1.17×).

## Stage cost and latency

| Stage | Sessions | Prompt tokens | Output tokens | Cache-read tokens | Mean | Median | p95 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Fresh draft | 24 | 35,934 | 4,762 | 20,224 | 9.362 s | 7.515 s | 17.018 s |
| Source revision | 24 | 47,160 | 7,542 | 13,056 | 11.870 s | 9.474 s | 29.824 s |
| Combined candidate | 24 | 83,094 | 12,304 | 33,280 | 21.232 s | 17.456 s | 41.379 s |

Summed stage latency was 509.579 seconds. Every session and the completed run
reported $0 cost.

## Hash-bound output audit

The reviewer inspected all 24 final artifacts against their source/task
boundary after generation. The committed audit contains only output hashes and
compact findings.

- Meta or harness preamble: 0/24
- Introduced non-source placeholder: 0/24
- Introduced run-date metadata: 0/24
- Material source-expansion risk: 2/24
- Artifact-only: 24/24
- No audit flag: 22/24 (91.67%)

The two material failures were:

- `b1-020-cache-blog`: unsupported internal read-path and causal claims, an
  always-fresh inventory guarantee not entailed by cache bypass, and a
  universal customer-experience claim.
- `b1-022-payment-delay-operations`: unsupported attribution of the second-
  route recommendation to Treasury and conversion of an uncertain $600,000
  estimate into an “up to” cap.

## Frontier implication

The common frontier now contains fourteen comparable 24-case candidates and
still has zero finalist-ready rows. H10 is pruned unless a materially new causal
factor appears. Plateau remains unsatisfied because the accepted local leader
passes only half the hard gates and one affordable high-value hypothesis
remains: a single resource-bounded larger-local-model compact-ledger probe.

B1 remains visible and lexical. Even a clean B1 candidate would still require
deployment/privacy qualification, aggregate-only B2, genuine sealed Tier C,
and intended-audience human confirmation.
