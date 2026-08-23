# Ox Alpha assignment: baseline failure and hypothesis review

- Assignment ID: `ox-baseline-failure-review-v1`
- Input classification: `sanitized_project_authored_research_artifacts`
- Intended use: `failure_analysis_and_hypothesis_critique_only`
- Required model: `stealth/ox-alpha`
- Required provider: `openrouter`
- Trusted orchestrator timestamp: `2026-08-23T04:02:28Z`

Read only these repository files:

1. `evals/executive-writing/goodprose-b1-v1/SCORER_CALIBRATION_v1.1.md`.
2. `programs/executive-writing/experiments/b1-v1-initial-baselines.json`.
3. `programs/executive-writing/experiments/goodprose-b1-v1.1-baselines.json`.
4. `programs/executive-writing/experiments/goodprose-b1-v1.1-case-results.jsonl`.
5. `programs/executive-writing/reports/FIRST_EVIDENCE_BASELINES.md`.

Do not modify files, run shell commands, access the network, inspect raw model
outputs, author benchmark cases, generate candidate prose, or act as an LLM
judge. The candidate outputs have already been generated and scored by an
inspectable deterministic evaluator.

Produce one raw JSON object with exactly these top-level fields:

- `assignment_id`
- `model_id`
- `provider`
- `prompt_hash`
- `input_classification`
- `intended_use`
- `scorer_correction_review`: whether the v1.1 scope is defensible, concrete
  residual validity risks, and any test missing from the frozen rules
- `comparison_review`: challenges to the paired statistics, advancement gate,
  retrieval selection, latency/cost reporting, or overclaims
- `failure_review`: the three most decision-relevant failure patterns supported
  by the supplied artifacts
- `hypothesis_review`: critique the proposed fact-and-constraint ledger plus
  verification pass, then rank at most three bounded next experiments
- `stop_or_continue`: the evidence that should cause the next iteration to be
  kept, rejected, or redirected
- `validation_performed`
- `uncertainties`
- `timestamp`

Do not repeat the results tables. Do not invent missing evidence. Treat all
task-family slices as descriptive. This review is research provenance only,
not benchmark evidence, training data, a reference answer, or final grading.
