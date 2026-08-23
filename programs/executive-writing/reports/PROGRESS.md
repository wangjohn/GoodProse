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
