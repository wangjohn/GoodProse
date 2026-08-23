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

## 2026-08-22 — MLX smoke-training runner validation

- Hypothesis: the frozen MLX runner can produce and prove a genuine adapter
  update while preserving enough evidence to reproduce or diagnose the run.
- Candidate/base: `qwen2.5-0.5b-instruct-4bit-lora-smoke-v1` from
  `mlx-community/Qwen2.5-0.5B-Instruct-4bit` at revision
  `a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3`.
- Frozen update: 40 iterations, four layers, rank 8, scale 20, learning rate
  1e-4, batch size 1, prompt masking, seed 20260822, final-checkpoint selection,
  full synthetic test-loss evaluation, 30-minute timeout, and $0 local cost.
- Validation: mocked snapshot download, model hashes, resolved MLX config,
  subprocess run, nonempty/nonzero Safetensors adapter, parsed metrics, and
  complete success manifest all passed. The runner also preserves failed
  attempts and refuses to overwrite a run ID.
- Engineering result: 50 repository tests, Ruff lint/format, and Pyright pass.
- Decision: execute one real run only after this frozen runner is committed.
- Records: `../configs/training/SMOKE_LORA_v1.md` and its JSON companion.

## 2026-08-22 — Genuine MLX LoRA smoke fine-tune

- Hypothesis/candidate: the frozen `qwen2.5-0.5b-mlx-lora-smoke-v1` run can
  prove the complete local update path for
  `qwen2.5-0.5b-instruct-4bit-lora-smoke-v1`.
- Revision/data/base: `dafa8f0` /
  `goodprose-project-authored-smoke-v1` /
  `mlx-community/Qwen2.5-0.5B-Instruct-4bit` at
  `a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3`.
- Result: 40 iterations and 4,198 trained tokens completed in 20.862 seconds
  excluding download with 1.075 GB peak memory. Validation loss fell from
  1.891 to 0.168; synthetic test loss was 0.190 (perplexity 1.209).
- Artifact proof: the final adapter is 2,938,645 bytes with hash
  `becaefb39f4f064ffc52bb8a02629b0d8c49406d83bc51087f04754359031f85`;
  all 56 tensors are nonzero. No training process remained active. Cost $0.
- Decision: pass as genuine smoke fine-tuning plumbing. The tiny templated
  corpus makes the losses unsuitable for any model-quality claim.
- Record: `../experiments/qwen2.5-0.5b-mlx-lora-smoke-v1.json`; large adapter
  and logs remain ignored and can be reproduced from the frozen config.

## 2026-08-22 — Matched MLX B1 evaluation runner validation

- Question: what changes after the genuine adapter when base weights, prompt,
  retrieval, decoding, and hardware are matched?
- Candidates: base and tuned variants under profile single-pass and compact
  ledger/draft, for four fixed candidates on all 24 B1 cases.
- Analysis: scorer v1.1 summaries plus paired tuned-minus-base bootstrap
  comparisons for each strategy; per-case outputs, scores, prompt hashes,
  intermediate ledgers, latency, tokens, peak memory, and artifact hashes.
- Validation: four focused tests and the complete 54-test repository suite,
  Ruff lint/format, and Pyright pass. The exact adapter and base hashes are
  frozen before B1 generation.
- Decision: execute once at the committed revision and report regressions as
  honestly as gains; no checkpoint or prompt reselection is allowed.
- Records: `../configs/training/MLX_B1_SMOKE_EVAL_PREREGISTRATION_v1.md` and
  its JSON companion.

## 2026-08-22 — Matched MLX smoke-adapter B1 evaluation

- Candidate/control: exact smoke LoRA adapter versus its exact 4-bit MLX base
  under matched profile and compact ledger/draft inference.
- Revision/evaluation: `b6da535` / `goodprose-b1-v1` / deterministic scorer
  v1.1; 144 local generations; temperature 0; seed 20260822; $0.
- Profile result: 67.9030 and 0% hard gates versus base 71.3900 and 16.67%.
  Paired difference -3.4870, 95% interval -11.5720 to +4.8613, and 10/1/13
  win/tie/loss.
- Ledger/draft result: 60.2537 and 4.17% hard gates versus base 73.8629 and
  29.17%. Paired difference -13.6092, 95% interval -21.1011 to -6.3146,
  and 7/0/17 win/tie/loss.
- Failure analysis: template/heading repetition, source-fact and action
  omission, overlearned generic caveats, placeholder loss, and observed
  retrieval-example fact leakage. The tuned ledger/draft path added 13 omission
  cases and 12 poor-actionability cases relative to its exact control.
- Decision: reject adapter for quality use; retain the exact run as genuine
  training-pipeline evidence. Do not run another small templated update.
- Records: `../experiments/mlx-qwen2.5-0.5b-smoke-b1-v1-analysis.json`, its
  case-level companion, shared `../experiments/latest-results.json`, and
  `FIRST_EVIDENCE_RESULTS.md`.

## 2026-08-23 — Ox all-profile source discovery

- Assignment/model: `ox-source-discovery-v1` / `stealth/ox-alpha` through
  OpenRouter, high reasoning, OpenCode 1.18.21.
- Result: all eleven names appeared once; 23 primary and routing leads were
  returned; no authored public-email collection was reported as verified; cost
  was $0. Raw output remains design provenance, not training or eval evidence.
- Codex review: retained only independently supported canonical routes;
  excluded company/secondary/government routes without adequate retrieval or
  individual attribution; corrected Jason Fried's outlook to unknown; removed
  unsupported quantitative and author-position claims; rejected the response's
  pre-session `generated_at` value.
- Decision: accept with corrections as bounded research leads. Record exact
  prompt, response, token, timing, and cost evidence in
  `../experiments/ox-source-discovery-v1.json`.

## 2026-08-23 — Ox named-source artifact implementation

- Assignment/model: `ox-source-artifacts-implementation-v1` /
  `stealth/ox-alpha` through OpenRouter, high reasoning, forked from the source
  research context; cost $0.
- Draft result: typed Pydantic source boundary, one all-eleven source manifest,
  one common-slice eval manifest, eleven source-specific configs, two READMEs,
  and 17 focused tests initially; no source text or training approval.
- Codex review: made evaluation membership exact; cross-validated config paths,
  IDs, blockers, architecture, eligibility, and provenance; narrowed rights
  uses; added regression tests for eval/config drift; and preserved exact Ox
  provenance in the machine artifacts. The corrected focused suite passes 20
  tests with Ruff lint/format and Pyright clean.
- Decision: accept after corrections as the source-manifest and rights-system
  milestone. Profile-card runs remain configured but unexecuted. Record:
  `../experiments/ox-source-artifacts-implementation-v1.json`.

## 2026-08-23 — All-eleven source-text-free profile coverage

- Question: can each descriptive source profile execute on identical
  project-authored content without source text, retrieval, identity prompting,
  or a standalone adapter?
- Candidates/control: eleven descriptive profile cards versus the frozen
  `qwen2.5-0.5b-profile-v1` house control; six shared B1 cases each; 72 local
  calls total in exact manifest order.
- Configuration: revision `c472575`; Ollama 0.9.6;
  `qwen2.5:0.5b-instruct`; temperature 0; seed 20260822; 512-token cap;
  retrieval disabled; deterministic scorer v1.1; $0.
- Result: house control 85.3381 / 33.33% hard gates. Descriptive means ranged
  from 76.7911 to 93.5057. Technical Link Commentary had the largest paired
  mean (+8.1677, 4/1/1 win/tie/loss) and 66.67% hard gates; Conversational
  Essay Memo (+5.5779), Policy Polemical Analysis (+4.9226), Institutional
  Narrative Letter (+3.8249), and Operational Executive Update (+2.7250) were
  also directionally positive. These are visible six-case estimates, not
  winner-selection evidence.
- Integrity: the publisher verified all raw hashes and exact pair order,
  rebuilt all 72 prompts, independently recomputed all v1.1 scores and summary
  statistics, corrected even-sized medians, and emitted no generated text.
  An output scan found no requested-person identity strings.
- Decision: complete coverage for all eleven profiles and retain all of them.
  Set `advancement_decision` to `none_coverage_only`; do not alter the existing
  24-case directional leader or claim impersonation quality.
- Records: `../experiments/source-profile-coverage-v1-results.json`, its
  source-text-free case companion, and ignored raw artifacts identified by the
  committed hashes.

## 2026-08-23 — Ox aggregate-only holdout lifecycle implementation

- Assignment/model: `ox-holdout-lifecycle-v1` / `stealth/ox-alpha` through
  OpenRouter, high reasoning, OpenCode 1.18.21; cost $0. The assignment and
  exact response are hash-pinned, with 177,412 input, 54,431 output, and
  3,429,504 cache-read tokens recorded.
- Draft result: strict registration, hidden-score, receipt, finalist-freeze,
  attestation, and lifecycle models; a B2 broker; Tier C open/complete/retire
  paths; CLI commands; 16 schemas; five synthetic examples; and 29 focused
  tests. No true hidden content or real holdout run was used.
- Codex review: verified the prior B2 chain before reuse; froze B1 accepted-
  candidate ordinal and evidence-artifact commitments; made hard gates and
  repeated-regression semantics independently verifiable; required external
  signing for sealed execution; linked registration, content, canary,
  contamination, finalist, and configuration hashes; burned Tier C before
  score loading; sanitized confidential failures; made state writes durable;
  and made the public verifier recompute the frozen winner. Added nine tests
  beyond the Ox draft, for 38 focused and 122 complete passing tests.
- Decision: accept after substantial corrections as protocol infrastructure.
  This is not a B2 result, sealed Tier C evidence, a finalist decision, or
  human confirmation.
- Record: `../experiments/ox-holdout-lifecycle-v1.json` and public protocol
  package `../../../evals/executive-writing/holdout-lifecycle-v1/`.

For each run, record the hypothesis, candidate and baseline identifiers,
dataset and evaluation versions, prompt and decoding configuration, code
revision, hardware or provider, cost, paired results, confidence intervals,
failure analysis, and keep/reject decision. Link to the corresponding
machine-readable manifest under `../experiments/`.
