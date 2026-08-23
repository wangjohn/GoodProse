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

## 2026-08-22 — Structured retrieval runner validation

- Hypothesis: explicit source-ledger extraction and post-draft verification can
  target the dominant retrieval-v1 omissions while preserving hard gates.
- Candidate/baseline: `qwen2.5-0.5b-retrieval-ledger-verify-v1` versus
  `qwen2.5-0.5b-retrieval-v1`.
- Configuration: same local Qwen 2.5 0.5B model, B1 cases, retrieval examples,
  temperature 0, seed 20260822, context 4,096, and 512-token per-call cap;
  four sequential ledger, draft, verify, and revise calls.
- Frozen gates: +2 paired mean points, no regression from 37.50% hard-gate
  pass, fewer than 14 omission cases, at most one fabrication and placeholder
  loss, mean latency at most 6,812.086 ms, at most 16,800 generated tokens, and
  $0 settled provider cost.
- Result: 36 full-repository tests plus lint, format, and type checks passed;
  the mocked full run made 96 calls and preserved all intermediate provenance.
- Decision: execute one real B1 run after committing the pipeline.
- Record: `../configs/baselines/STRUCTURED_ITERATION_v1.md`.

## 2026-08-22 — Structured retrieval improvement iteration one

- Hypothesis/candidate/baseline: the four-stage
  `qwen2.5-0.5b-retrieval-ledger-verify-v1` candidate will reduce omissions
  versus `qwen2.5-0.5b-retrieval-v1` without a hard-gate regression.
- Dataset/scorer/revision: `goodprose-b1-v1` /
  `goodprose-deterministic-v1.1` / `b7b98f9`; local Ollama 0.9.6 on Apple M3
  Pro; temperature 0; seed 20260822; $0.
- Result: 81.3694 mean and 33.33% hard gates versus 84.8283 and 37.50%.
  Paired difference -3.4589 (95% interval -10.4503 to +3.6694), median -6.7561,
  and 8/1/15 win/tie/loss. Omissions rose 14 to 16. Mean latency was 7,239.643
  ms and generated tokens were 16,861, narrowly failing both frozen caps.
- Post hoc diagnostic: the draft stage alone scored 87.3175 and 37.50% hard
  gates, but its +2.4892 paired estimate was uncertain and it had 15 omission
  cases. Verification/revision lowered final score 5.9482 points from the draft
  with a strictly negative bootstrap interval; ten changed cases worsened and
  only one improved.
- Decision: reject the candidate and retain retrieval v1. Test a newly frozen,
  regenerated two-stage compact-ledger/draft pipeline; do not promote the post
  hoc draft artifact.
- Records: `../experiments/goodprose-structured-retrieval-v1-analysis.json`,
  case results `../experiments/goodprose-structured-retrieval-v1-case-results.jsonl`,
  and `ITERATION_1_STRUCTURED.md`.

## 2026-08-22 — Compact ledger-draft runner validation

- Hypothesis: a newly generated two-stage candidate can retain the directional
  ledger-draft benefit while removing the verifier/reviser responsible for the
  iteration-one regression.
- Candidate/baseline: `qwen2.5-0.5b-retrieval-ledger-draft-v2` versus
  `qwen2.5-0.5b-retrieval-v1`; same local model, cases, retrieval examples,
  temperature, seed, and context.
- Change: compact non-tabular atomic ledger capped at 192 tokens, followed by
  one 512-token retrieval-conditioned draft with a silent completeness check.
- Frozen gates: +2 paired mean points, no regression from 37.50% hard gates,
  no more than 14 omissions/one fabrication/one placeholder loss, mean latency
  at most 4,257.554 ms, at most 9,450 generated tokens, and $0 cost.
- Result: focused pipeline tests and the complete 41-test repository suite,
  lint, format, and type checks passed.
- Decision: execute one real B1 run only after committing the candidate.
- Record: `../configs/baselines/LEDGER_DRAFT_ITERATION_v2.md`.

## 2026-08-22 — Compact ledger-draft improvement iteration two

- Hypothesis/candidate/baseline: the regenerated
  `qwen2.5-0.5b-retrieval-ledger-draft-v2` candidate will exceed retrieval v1 by
  at least two points without hard-gate or fidelity regression.
- Dataset/scorer/revision: `goodprose-b1-v1` /
  `goodprose-deterministic-v1.1` / `6920e65`; local Ollama 0.9.6 on Apple M3
  Pro; temperature 0; seed 20260822; $0.
- Result: 87.1981 mean and 50.00% hard gates versus 84.8283 and 37.50%.
  Paired difference +2.3698 (95% interval -2.0211 to +6.7390), median +0.5852,
  and 13/4/7 win/tie/loss. Omissions fell 14 to 12; registered fabrication and
  placeholder-loss counts fell to zero.
- Efficiency: 2,850.460 ms mean latency, 6,362 generated tokens, and $0; all
  frozen thresholds passed. Ledger/draft stages averaged 1,100.578/1,749.882 ms.
- Decision: keep as the directional B1 leader, without a confirmation or
  production claim. Use this inference wrapper in the smoke fine-tune
  comparison.
- Records: `../experiments/goodprose-compact-ledger-draft-v2-analysis.json`,
  case results `../experiments/goodprose-compact-ledger-draft-v2-case-results.jsonl`,
  and `ITERATION_2_LEDGER_DRAFT.md`.

## 2026-08-22 — Smoke-training corpus compilation

- Hypothesis: a separate project-owned synthetic corpus can validate real
  fine-tuning without contaminating the visible B1 evaluation or depending on
  unresolved external-source training rights.
- Dataset: `goodprose-project-authored-smoke-v1`; 48 records, 12 independent
  scenario lineages, four deterministic template clusters, and 32/8/8
  train/valid/test records. Sampling is 100% `task_pairs`, with no style-target
  or preference-pair data.
- Provenance/rights: fictional project-authored facts generated by
  `goodprose-smoke-template-v1`; permitted only for the project smoke run; no
  named-source, imported, private, B2, or Tier C text.
- Isolation: no shared lineages, exact normalized content, or 12-word n-grams
  with the 24 B1 inputs. Derived JSONL is ignored and byte-reproducible from
  committed code; the manifest records every split hash.
- Engineering result: `mlx-lm[train]==0.31.3` and its lock are installed; 46
  tests, Ruff lint/format, and Pyright pass.
- Decision: pass as smoke infrastructure, not model-quality evidence. Proceed
  to one bounded real LoRA run and matched untuned/tuned evaluation.
- Record: `../../../data/executive-writing/smoke-v1/manifest.json`.

For each run, record the hypothesis, candidate and baseline identifiers,
dataset and evaluation versions, prompt and decoding configuration, code
revision, hardware or provider, cost, paired results, confidence intervals,
failure analysis, and keep/reject decision. Link to the corresponding
machine-readable manifest under `../experiments/`.
