# Compact ledger-draft iteration v2 preregistration

Status: frozen before candidate generation on 2026-08-22.

## Evidence-driven change

Iteration one showed that the four-stage final candidate regressed, while its
preserved draft stage was directionally stronger before verification/revision.
That draft result is post hoc and cannot advance. It also had 15 omission cases,
so v2 is not a direct promotion: it regenerates every case with a new compact
atomic-ledger prompt and explicit silent completeness check.

V2 removes the external verifier and reviser, caps ledger generation at 192
tokens, prohibits tables and boilerplate, forbids inferred dates/causes/facts,
and asks for one labeled line per fact, qualifier, placeholder, and delivery
requirement. The single drafting call treats the source as authoritative and
must internally check every ledger item before returning only the artifact.

## Hypothesis and frozen gates

Compared with `qwen2.5-0.5b-retrieval-v1` on the identical 24 B1 cases and
scorer v1.1, the compact ledger will produce at least +2.0 paired mean points
with no regression from the 37.50% hard-gate pass rate.

- Analysis: paired mean and median differences, win/tie/loss, and a 95% paired
  bootstrap interval from 10,000 resamples with seed 20260822.
- Fidelity guardrails: no more than 14 omission cases, one fabrication case,
  or one confidential-placeholder loss.
- Efficiency guardrails: mean end-to-end latency at most 4,257.554 ms (2.5×
  retrieval v1) and total generated tokens at most 9,450 (2.25× retrieval v1).
- Cost guardrail: $0 settled provider cost.

Advance only if the +2 effect and no-hard-gate-regression rules pass. Record
all other gates and reject deployment of the candidate if an efficiency or
fidelity guardrail fails. Candidate prompts receive no expected checks, scorer
details, case results, or rubrics. Do not change the cases, scorer, model, or
retrieval examples for this run.
