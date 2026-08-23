# Experiment log

No model-quality experiments have been run under the executive-writing program
yet.

## 2026-08-22 — Harness preflight

- Hypothesis: Ori can run the exact zero-priced Ox Alpha model through OpenCode
  with verified repository tool use and contract-compliant artifact output.
- Candidate: `stealth/ox-alpha` through OpenRouter; harness OpenCode `1.18.21`
  via Ori `0.8.0+3511459`; baseline: no delegated worker.
- Result: read-only smoke passed after one bounded retry; artifact-contract
  validation failed because its timestamp was date-only, not an RFC 3339
  date-time. Git state remained unchanged and both successful model calls
  reported cost $0.
- Decision: reject substantive delegation and continue directly with Codex.
- Manifest: `../experiments/2026-08-22-harness-preflight.json`.

### Corrected complete rerun

The full gate was rerun with the exact RFC 3339 timestamp supplied as trusted
orchestrator metadata. The read-only smoke and strict artifact contract both
passed; session exports verified `openrouter` / `stealth/ox-alpha`, $0 cost,
and an unchanged Git tree. The earlier negative result remains preserved in the
manifest. Disposition: enable bounded Ox Alpha assignments with Codex review.

## 2026-08-22 — Ox Alpha benchmark-design review

- Hypothesis: a bounded independent repository review will identify missing
  schema and coverage requirements before B1 fixtures are frozen.
- Worker: `stealth/ox-alpha` through OpenRouter, prompt
  `benchmark-design-review-v1` at
  `sha256:3cb99eafd45046961fd265effc947f088cdca5ed03c4c7821bd60d289532b004`.
- Inputs/use: sanitized public repository files; design review only.
- Result: accepted structured facts, edit budgets, explicit project-authored
  provenance, adversarial tags, and format constraints. Codex rejected the
  suggestion to defer document and short-form genres because the contract
  requires broader first-slice coverage.
- Cost: $0. Decision: keep as design provenance only; exclude from training,
  benchmark evidence, reference answers, and grading.
- Record: `../experiments/ox-benchmark-design-review-v1.json`.

## 2026-08-22 — GoodProse B1 v1 benchmark build

- Hypothesis: 24 project-authored cases can prove the evaluation plumbing and
  screen the first three baselines across the contract's high-value task span.
- Dataset/eval: `goodprose-b1-v1`, cases SHA-256
  `a15232a5d426dcb6f5161abc5644a8ed10f57b8b7b87fb771e62fe26e57ae352`,
  scorer `goodprose-deterministic-v1`, preregistered before generation.
- Code base: `645c342`; implementation and data are captured by the enclosing
  benchmark milestone commit.
- Hardware/provider/cost: local Apple M3 Pro; $0.
- Result: 24/24 records build deterministically and validate against the frozen
  schema. The full repository suite passed (19 tests, lint, format, type check,
  and corpus validation).
- Decision: keep as B1 search-development evidence only. It cannot establish
  semantic writing quality, authenticity, or publish readiness.

## 2026-08-22 — Local baseline runner validation

- Hypothesis: the cached Qwen 0.5B model can support a matched, zero-cost
  three-prompt baseline comparison with complete provenance and no rubric
  leakage.
- Candidate IDs: `qwen2.5-0.5b-minimal-v1`,
  `qwen2.5-0.5b-profile-v1`, and `qwen2.5-0.5b-retrieval-v1`.
- Dataset/scorer: `goodprose-b1-v1` / `goodprose-deterministic-v1`.
- Configuration: local Ollama 0.9.6, temperature 0, seed 20260822, 512 maximum
  generated tokens, 4,096-token context; Apple M3 Pro; $0.
- Result: mocked end-to-end 24-case artifact run, local-endpoint enforcement,
  prompt isolation, deterministic retrieval, tests, lint, and type checking
  passed.
- Decision: keep and execute real matched runs after committing the runner.

## 2026-08-22 — Initial matched B1 baseline generation

- Hypothesis: strong profile instructions and retrieval conditioning will
  improve fidelity and task compliance over minimal instructions on the same
  local model.
- Candidate IDs: `qwen2.5-0.5b-minimal-v1`,
  `qwen2.5-0.5b-profile-v1`, and `qwen2.5-0.5b-retrieval-v1`.
- Dataset/scorer/revision: `goodprose-b1-v1` /
  `goodprose-deterministic-v1` / `b5beef1`; matched temperature 0 and seed
  20260822; local Ollama 0.9.6 on Apple M3 Pro; $0.
- Raw result: the three means were 67.3438, 84.0755, and 84.6200; hard-gate
  rates were 20.83%, 16.67%, and 33.33%. These figures are retained for audit,
  not accepted for comparison.
- Validity finding: all three outputs correctly retained the caveat “should not
  assume ... applies to enterprise,” but literal substring matching marked it
  as an affirmative forbidden claim. The outputs, timings, and token records
  remain valid; the v1 score and summary artifacts are evaluator-invalidated.
- Decision: no winner. Freeze `goodprose-deterministic-v1.1` in
  `../../../evals/executive-writing/goodprose-b1-v1/SCORER_CALIBRATION_v1.1.md`,
  implement only the registered negation correction, and rescore identical
  output bytes. This is post-generation evaluator calibration, not
  confirmatory evidence.
- Record: `../experiments/b1-v1-initial-baselines.json`.

## 2026-08-22 — Corrected paired baseline analysis

- Hypothesis: v1.1 will repair only the observed negated-claim false positive,
  permitting an honest exploratory comparison on identical output bytes.
- Dataset/evaluation: `goodprose-b1-v1` / `goodprose-b1-v1.1`, scorer
  `goodprose-deterministic-v1.1`; no inference; $0.
- Validation: 18 focused tests passed. Exactly one case per candidate changed:
  `b1-011` gained five development points and passed its hard gate. The real
  retrieval fabrication in `b1-006` remained a failure after a newline-boundary
  regression test prevented heading negation from leaking across clauses.
- Result: minimal 67.5522 / 25.00% hard gates; profile 84.2839 / 20.83%;
  retrieval 84.8283 / 37.50%. Retrieval versus minimal was +17.2761 paired
  points (95% bootstrap interval +6.8559 to +27.9577), 16/1/7 win/tie/loss,
  and +12.50 hard-gate percentage points. Profile failed the no-regression
  gate. Retrieval versus profile was +0.5444 with an interval spanning zero.
- Failure analysis: retrieval has 14 omission cases, one placeholder loss, one
  true fabrication, and four actionability failures. It removes the structural
  failures seen in the other baselines but passes only 9/24 hard gates.
- Decision: keep retrieval v1 as the baseline for iteration one; do not claim
  it is meaningfully better than profile on mean quality. Test a structured
  fact-and-constraint ledger plus verification pass next.
- Records: `../experiments/goodprose-b1-v1.1-baselines.json`, case-level companion
  `../experiments/goodprose-b1-v1.1-case-results.jsonl`, and human summary
  `FIRST_EVIDENCE_BASELINES.md`.

## 2026-08-22 — Ox Alpha baseline-failure review attempt

- Hypothesis: a read-only Ox Alpha assignment will surface validity or
  experiment-design problems before iteration one.
- Model/provider/prompt: `stealth/ox-alpha` / OpenRouter /
  `sha256:1dd9dcae60557af224583b1e32d73f723a047353519e28fd0657dca15a713004`.
- Validation: the public inventory still listed the exact model with a
  1,048,576-token context and $0 prompt/completion prices. The earlier
  successful design-review session still exported nonzero Ox Alpha usage.
- Result: fresh high and default sessions, a fork of the successful session,
  and a minimal no-tool diagnostic each stopped with zero input/output tokens
  and no content. Repository tree `f714374d7b2d50428cc8895430680ebd8b1a066d`
  remained unchanged; settled cost was $0.
- Decision: no Ox review was produced. Reject any inferred findings and
  continue directly; bounded delegation remains optional and must be
  revalidated before a later retry.
- Record: `../experiments/ox-baseline-failure-review-v1.json`.

For each run, record the hypothesis, candidate and baseline identifiers,
dataset and evaluation versions, prompt and decoding configuration, code
revision, hardware or provider, cost, paired results, confidence intervals,
failure analysis, and keep/reject decision. Link to the corresponding
machine-readable manifest under `../experiments/`.
