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

### 2026-08-22 — Phase 0 checkpoint: compact ledger-draft runner

- Hypothesis: removing the harmful verifier/reviser and constraining the ledger
  to compact atomic source items can retain the draft-stage signal while
  avoiding the omission and efficiency regressions from iteration one.
- Evidence: newly frozen candidate config and preregistration; 192/512 per-step
  token limits enforced in the local request; source-authoritative prompts with
  no rubric leakage; complete two-step provenance; and a green 41-test
  repository suite, Ruff, format, and Pyright.
- Exit criteria: evidence-driven change isolated to the two-stage pipeline,
  exact per-step limits and provenance, frozen comparison/error/efficiency
  gates, same model and retrieval data, and complete engineering verification.
- Decision: pass. The v2 candidate is eligible for one regenerated $0 B1 run.
- Next actions: execute at the committed revision, score offline under v1.1,
  and compare with retrieval v1 using the frozen gates.
- Unresolved risks: even a compact ledger is model-generated and can omit or
  alter facts; the prior draft signal was post hoc and its confidence interval
  included zero.

### 2026-08-22 — Phase 0 checkpoint: compact ledger-draft iteration two

- Hypothesis: a regenerated compact ledger plus single draft will clear the
  practical-effect gate without hard-gate, fidelity, or efficiency regression.
- Evidence: one frozen 24-case run at revision `6920e65`; 48 local calls; exact
  intermediate/final hashes; offline v1.1 scoring; paired bootstrap; all frozen
  gates; step-level latency/tokens; and a green 42-test repository suite, Ruff,
  format, and Pyright.
- Exit criteria: +2 paired points, at least 37.50% hard gates, at most 14
  omission/one fabrication/one placeholder-loss cases, mean latency at most
  4,257.554 ms, at most 9,450 generated tokens, and $0 cost.
- Decision: keep as the directional B1 leader. It gained +2.3698 points,
  increased hard-gate pass to 50.00%, reduced omissions to 12, eliminated the
  registered fabrication and placeholder-loss errors, and passed every frozen
  efficiency/cost guardrail.
- Next actions: build a separate project-authored smoke-training corpus and run
  a genuine small-model update; compare the tuned checkpoint under matched
  single-pass and leading two-stage inference.
- Unresolved risks: the paired interval (-2.0211 to +6.7390) includes zero;
  twelve hard-gate failures remain; B1 is visible, lexical, and not authentic
  human rough-to-final evidence.

### 2026-08-22 — Phase 0 checkpoint: smoke-training corpus

- Hypothesis: a deterministic project-owned corpus can prove the real MLX
  fine-tuning path without using B1, private material, or unresolved
  named-source rights.
- Evidence: 48 MLX-compatible chat records across 12 fictional scenario
  lineages and four output formats; lineage-isolated 32/8/8 train/valid/test
  splits; exact file and dataset hashes; and a normalized exact plus 12-word
  n-gram contamination scan against all 24 B1 inputs with zero matches.
  The complete repository suite passed: 46 tests, Ruff lint and format, and
  Pyright.
- Exit criteria: reproducible ignored JSONL, committed provenance manifest,
  explicit smoke-only rights scope, B1 isolation, no imported or named-source
  material, and a training dependency pinned to `mlx-lm[train]==0.31.3`.
- Decision: pass for pipeline validation only. The corpus may be used for one
  genuine local smoke update and cannot support a quality or production claim.
- Next actions: freeze the MLX LoRA configuration and run manifest, execute one
  bounded Apple-Metal training run, then compare untuned and tuned inference
  under matched prompts on the disjoint smoke test and B1.
- Unresolved risks: only twelve independent synthetic lineages and four
  deterministic templates are represented; model download availability and
  actual Metal memory/throughput remain unmeasured until the real run.

### 2026-08-22 — Phase 0 checkpoint: MLX smoke-training runner

- Hypothesis: a frozen local runner can preserve a real adapter update and all
  evidence required to distinguish a genuine fine-tune from a configuration
  or inference-only artifact.
- Evidence: pinned base repository and immutable revision; fixed 40-iteration
  LoRA configuration; dataset/right/hash validation; local model resolution;
  complete base and adapter hashing; parsed train/validation/test metrics;
  nonzero-tensor validation; failure manifests; and a mocked end-to-end run.
  The complete suite passed: 50 tests, Ruff lint and format, and Pyright.
- Exit criteria: no post-result checkpoint selection, no overwrite of prior
  attempts, exact framework/data/model/config evidence, bounded timeout, $0
  cost, weights ignored by Git, and deterministic mocked validation.
- Decision: pass. The runner and preregistration are eligible for exactly one
  real local Apple-Metal smoke run at the committed revision.
- Next actions: download the 278 MB pinned base snapshot, execute the frozen
  run, preserve success or failure, and inspect that no task-owned compute
  remains active.
- Unresolved risks: Metal is intentionally unavailable inside the filesystem
  sandbox, so real training requires an approved unsandboxed local command;
  measured runtime and peak unified memory are not yet known.

### 2026-08-22 — Phase 0 checkpoint: genuine MLX smoke fine-tune

- Hypothesis: the frozen local run will complete a real parameter update and
  produce validated inference-loadable adapter artifacts within the machine's
  memory and time envelope.
- Evidence: revision `dafa8f0`; exact 278,064,920-byte base weight; 4,198
  trained tokens; train loss 1.421 at the first report to 0.099 at iteration
  40; validation loss 1.891 before training to 0.168; synthetic test loss
  0.190; 1.075 GB peak memory; 20.862 seconds excluding download; and a
  2,938,645-byte adapter with all 56 tensors nonzero. No training process
  remained active afterward and settled provider cost was $0.
- Exit criteria: positive training tokens, nonempty/nonzero adapter, complete
  synthetic test-loss evaluation, exact hashes and versions, bounded runtime,
  ignored weights, preserved run manifest, and no leftover process.
- Decision: pass the contract's genuine smoke fine-tune requirement. Treat all
  loss values as templated-corpus plumbing evidence, not writing-quality proof.
- Next actions: run the newly frozen exact-base versus exact-adapter B1
  comparison under both profile and compact-ledger/draft inference.
- Unresolved risks: the adapter is locally stored and reproducible but not
  distributed; synthetic-template loss may reflect rapid template fitting and
  says nothing about authentic executive-writing preference.

### 2026-08-22 — Phase 0 checkpoint: matched MLX B1 evaluation runner

- Hypothesis: exact-base versus adapter comparisons under two matched inference
  strategies can isolate the smoke update's behavioral effect without
  checkpoint or prompt selection after viewing B1 outputs.
- Evidence: frozen base/adapter/cases hashes, deterministic decoding, exact
  existing profile and retrieval prompts, per-step provenance, direct v1.1
  scoring, paired bootstrap analysis, local-only raw outputs, and a mocked
  runner. The complete suite passed: 54 tests, Ruff, format, and Pyright.
- Exit criteria: four fixed candidates, same base and prompts within each
  strategy, no rubric leakage, complete score/latency/token/memory evidence,
  fixed final adapter, and explicit exploratory interpretation.
- Decision: pass. Execute one $0 B1 comparison at this committed revision.
- Next actions: preserve every output and comparison, publish the shared
  first-evidence table and failure analysis, then choose the next hypothesis
  from measured errors rather than synthetic loss.
- Unresolved risks: MLX and Ollama packaging differ, so the matched MLX base is
  the causal fine-tune baseline while earlier Ollama candidates remain useful
  architecture references rather than exact weight-controlled comparators.

### 2026-08-22 — First-evidence checkpoint: smoke adapter evaluation

- Hypothesis: the small genuine adapter may change B1 behavior, but only an
  exact base-versus-adapter comparison can determine the direction without
  confounding the inference wrapper.
- Evidence: four frozen 24-case candidates at revision `b6da535`; 144 local MLX
  generations; exact output, score, prompt, adapter, model, config, and run
  hashes; v1.1 case scoring; 10,000-resample paired intervals; latency, token,
  and memory metrics; qualitative permitted-output review; and no remaining
  inference process. Total runtime was 158.463 seconds and cost was $0.
- Exit criteria: all four candidates complete, exact artifact verification,
  matched comparisons for both strategies, negative results retained, shared
  machine/human table, failure analysis, and no quality claim from smoke data.
- Decision: reject the smoke adapter for quality use and retain it only as
  proof of genuine fine-tuning plumbing. Profile regressed -3.4870 points and
  hard gates fell 16.67 percentage points. Ledger/draft regressed -13.6092
  points (95% interval -21.1011 to -6.3146) and hard gates fell 25 points.
  The untuned compact-ledger/draft v2 candidate remains the directional B1
  leader at 87.1981 and 50.00% hard gates.
- Next actions: stop synthetic template fitting; prioritize B2/Tier C
  infrastructure, evaluator validity, rights-safe authentic task pairs, and
  the contracted source/evaluation coverage before another unified update.
- Unresolved risks: lexical scoring misses semantic example-fact leakage; the
  current leader still fails 12 of 24 hard gates; no authentic human endpoint,
  sealed evidence, or production recommendation exists yet.

### 2026-08-23 — Phase 0 checkpoint: all-eleven source and rights artifacts

- Hypothesis: Ox Alpha can accelerate bounded public-source discovery and
  mechanical artifact construction while Codex retains source verification,
  rights classification, integration review, and final decision authority.
- Evidence: exact `stealth/ox-alpha` source-discovery and implementation
  sessions; pinned prompts and response hashes; zero settled cost; independent
  Codex checks of the retained canonical routes; one typed manifest containing
  all eleven people exactly once; eleven descriptive profile specs; eleven
  conservative rights assessments; eleven common six-case evaluation slices;
  and eleven source-specific profile-card coverage configs.
- Review corrections: removed weakly attributed newsrooms, secondary and
  unretrieved government routes, unsupported quantitative archive claims, and
  an unverified author-position claim; narrowed `permission_required` uses to
  metadata audit and source-text-free profile evaluation; rejected Ox's
  incorrect generated timestamp; and added exact cross-artifact and provenance
  validation.
- Exit criteria: no `training_approved` source; no corpus bodies, public email,
  private data, or hidden evaluation material; exact Ox model/provider/prompt/
  response/time/cost provenance; frozen standalone threshold; explicit
  blockers; and 20 focused source-artifact tests plus lint, format, and Pyright
  passing after Codex corrections. Required corpus validation and the complete
  75-test repository suite also pass; Ruff lint/format and Pyright are clean.
- Decision: accept the source/right/profile artifact milestone. Treat traits
  as testable hypotheses, not identity replicas or human-confirmed analysis.
  Treat configured slices as coverage definitions, not model-quality evidence.
- Next actions: execute the eleven source-text-free profile-card coverage runs
  on the shared B1 slice, then implement B2 aggregate-only and Tier C one-shot
  lifecycle infrastructure.
- Unresolved risks: nine statistically promising or unknown sources still
  require rights promotion and measurement before training; Bezos and Jassy
  are clearly insufficient for standalone adapters; topic swaps and
  leave-time-out cases remain unbuilt; no public-email corpus was verified.

### 2026-08-23 — Phase 0 checkpoint: all-eleven source-profile coverage

- Hypothesis: every descriptive profile can execute as a source-text-free
  prompt-time control on identical project-authored content with complete
  provenance and without identity, retrieval, or rights leakage.
- Evidence: Ox Alpha drafted the runner under exact session and prompt/response
  provenance; Codex corrected and froze it at revision `c472575`; the local
  matrix completed exactly 72 calls (twelve candidates by six cases) in 157.0
  seconds with zero settled cost. The offline publisher rebuilt every prompt,
  verified all prompt/output/artifact hashes, independently recomputed every
  v1.1 score, and published 72 source-text-free case records.
- Result: all eleven profiles are executable. The house control scored 85.3381
  with 33.33% hard gates. Directionally, Technical Link Commentary was highest
  at 93.5057 and 66.67% hard gates (+8.1677 paired points); Conversational
  Essay Memo, Policy Polemical Analysis, Institutional Narrative Letter, and
  Operational Executive Update also had positive six-case paired means.
- Exit criteria: exact candidate/case order, no third-party source text or
  retrieval, no requested-person names or source IDs in prompts, v1.1 scoring,
  independently verified compact publication, all eleven retained, and no
  advancement claim from the visible six-case slice.
- Decision: pass the coverage milestone only. No profile advances, becomes a
  production default, or changes the directional 24-case B1 leader. Continue
  to label the apparent ranking exploratory and retain every profile.
- Next actions: implement B2 aggregate-only reporting and Tier C one-shot
  lifecycle controls, then add external-evaluation adapters before another
  unified-model update.
- Unresolved risks: n=6 is small and visible; topic-swap and leave-time-out
  controls are absent; deterministic scoring is lexical; several profiles
  increased rewriting or fabrication errors; and no named source is approved
  for training.
