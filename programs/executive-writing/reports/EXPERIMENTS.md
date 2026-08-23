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

For each run, record the hypothesis, candidate and baseline identifiers,
dataset and evaluation versions, prompt and decoding configuration, code
revision, hardware or provider, cost, paired results, confidence intervals,
failure analysis, and keep/reject decision. Link to the corresponding
machine-readable manifest under `../experiments/`.
