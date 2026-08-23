# Executive-writing program progress

## Current state

- Phase: Phase 0 feasibility and first-evidence vertical slice
- Canonical project name: GoodProse
- Program branch: `codex/executive-model-program`
- Settled spend: $0 of $100
- Starting revision: `20c27103de41a495cbe6795432f48e6794a46f6c`
- First-evidence milestone: in progress; repository and harness feasibility audited
- Harness preflight: failed closed on 2026-08-22; the read-only smoke passed
  after one retry, but the artifact-contract response violated the RFC 3339
  timestamp requirement. Ox Alpha delegation is disabled and Codex continues
  directly. See `../experiments/2026-08-22-harness-preflight.json`.
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
