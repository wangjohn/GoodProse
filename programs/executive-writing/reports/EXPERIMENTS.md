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

For each run, record the hypothesis, candidate and baseline identifiers,
dataset and evaluation versions, prompt and decoding configuration, code
revision, hardware or provider, cost, paired results, confidence intervals,
failure analysis, and keep/reject decision. Link to the corresponding
machine-readable manifest under `../experiments/`.
