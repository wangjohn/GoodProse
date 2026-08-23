# Executive-writing program progress

## Current state

- Phase: Phase 2/3 unified candidate evaluation and architecture selection
- Canonical project name: GoodProse
- Program branch: `codex/executive-model-program`
- Settled spend: $0 of $100
- Starting revision: `20c27103de41a495cbe6795432f48e6794a46f6c`
- First-evidence milestone: complete; the 24-case B1 benchmark, three matched
  baselines, shared results, two evidence-driven inference iterations, genuine
  smoke fine-tune, failure analysis, and reproducible engineering checks are
  committed
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

### 2026-08-23 — Phase 1 checkpoint: aggregate-only holdout lifecycle

- Hypothesis: a public protocol can enforce aggregate-only B2 cadence and a
  burn-before-read Tier C lifecycle without exposing hidden cases, outputs,
  rationales, rubrics, or slices to the development checkout.
- Evidence: Ox Alpha drafted the bounded implementation under exact session,
  prompt, response, token, timing, and zero-cost provenance. Codex then audited
  and substantially corrected the trust boundary: registration/content/canary/
  configuration commitments, exact B1 ordinal cadence, verified prior receipt
  chains, hard-gate-aware decisions, cumulative regression semantics, sealed
  signer requirements, confidential raw-byte hashes and sanitized failures,
  contamination/finalist linkage, durable owner-only state, and independent
  recomputation of the frozen Tier C winner.
- Exit criteria: strict schemas; five synthetic example documents and sixteen
  generated schemas; B2 duplicate, cadence, maximum-query, fork, regression,
  and post-block rejection; Tier C three-to-five finalist freeze, exclusive
  opened/completed/retired states, crash consumption, one-shot rejection,
  hard-gate selection, external HMAC authentication, and repository-side
  verification bound to registration/freeze. The focused 38-test suite and
  complete 122-test repository suite pass; Ruff, format, Pyright, JSON checks,
  and `git diff --check` are clean.
- Decision: accept `holdout-lifecycle-v1` as tested public infrastructure and
  synthetic procedural evidence only. No real B2 query or Tier C run occurred,
  and nothing in the repository is genuinely sealed.
- Next actions: integrate tested adapters and reproducible acquisition steps
  for the contracted external evaluations, then build the unified candidate,
  finalist-freeze, and human-packet workflow without touching true Tier C
  material.
- Unresolved risks: a separately controlled evaluator must retain and score
  true hidden content, hold the authenticator key, enforce one durable state
  location per registration, and attest real access separation. A genuinely
  sealed run and final intended-audience human evaluation remain mandatory
  stopping conditions.

### 2026-08-23 — Phase 1 checkpoint: external evaluation adapters v1

- Hypothesis: exact source pins plus strict local adapters can make every
  contracted public compatibility suite reproducible without redistributing
  benchmark content, exposing evaluator-only material to candidates, or
  overstating an adapter test as model evidence.
- Evidence: Ox Alpha drafted the bounded implementation from sanitized public
  metadata only at zero cost. Codex then tested the actual pinned local files
  and corrected four incompatible source-shape assumptions, removed test-only
  verification bypasses, froze the real WritingBench subsets, and separated
  candidate generation by explicit development/full suite. Fresh adaptation
  passes produced 115/107 English-eligible WritingBench cases with 32 frozen
  development cases each; 308 IteraTeR cases; 185/35 EditEval clarity/
  coherence cases; 536 concision cases; and 300 nonempty-prompt YapBench
  compatibility cases. No source rows, criteria, references, predictions, or
  results entered Git.
- Exit criteria: all seven IDs have exact repository/dataset revisions, byte
  hashes, component-level rights/status distinctions, strict frozen models,
  hash-before-parse acquisition, expected source and usable counts, duplicate
  and schema rejection, local evaluator artifacts, candidate-only payloads,
  exact prediction-set validation, deterministic 1,000-resample YapBench
  intervals, safe non-overwriting CLI commands, and public acquisition
  instructions. The 27 focused tests and complete 149-test repository suite
  pass; Ruff lint/format, Pyright, JSON validation, and `git diff --check` are
  clean.
- Decision: accept `external-v1` as tested acquisition and adapter
  infrastructure only. WritingBench remains unexecuted until an exact judge
  configuration is separately frozen. YapBench execution remains blocked by
  missing dataset-license metadata. No leaderboard, quality, finalist, or
  production claim follows from these compatibility checks.
- Next actions: build the reproducible rights-safe unified pilot and the
  common candidate-comparison/finalist-freeze workflow, then use external
  suites only at their registered diagnostic cadence.
- Unresolved risks: public benchmarks may have appeared in model pretraining;
  WritingBench's upstream repository does not pin its judge model version;
  four YapBench prompts and two IteraTeR references are empty after whitespace
  normalization; and public compatibility measures cannot replace authentic
  task-aligned, sealed, or intended-audience human evidence.

### 2026-08-23 — Phase 2 checkpoint: unified pilot compiler and MLX runner

- Hypothesis: a strict compiler and generic local runner can make one
  project-authored, profile-conditioned three-corpus LoRA pilot reproducible
  without weakening smoke validation or allowing a synthetic architecture
  exercise to masquerade as authentic model-quality evidence.
- Evidence: Ox Alpha drafted infrastructure only from the frozen sanitized
  assignment at zero cost and authored no real examples. Codex removed one
  out-of-scope fixture file and strengthened the review boundary with complete
  source-provenance preservation, canonical public-schema commitment, exact
  numerator/denominator ratio evidence, recomputed dataset digests, manifest
  versus config versus disk hash checks, full preference-row equality, and
  independent ID, lineage, split, corpus, profile, rights, and intended-use
  validation.
- Exit criteria: strict 90-record/30-lineage/60-15-15/54-22-14 compilation;
  all-three-corpus materialization; B1 lineage, exact-hash, and 12-word n-gram
  separation; atomic non-overwrite; frozen smoke/unified config pairing;
  preserved failure artifacts and genuine-update proof; backward-compatible
  CLI; no downloads or model calls in tests. The 34 focused tests and complete
  179-test repository suite pass; Ruff lint/format, Pyright, JSON validation,
  and `git diff --check` are clean.
- Decision: accept `ox-unified-pilot-pipeline-v1` after substantial Codex
  corrections as infrastructure only. No pilot source rows exist yet, no
  training ran, and no quality, source-fidelity, production, or redistribution
  claim follows from this checkpoint.
- Next actions: independently author and audit exactly 90 project-owned pilot
  records, compile and freeze the manifest/config at a committed revision, run
  one fixed local MLX LoRA pilot, and compare the exact base and adapter under
  the common candidate workflow before any finalist freeze.
- Unresolved risks: the future source rows remain deliberately synthetic and
  small; float ratios remain present for MLX config compatibility but are now
  backed by exact rational evidence; authentic task pairs, named-source
  training rights, sealed evidence, and intended-audience human review remain
  mandatory for the research contract.

### 2026-08-23 — Phase 2 checkpoint: unified pilot dataset and run freeze

- Hypothesis: 30 fictional scenario lineages rendered across three profiles,
  seven genres, and three explicit corpora are sufficient to test whether the
  hardened pipeline can learn and preserve profile control without using
  external, named-source, private, B1, or hidden material.
- Evidence: 90 locally authored project-owned records; exact 60/15/15 lineage
  splits; 54 task pairs, 22 style targets, and 14 preference pairs; 30 records
  per profile; 12 or 13 per genre; unique hashes for all 90 prompts and chosen
  targets; 11,635 user words and 9,053 target words. Strict compilation passed
  against the committed schema and compiler. Built-in privacy scanner v1 found
  zero findings across all records, and B1 separation found zero shared
  lineages, normalized exact hashes, or contiguous 12-word n-grams.
- Exit criteria: source and derived bodies ignored; compact manifest and
  dataset card committed; project-only rights and architecture-only use
  explicit; exact source/dataset/split/preference/schema/compiler/B1/privacy
  hashes recorded; full materialized-row validation rerun from the frozen
  training config; and no model loaded before the fixed run configuration and
  final-iteration selection rule are committed.
- Decision: freeze `goodprose-project-authored-unified-pilot-v1` and the one-run
  `qwen2.5-0.5b-mlx-lora-unified-pilot-v1` configuration. Use 80 fixed
  iterations on the final eight layers with no checkpoint search. Preference
  rejected responses remain preserved but v1 uses chosen responses for SFT
  only.
- Next actions: commit this freeze, execute the single $0 local MLX run, verify
  genuine nonzero adapter updates and test loss, then bind the final adapter
  hash into the preregistered matched B1 comparison before any inference.
- Unresolved risks: the renderer deliberately repeats profile/genre patterns,
  all scenarios and preferences are synthetic, the exact Codex serving-model
  build was not exposed, and the small dataset cannot establish authentic-task
  quality, human preference, source fidelity, or production readiness.

### 2026-08-23 — Phase 2 checkpoint: genuine unified LoRA update

- Hypothesis: the frozen 90-record mixture can produce a genuine unified LoRA
  update on the same small local base without violating the preregistered
  integrity, resource, or checkpoint-selection boundary.
- Evidence: the exact committed config at revision `370739d` validated the
  manifest, source, four materialized files, every row, counts, ratios, rights,
  intended use, preference equality, IDs, and lineage isolation before model
  loading. The 80-iteration run completed in 27.593 seconds with 10,917 trained
  tokens, 1.471 GiB peak memory, 112 of 112 nonzero adapter tensors, synthetic
  test loss 0.274, and settled cost $0. No training process remains.
- Exit criteria: fixed final iteration 80 selected; no checkpoint search;
  exact 4-bit base revision and weight hash; MLX-LM 0.31.3 / MLX 0.32.1;
  nonempty 5,877,295-byte adapter with SHA-256 `3f2826e…`; complete ignored run
  manifest/log/resolved-config hashes; and a committed experiment record and
  model card that prohibit authentic-quality or production claims.
- Decision: accept the run as the contract's genuine unified controllable-model
  training milestone, pending inference confirmation of profile control. Do
  not advance it from loss: validation reached 0.226 at iteration 60 and rose
  to 0.253 at the frozen final iteration, a possible overfitting signal that is
  preserved rather than selecting iteration 60 after the fact.
- Next actions: generalize the matched MLX evaluator without changing its
  prompts or scoring, bind the exact final adapter hash, commit the evaluation
  config before inference, and run the four preregistered base/adapter ×
  profile/ledger candidates plus a fixed profile-control diagnostic.
- Unresolved risks: low synthetic loss can reflect renderer memorization; B1
  uses an unseen house profile and lexical scoring; the adapter may regress
  factual gates or fail to generalize; authentic, sealed, and human evidence
  remain absent.

### 2026-08-23 — Phase 2 checkpoint: unified matched-evaluation freeze

- Hypothesis: the existing MLX base-versus-adapter evaluator can be generalized
  without changing prompts, decoding, cases, scorer, or historical smoke IDs,
  allowing the unified adapter's causal effect to be measured under the same
  two inference strategies.
- Evidence: strict adapter experiment/lineage pairing for smoke and unified
  runs; exact final adapter, base weight, training revision, B1, profile config,
  retrieval collection, and decoding commitments; deterministic four-candidate
  order; full artifact hashing; training-record cross-validation; paired
  10,000-resample analysis; and a publisher that defers cross-architecture
  leadership rather than inferring it from an exact-base comparison.
- Exit criteria: the unified JSON config and preregistration are frozen before
  inference; crossed adapter lineages fail; historical smoke config remains
  valid; 7 focused evaluator tests and the complete 181-test suite pass; Ruff,
  format, Pyright, JSON validation, and `git diff --check` are clean.
- Decision: commit evaluator SHA-256 `9ac0da6…` and config SHA-256 `fd628da…`,
  then run the exact four candidates once. Advancement requires +2 mean B1
  points with no hard-gate regression in at least one matched strategy, but a
  pass remains exploratory and does not automatically become the architecture
  leader.
- Next actions: execute and independently publish compact per-case hashes,
  paired effects, failure changes, latency, tokens, memory, and cost; inspect
  only permitted B1 outputs after the run for qualitative failure analysis.
- Unresolved risks: visible B1 and lexical scoring remain weak substitutes for
  authentic or human endpoints, and the unified training profile vocabulary
  does not exactly match B1's `executive-house-v1` profile.

### 2026-08-23 — Phase 2 checkpoint: unified matched B1 result and failure audit

- Hypothesis: the fixed unified adapter will improve B1 by at least two points
  without regressing hard gates under either matched profile or ledger-draft
  inference, and permitted-output review will not reveal a disqualifying
  failure hidden by the lexical scorer.
- Evidence: one frozen four-candidate run at revision `d29adab`; 96 local MLX
  generations; exact config, adapter, model, prompt, output, score, and summary
  hashes; 10,000-resample paired intervals; full latency, token, memory, and
  cost records; compact case-level results; permitted-output review; and an
  integrity-bound post-run exact-label/repetition audit with deterministic
  tests and no raw output in the committed result.
- Exit criteria: +2 paired B1 points and no hard-gate regression in at least one
  strategy, followed by qualitative review for scorer-blind failures. Profile
  changed -0.6715 points (95% interval -13.2339 to +11.8394); ledger-draft
  changed +0.6820 (-7.6786 to +9.1114). Neither advanced. The tuned candidates
  introduced frozen training-scenario labels in 20/24 profile and 15/24
  ledger-draft cases versus zero for both exact-base controls; severe
  repetition remained in 10/24 and 8/24 tuned cases.
- Decision: reject the adapter for quality, fidelity, and memorization risk.
  Retain the checkpoint only as genuine unified-training and negative-result
  evidence. Do not retrain on the same synthetic renderer to manufacture a
  win, and do not infer useful profile control from synthetic loss.
- Next actions: complete the common cross-architecture comparison using the
  frozen B1 evidence, formalize the plateau/high-value hypothesis ledger, and
  advance only strong hard-gate-passing diverse candidates toward the B2,
  finalist-freeze, sealed Tier C, and human packet workflow.
- Unresolved risks: every current B1 candidate has substantial deterministic
  or qualitative failures; B1 is visible and lexical; true B2 and Tier C access
  separation, authentic human task evidence, and final intended-audience
  ratings remain absent.

### 2026-08-23 — Phase 3 checkpoint: Ox Alpha quality-ceiling freeze

- Hypothesis: the exact free Ox Alpha endpoint can establish a materially
  stronger source-only quality ceiling than the local compact-ledger leader,
  whose B1 hard-gate pass rate is only 50%, without receiving evaluator or
  hidden material and without acting as teacher or judge.
- Evidence: a zero-cost interface check returned the exact requested object in
  one text event under session `ses_fcfe…`, with verified OpenRouter /
  `stealth/ox-alpha`, high reasoning, OpenCode 1.18.21, 8,092 input and seven
  output tokens, and zero file changes. The frozen runner independently checks
  public inventory and every price field before use, builds prompts from B1
  input fields only, runs each case in an isolated no-tools session, validates
  exported model/provider/version/cost, and commits only compact hashes and
  scores. The resolved agent config is temperature 0, top-p 1, one step, and
  wildcard tool denial.
- Exit criteria: config and prompt freeze before B1 generation; exact model and
  all reported prices remain zero; no expected answers, scorer rules, B2/Tier C,
  private material, or prior outputs cross the provider boundary; single
  candidate per case with retry only before a usable response; matched paired
  comparison to the pinned compact-ledger leader; mocked run/publisher and
  config-drift tests; full engineering verification.
- Decision: freeze `ox-alpha-b1-profile-v1` for one 24-case generation run after
  this checkpoint commit. Advancement requires at least +2 paired points and
  no hard-gate-rate regression, but cannot decide production without privacy,
  deployment, sealed, and human gates.
- Next actions: commit the runner/config, revalidate live inventory, execute the
  approved sanitized transfer, publish the paired result, inspect permitted B1
  outputs for scorer-blind failures, then update the common architecture
  frontier.
- Unresolved risks: a stealth model identifier and zero current price are not
  durable deployment properties; external-provider use may be unacceptable for
  private production inputs; B1 remains visible, lexical, and exploratory.

### 2026-08-23 — Phase 3 checkpoint: Ox Alpha B1 result and output audit

- Hypothesis: the frozen source-only Ox candidate would clear the +2-point
  advancement rule without hard-gate regression and permitted output review
  would reveal no disqualifying scorer-blind artifact or fidelity failure.
- Evidence: 24 isolated OpenRouter / `stealth/ox-alpha` sessions at revision
  `aeb6e1f`; exact config, input, model, provider, OpenCode, prompt, response,
  event, token, latency, and zero-cost provenance; unchanged output SHA-256
  `1092b955…`; corrected v1.1 comparison; preserved invalid first publication;
  and a hash-bound post-run audit that commits no response bodies.
- Exit criteria: the corrected preregistered score cleared the numeric rule at
  +3.8757 paired mean points, with a -0.8240 to +8.7727 interval and unchanged
  50% hard gates. It did not pass every hard gate. Qualitative review found
  step-limit/tool-status preambles in 8/24 outputs, non-source placeholders in
  3/24, run-date metadata in 5/24, and material source-expansion risks in 6/24;
  only 9/24 had no audit flag.
- Correction: the initial publication mixed the Ox v1.1 score with the compact-
  ledger run's original v1 score. It is explicitly invalid. A generation-
  unaffected correction pins the existing compact-ledger v1.1 rescore, and the
  publisher now rejects scorer-version drift.
- Decision: reject the raw candidate for artifact contamination and source-
  grounding risk. Retain the corrected numeric result only as visible-B1
  quality-ceiling diagnostic evidence. Do not post-process the evaluated
  outputs in place.
- Next actions: preregister a fresh Ox harness candidate that removes the one-
  step finalization reminder while preserving tool denial and all provider,
  privacy, cost, and source-only boundaries; rerun B1 once; require both score
  and output-audit gates before common-frontier inclusion.
- Unresolved risks: the deterministic scorer both misses meta/source-expansion
  defects and marks some faithful paraphrases as lexical omissions; Ox remains
  externally hosted and unstable; no candidate passes every B1 hard gate; true
  B2, Tier C, and intended-audience human evidence remain absent.

### 2026-08-23 — Phase 3 checkpoint: Ox Alpha v2 harness freeze

- Hypothesis: the one-step OpenCode ceiling harness caused the v1 finalization
  preambles; allowing two agent steps while continuing to deny every tool will
  remove that artifact contamination without changing model, provider,
  decoding, data boundary, or candidate-resampling policy.
- Evidence: version-bound runner support for the v1 and v2 experiment,
  candidate, prompt, agent, step count, and all-hard-gates policy; a v2 profile
  card that prohibits tool/session/task commentary and unsupported metadata,
  governance, owners, guarantees, workflows, and channels; directly pinned
  corrected v1.1 compact-ledger baseline artifacts; and focused regression
  coverage for cross-version drift and input-only prompt construction.
- Exit criteria: resolved OpenCode 1.18.21 config reports temperature 0, top-p
  1, two steps, and wildcard permission denial; v1 still loads with one step;
  v2 config SHA-256 `85b7994…`, preregistration `7f04562…`, and agent config
  `3d95cb8…`; no B1 generation before this checkpoint commit.
- Decision: freeze `ox-alpha-b1-profile-v2` as a fresh candidate. Common-
  frontier advancement now requires +2 paired mean points, no hard-gate
  regression, all 24 hard gates, zero meta commentary, zero introduced
  placeholders or run-date metadata, and no material source-grounding finding.
- Next actions: commit the freeze, revalidate exact live inventory and zero
  pricing, generate one usable candidate per case, publish the score, run the
  preregistered artifact/source audit, and compare v2 with both v1 diagnostic
  evidence and the local frontier.
- Unresolved risks: the two-step hypothesis may not change first-response
  behavior; stronger prohibitions may reduce readability or lexical recall;
  visible B1 and external deployment limits remain unchanged.

### 2026-08-23 — Phase 3 checkpoint: Ox Alpha v2 result and rejection

- Hypothesis: two maximum agent steps with tools still denied would eliminate
  v1's status preambles and, with stronger generic source instructions, produce
  a candidate that clears every B1 hard gate and the post-run grounding audit.
- Evidence: 24 fresh isolated sessions at effective revision `3ccce83f…`; exact
  model/provider/config/session/event/output provenance; 26,478 input and 5,004
  output tokens; 433.761 seconds summed latency; zero file changes; settled
  cost $0; directly pinned v1.1 compact-ledger comparison; and a hash-bound
  post-run audit with no output bodies committed.
- Provenance correction: the command recorded a wrong 40-character expansion
  of the correct short revision. The clean HEAD was verified during the active
  run. The immutable value and corrected effective revision are both preserved
  under correction SHA-256 `0101245…`; generation was unaffected and usable
  outputs were not resampled.
- Exit criteria: score-only comparison passed at +6.3457 paired mean points,
  +1.7683 to +11.3288 interval, and +4.17 hard-gate percentage points. The
  stricter gate failed because only 13/24 hard gates passed. Artifact-only
  compliance improved from 16/24 to 24/24, meta preambles from 8 to zero,
  run-date insertions from five to zero, and no-audit-flag cases from 9 to 18.
  One non-source placeholder and six material source-expansion risks remained.
- Decision: accept the two-step change as a successful harness repair but
  reject `ox-alpha-b1-profile-v2` as a writing candidate. Retain score and
  latency evidence only as a strong visible-B1 ceiling diagnostic.
- Next actions: publish the common cross-architecture frontier and frozen
  hypothesis ledger. Run a fresh source-verifier/reviser candidate only if that
  analysis establishes it as the final high-value automated hypothesis; do not
  post-process v2 outputs in place.
- Unresolved risks: lexical hard gates undercount faithful paraphrases while
  missing unsupported inference, but the contract still requires every frozen
  hard gate; Ox privacy/deployment remain unresolved; B2, Tier C, and human
  evidence remain unavailable until a finalist qualifies.

### 2026-08-23 — Phase 3 checkpoint: common architecture frontier

- Question: after prompt, retrieval, structured, smoke-training, unified-
  training, and two Ox branches, which candidates remain on the common B1
  quality/fidelity/cost frontier and which hypotheses still have high value?
- Evidence: a hash-bound 13-candidate table under identical 24-case B1 and
  deterministic v1.1 scoring; source pins for the shared first-evidence table,
  unified analysis/audit, and both corrected Ox analyses/audits; schema checks
  for source drift, unique candidates, finalist accounting, and hypothesis-
  frontier linkage; and a fourteen-entry hypothesis registry.
- Result: compact ledger/draft remains the local directional leader at 87.1981
  and 50% hard gates. Ox v2 is the score ceiling at 93.5438 and 54.17% but is
  rejected for grounding. Every fine-tuned candidate is dominated or rejected.
  Zero of thirteen candidates are finalist-ready.
- Decision: plateau is not satisfied because the accepted leader fails hard
  gates and affordable unresolved hypotheses remain. Run `h10`, a fresh Ox
  source-verifier/reviser candidate, next. Keep exactly one larger-local-model
  compact-ledger probe contingent on the h10 result and a resource check.
- Pruning: do not repeat the local 0.5B full verify/revise path, templated smoke
  LoRA, current synthetic unified recipe, Ox one-step harness, or unapproved
  profile-adapter sweep without a new causal factor.
- Next actions: commit the frontier, freeze h10's two-session candidate and
  exact output gates before generation, execute once, and then refresh the
  frontier/plateau decision.
- Unresolved risks: common B1 remains visible and lexical; source-profile
  coverage is only six cases; public suites, B2, Tier C, rights-approved
  authentic training, and human confirmation remain outside current evidence.

### 2026-08-23 — Phase 3 checkpoint: Ox Alpha source-reviser freeze

- Hypothesis: a fresh Ox draft followed by a separate source-only verification
  and revision session can remove unsupported inferred process and preserve
  operative source wording, the dominant residual failures in Ox v2.
- Evidence: a version-bound `draft_revise` runner creates exactly two isolated
  no-tools sessions per case, verifies every exported model/provider/version,
  cost, file-change, event, token, latency, prompt, and output record, and
  commits only final candidate hashes and compact results. The revision prompt
  receives the same B1 input fields plus only its fresh draft; it receives no
  expected answer, scorer, audit finding, previous candidate, B2, Tier C,
  private material, or training example. The legacy single-pass runner rejects
  this configuration. Nine focused tests, Ruff, formatting, and Pyright pass.
- Freeze: candidate/config `ox-alpha-b1-source-reviser-v1`, config SHA-256
  `9c8638b…`, preregistration `ef4652d…`, and OpenCode agent config `aaedc442…`.
  The resolved agent is temperature 0, top-p 1, two maximum steps per stage,
  and wildcard tool denial. No candidate generation occurred before freeze.
- Decision gate: require at least +2 paired mean points, no hard-gate
  regression, all 24 lexical hard gates, artifact-only output, zero introduced
  placeholders or dates, zero material source expansion, and clean privacy,
  rights, leakage, provider, provenance, and cost checks.
- Next actions: commit this freeze, revalidate exact live inventory and all-zero
  pricing, run 48 stage sessions once, publish the deterministic result, perform
  the hash-bound permitted output audit, and refresh the common frontier.
- Unresolved risks: a verifier may preserve or introduce subtle unsupported
  implications and may trade readability for lexical copying; Ox remains an
  unstable external endpoint unsuitable for private production evidence.

### 2026-08-23 — Phase 3 checkpoint: Ox Alpha source-reviser rejection

- Hypothesis: a separate source-only revision session would eliminate Ox v2's
  residual unsupported inference and preserve enough exact operative language
  to pass all 24 deterministic hard gates.
- Evidence: 48 unique OpenRouter / `stealth/ox-alpha` sessions at exact frozen
  revision `3bcecc4c…`; 24 fresh drafts and 24 isolated revisions; all normal
  stops; exact model/provider/OpenCode/config/input/output/event provenance;
  83,094 prompt, 12,304 output, and 33,280 cache-read tokens; 509.579 seconds
  summed stage latency; zero tool events, file changes, or settled cost.
- Score: 93.3607 mean and 54.17% hard gates, +6.1626 paired mean points over
  compact ledger with interval +2.0563 to +10.5460 and 15/2/7 wins/ties/losses.
  The score-only rule passed, but only 13/24 hard gates passed. Versus Ox v2,
  paired mean changed -0.1831 with 8/3/13 wins/ties/losses and unchanged gate
  count; prompt tokens rose 3.14× and latency 1.17×.
- Audit: artifact-only 24/24; zero meta preambles, introduced placeholders, or
  run dates; two material expansion cases and 22/24 no-flag outputs. This
  improves v2's six expansion cases and 18 no-flag outputs, but still fails the
  frozen zero-risk gate.
- Decision: reject h10 and never repair, filter, resample, train on, or promote
  its evaluated outputs. The common frontier now has 14 comparable candidates
  and zero finalists.
- Next actions: execute a resource/model-pin feasibility check for h11, then
  freeze at most one zero-cost larger-local-model compact-ledger candidate.
- Unresolved risks: the accepted local leader still passes only half the hard
  gates; external sources, authentic training approval, B2, Tier C, deployment
  qualification, and intended-audience human evidence remain absent.

### 2026-08-23 — Phase 3 checkpoint: larger-local-model h11 freeze

- Hypothesis: replacing the 0.5B base with a same-family 7B instruct model can
  close the quality/fidelity gap while compact-ledger prompts, retrieval,
  decoding, token limits, cases, scorer, and local-only boundary remain fixed.
- Feasibility: official Ollama `qwen2.5:7b-instruct`, 7.616B parameters,
  Q4_K_M, Apache-2.0; manifest `845dbda0…`, primary blob `2bada8a7…`,
  4,683,087,332 installed bytes. The non-B1 cold smoke completed in 14.038
  seconds, loaded 6.0 GB fully on GPU, retained 24% free memory and zero
  throttled pages, and left 35.09 GiB disk free. Settled cost $0.
- Integrity: the local runner now verifies Ollama 0.9.6, loopback endpoint,
  exact manifest and primary blob, model metadata/license, installed-size cap,
  and at least 30 GiB free disk before generation. Prompt/config comparison
  confirms every non-model factor equals the compact-ledger leader.
- Freeze: candidate `qwen2.5-7b-retrieval-ledger-draft-h11-v1`, config SHA-256
  `44b5934…`, feasibility record `c35d43d…`, and preregistration `cc67047…`.
  No B1 call occurred before this freeze.
- Decision gate: require +2 paired mean points, no hard-gate regression, all
  24 hard gates, zero fabrication/placeholder loss, mean latency at most 60
  seconds, bounded output tokens, artifact-only output, zero material source
  expansion, and clean privacy/rights/leakage/pin/provenance/resource/cost.
- Next actions: commit the freeze; revalidate the exact local identity/resource
  gates; run one 48-call ledger/draft candidate; offline-rescore, audit, and
  refresh the frontier without quality retry or in-place repair.
- Unresolved risks: the non-B1 single-pass smoke added placeholders and
  unsupported follow-ups; a larger model may remain lexically incomplete,
  semantically expansive, or too slow despite fitting memory.
