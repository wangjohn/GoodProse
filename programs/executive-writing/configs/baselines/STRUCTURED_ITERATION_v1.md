# Structured retrieval iteration v1 preregistration

Status: frozen before candidate generation on 2026-08-22.

## Hypothesis

On the same Qwen 2.5 0.5B model, retrieval example, B1 cases, seed, and decoding
limits, a four-call `ledger -> draft -> verify -> revise` pipeline will reduce
critical omissions and unsupported transformations relative to
`qwen2.5-0.5b-retrieval-v1` without lowering its hard-gate pass rate.

The ledger and verifier receive only the task input, source, objective,
audience, and user constraints. They do not receive expected facts, forbidden
aliases, scores, case results, scorer code, or rubric details. The source is
repeated as authoritative at drafting, verification, and revision. Final
revision instructions require the smallest supported changes.

## Frozen comparison and gates

- Evaluation: `goodprose-b1-v1.1` with scorer
  `goodprose-deterministic-v1.1`.
- Baseline: `qwen2.5-0.5b-retrieval-v1` on identical 24 cases.
- Primary effect: at least +2.0 paired mean development points.
- Hard gate: at least the baseline 37.50% pass rate.
- Failure targets: fewer than 14 omission cases; no more than one unsupported
  claim and one confidential-placeholder loss.
- Analysis: paired mean and median differences, win/tie/loss, and a 95% paired
  bootstrap interval from 10,000 resamples with seed 20260822.
- Efficiency guardrail: mean end-to-end latency at most 6,812.086 ms and total
  generated tokens at most 16,800, both four times the retrieval-v1 baseline.
- Cost gate: settled provider cost remains $0.

Advance only if the primary effect and hard gate both pass. A failure is still
useful evidence: preserve every output, intermediate-step hash, score, latency,
token count, and failure label, then select the next hypothesis from observed
errors. Do not change B1 cases, retrieval examples, or scorer for this run.
