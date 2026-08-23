# Executive-writing program progress

## Current state

- Phase: Phase 0 feasibility and first-evidence vertical slice
- Canonical project name: GoodProse
- Program branch: `codex/executive-model-program`
- Settled spend: $0 of $100
- Starting revision: `20c27103de41a495cbe6795432f48e6794a46f6c`
- First-evidence milestone: in progress; the 24-case B1 benchmark, frozen
  schema, preregistration, deterministic scorer, and validation path are
  complete; three baselines, shared results, failure analysis, and smoke
  fine-tune remain
- Harness preflight: passed on a complete 2026-08-22 rerun after supplying a
  trusted orchestrator timestamp to the artifact task. Exact model/provider,
  repository `read` use, strict artifact JSON, unchanged Git tree, and $0 cost
  were verified. See `../experiments/2026-08-22-harness-preflight.json`.
- Human evaluation: not requested; finalist-readiness gate not reached

## Launch readiness

- The concise `/goal` launcher and versioned research contract are separated.
- The contract prioritizes a 20-to-50-case first-evidence loop before
  exhaustive benchmark and public-email work.
- No Ox Alpha delegation is permitted until
  `../configs/HARNESS_PREFLIGHT.md` passes. A failed gate transfers the work to
  Codex and does not pause the program.
- No paid action is approved. The budget process remains unchanged.

## Phase ledger

Add one dated entry per phase decision with the hypothesis, evidence produced,
exit criteria, decision, next actions, and unresolved risks. Do not overwrite
historical entries.

### 2026-08-22 — Phase 0 checkpoint: environment and harness capability

- Hypothesis: the installed Ori wrapper can drive the exact free Ox Alpha
  model through a verified OpenCode harness without changing repository state.
- Evidence: Ori `0.8.0+3511459`; official `opencode-ai@1.18.21`; OpenRouter
  inventory entry for `stealth/ox-alpha`; an authenticated $0 read-tool smoke
  session; the artifact-contract response; unchanged Git tree
  `76009539d89b0b1d490993c96b76ae16f65070b3`; and the machine-readable record.
- Exit criteria: both the read-only tool smoke and strict artifact-contract
  task pass with exact model/provider provenance and no repository changes.
- Decision: gate failed because the artifact timestamp was not an RFC 3339
  date-time. No substantive task will be delegated to Ox Alpha. This is an
  optimization-gate failure, not a program blocker.
- Next actions: build the rights-safe 20-to-50-case benchmark slice, implement
  deterministic baselines and scoring, then prove smoke fine-tuning locally.
- Unresolved risks: only 48 GiB disk is free; the 18 GiB M3 Pro can support
  small MLX experiments but not an assumed production-scale run. No training
  source is yet `training_approved`, so the starter corpus must be explicitly
  project-authored or synthetic and cannot establish production quality.

### 2026-08-22 — Phase 0 checkpoint: corrected harness gate

- Hypothesis: the artifact-contract failure was caused by withholding a trusted
  wall-clock value, not by an inability to satisfy the output contract.
- Evidence: a complete rerun reverified the live model inventory; smoke session
  `ses_fd38f287bffeb6vUCx0WtNbAE6` used the `read` tool; artifact session
  `ses_fd38eae4cffe5JTH1tdGTUwR7M` returned the exact required raw JSON; both
  used `openrouter` / `stealth/ox-alpha`, cost $0, and preserved Git tree
  `413a8c030722b17cf21cb6d74eef38f4aeb9e74d`.
- Exit criteria: exact model/provider provenance, a successful read-only tool
  call, contract-compliant artifact fields, no state change, and zero/approved
  price are all verified.
- Decision: pass. Ox Alpha may receive bounded, sanitized assignments; Codex
  retains source verification, patch review, experiment execution, and final
  decisions.
- Next actions: delegate a bounded benchmark-design review while Codex builds
  the first-evidence dataset and deterministic evaluation path.
- Unresolved risks: model-generated research is not independent evaluation
  evidence and must carry generator provenance; model availability and pricing
  remain runtime facts that require revalidation after any change.

### 2026-08-22 — Phase 0 checkpoint: B1 design review

- Hypothesis: a bounded Ox Alpha review can expose missing validity controls
  before the first benchmark version is implemented.
- Evidence: committed prompt and reviewed result for
  `ox-benchmark-design-review-v1`; exact model/provider/prompt provenance; $0
  cost; unchanged repository snapshot during the assignment.
- Exit criteria: coverage and schema recommendations are concrete, checked by
  Codex against the contract, and isolated from training and evaluation data.
- Decision: accept structured fidelity entities, edit budgets, project-authored
  provenance, format rules, and slice tags. Reject deferring contracted genres;
  use a program-specific schema to cover them now.
- Next actions: implement and preregister the 24-case B1 benchmark, validator,
  deterministic scorer, and three matched baseline configurations.
- Unresolved risks: 24 cases provide plumbing and screening evidence only;
  semantic quality and unsupported-claim detection still require independent
  calibrated or human assessment in later phases.

### 2026-08-22 — Phase 0 checkpoint: B1 v1 benchmark implementation

- Hypothesis: a 24-case project-authored slice can cover the contracted
  email, memo, document, short-form, blog, audience-adaptation, and revision
  paths while making deterministic fidelity failures inspectable.
- Evidence: `goodprose-b1-v1` contains 24 content-hashed cases across 14 task
  families and five output formats, a generated frozen JSON schema,
  preregistration, exact file hashes, and deterministic scoring with the
  contract's 35/20/15/15/10/5 weights. The complete repository suite passed:
  19 tests, Ruff lint and format, Pyright, and corpus validation.
- Exit criteria: 20–50 rights-safe cases, contracted first-slice task coverage,
  explicit provenance/limitations, deterministic rebuild, schema validation,
  preregistered metrics and hard gates, and green engineering checks.
- Decision: pass and freeze B1 v1 before candidate generation. Treat it as
  visible exploratory search evidence only, never sealed or confirmatory.
- Next actions: run matched minimal-instruction, strong-prompt, and retrieval
  baselines on the cached local model; publish case-level and aggregate results;
  then select the first evidence-driven improvement hypothesis.
- Unresolved risks: exact lexical checks can miss valid paraphrases and cannot
  detect every semantic fabrication; all 24 inputs are project-authored rather
  than authentic permissioned rough-to-final pairs.

### 2026-08-22 — Phase 0 checkpoint: matched local baseline runner

- Hypothesis: one cached local model can provide a controlled comparison of
  minimal instruction, strong profile prompting, and retrieval conditioning
  without provider cost or model-family confounding.
- Evidence: three pinned configs use `qwen2.5:0.5b-instruct` with manifest hash
  `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`,
  blob hash `c5396e06af294bd101b30dce59131a76d2b773e76950acc870eda801d3ab0515`,
  Apache-2.0 license, temperature 0, seed 20260822, and local loopback only.
  Nine focused tests plus Ruff and Pyright passed, including a 24-case mocked
  run with provenance-complete artifact hashes.
- Exit criteria: matched configurations, no rubric leakage, deterministic
  retrieval, local endpoint enforcement, complete run manifests, raw artifact
  isolation, and green tests/lint/type checks.
- Decision: pass. The runner is eligible for the real $0 B1 baseline runs.
- Next actions: execute all three candidates at revision captured by this
  milestone, shut down the local service, compare paired scores, and publish a
  shared table and failure analysis.
- Unresolved risks: the 494M-parameter quantized instruction model is a plumbing
  baseline, not a quality ceiling; temperature zero does not guarantee perfect
  reproducibility across Ollama/runtime versions.

### 2026-08-22 — Phase 0 checkpoint: initial B1 baseline generation and scorer calibration

- Hypothesis: matched minimal, profile-card, and retrieval prompts will expose
  directional quality and compliance differences on the same local model.
- Evidence: all three 24-case generations completed at revision `b5beef1` with
  exact output hashes, latency and token records, and $0 settled cost. The raw
  v1 means were 67.3438, 84.0755, and 84.6200 respectively, but scorer review
  found a shared false fabrication failure on case `b1-011`.
- Exit criteria: complete matched artifacts plus a scorer-validity inspection
  before comparative inference.
- Decision: generation artifacts pass; v1 comparative scores fail calibration.
  Preserve every artifact, freeze a narrowly scoped v1.1 negation correction,
  and rescore the exact outputs without new inference. Do not select a winner
  from the v1 aggregates.
- Next actions: implement the frozen regression tests and v1.1 matcher, publish
  paired bootstrap results under the corrected scorer, then send the bounded
  failure analysis and next-hypothesis critique to Ox Alpha.
- Unresolved risks: v1.1 remains lexical and can still miss paraphrases or
  unsupported semantic claims; B1 is visible, small, and project-authored.

### 2026-08-22 — Phase 0 checkpoint: corrected baseline analysis

- Hypothesis: the frozen v1.1 negation correction can repair the demonstrated
  false positive without changing candidate outputs or unrelated scores.
- Evidence: 18 focused tests pass; exact old/new comparison shows only the
  shared `b1-011` case changes for all three candidates. Offline rescoring,
  10,000-resample paired bootstrap intervals, case-level results, task slices,
  latency, tokens, and artifact hashes are published under
  `goodprose-b1-v1.1-baseline-analysis`.
- Exit criteria: registered regression behavior, no model inference, exact
  output-byte reuse, unrelated-score invariance, matched comparison table,
  hard gates, costs, and failure analysis.
- Decision: pass as exploratory evaluator-calibrated evidence. Retrieval v1
  advances over minimal (+17.2761 points, 95% interval +6.8559 to +27.9577,
  hard-gate +12.50 pp) and becomes the next-iteration baseline. It does not
  establish superiority over profile v1 (+0.5444, interval crosses zero).
- Next actions: obtain a bounded Ox Alpha critique, incorporate only verified
  findings, then test the fact-ledger plus verification-pass hypothesis on the
  same cases and model.
- Unresolved risks: retrieval still fails 15 of 24 hard gates, including 14
  cases with omissions, one true fabrication, and one placeholder loss;
  deterministic B1 results cannot substitute for semantic or human judgment.

### 2026-08-22 — Phase 0 checkpoint: Ox baseline-review runtime failure

- Hypothesis: Ox Alpha can provide a bounded independent critique of scorer
  validity, selection logic, and the next experiment without seeing raw outputs
  or acting as judge.
- Evidence: the committed prompt hash, four session IDs, zero-token usage
  records, unchanged repository tree, and a fresh public inventory response
  showing the exact model, 1,048,576-token context, and $0 prices.
- Exit criteria: a nonempty contract-compliant JSON critique with exact
  model/provider provenance and no repository change.
- Decision: fail the optimization. Fresh default and high variants, a fork of
  the earlier successful Ox session, and a minimal `OK` diagnostic all stopped
  with zero input and output tokens. No review exists and none is inferred.
- Next actions: continue the structured local improvement experiment under
  Codex review; retry Ox only at a later natural checkpoint after runtime
  revalidation, without pausing evidence-bearing work.
- Unresolved risks: public inventory presence does not establish live inference
  health; the endpoint may be transiently unavailable or incompatible with the
  current harness request path.

### 2026-08-22 — Phase 0 checkpoint: structured retrieval runner

- Hypothesis: a rubric-isolated `ledger -> draft -> verify -> revise` pipeline
  can reduce retrieval-v1 omissions and unsupported transformations on the same
  model and examples.
- Evidence: committed frozen config and preregistration; deterministic prompt
  builders; complete intermediate output, prompt, hash, latency, and token
  provenance; local endpoint enforcement; 96-call mocked 24-case pipeline; and
  a green 36-test repository suite, Ruff, format, and Pyright.
- Exit criteria: no expected-check or scorer leakage, exact four-step
  provenance, same model/retrieval assets, frozen advancement and efficiency
  gates, and complete engineering verification.
- Decision: pass. The candidate runner is eligible for one real $0 B1 run.
- Next actions: execute at the committed revision, rescore offline under v1.1,
  compare only against the frozen retrieval-v1 baseline, and keep or reject it
  under the preregistered gates.
- Unresolved risks: the 0.5B model may corrupt facts in its own ledger or
  verifier, and four sequential calls can increase latency without improving
  final fidelity.

### 2026-08-22 — Phase 0 checkpoint: structured retrieval iteration one

- Hypothesis: four-stage ledger, draft, verify, and revise inference will reduce
  retrieval-v1 omissions without regressing hard gates.
- Evidence: one frozen 24-case run at revision `b7b98f9`; 96 local calls; exact
  intermediate and final hashes; v1.1 offline scores; 10,000-resample paired
  analysis; preregistered gate results; post hoc stage attribution; and a green
  39-test repository suite, Ruff, format, and Pyright.
- Exit criteria: at least +2 paired points, no hard-gate regression, fewer than
  14 omission cases, bounded error counts, mean latency at most 6,812.086 ms,
  at most 16,800 generated tokens, and $0 cost.
- Decision: reject. The candidate was -3.4589 points (95% interval -10.4503 to
  +3.6694), regressed hard gates by 4.17 percentage points, produced 16 omission
  cases, and narrowly exceeded both efficiency caps.
- Next actions: preregister a two-stage compact-ledger plus single-draft
  candidate. Remove the verifier/reviser that post hoc attribution shows caused
  a -5.9482-point mean loss from draft to final.
- Unresolved risks: the ledger-conditioned draft diagnostic was selected after
  observing results and cannot itself advance; its 15 omission cases still
  regress the baseline despite a higher mean.
