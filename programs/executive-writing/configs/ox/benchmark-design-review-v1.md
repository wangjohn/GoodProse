# Ox Alpha assignment: first-evidence benchmark design review

- Assignment ID: `ox-benchmark-design-review-v1`
- Input classification: `sanitized_public_repository`
- Intended use: `benchmark_design_review_only`
- Required model: `stealth/ox-alpha`
- Required provider: `openrouter`
- Trusted orchestrator timestamp: `2026-08-23T02:26:09Z`

Read only these repository files:

1. `docs/goals/executive-writing-model.md`, concentrating on the first-evidence
   milestone, scorecard, custom benchmark, and error taxonomy.
2. `evals/schemas/eval-case.schema.json`.
3. `src/goodprose/models.py`.
4. `evals/executive-writing/README.md`.
5. `data/voice-profiles/index.json`.

Do not modify files, run shell commands, access the network, or inspect hidden
evaluation material. Produce a single JSON object with these fields:

- `assignment_id`
- `model_id`
- `provider`
- `prompt_hash`
- `input_classification`
- `intended_use`
- `findings`: concrete design findings for a 24-case, project-authored B1
  benchmark covering the contract's highest-value task types
- `coverage_matrix`: proposed counts by task family and adversarial feature
- `schema_gaps`: fields that should exist in a program-specific v1 schema
  without changing shared GoodProse models prematurely
- `deterministic_checks`: checks that can be evaluated without an LLM judge
- `risks`: validity, leakage, rights, and overclaiming risks
- `validation_performed`
- `uncertainties`
- `timestamp`

Do not write benchmark cases, reference answers, training examples, or model
outputs. This is design review, not evaluation evidence or training data.
