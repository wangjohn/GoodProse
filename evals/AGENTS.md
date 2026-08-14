# Evaluation Rules

## Goal

Evals measure whether the system converts coding-agent artifacts into high-quality engineering specifications.

The score is not the goal. Reliable measurement is the goal.

## Experimental discipline

Always record:

- source dataset version
- train/eval split version
- model provider and exact model identifier
- prompt version
- system instructions
- decoding parameters
- scorer implementation/version
- judge model identifier, if applicable
- git commit
- timestamp

## Never

- Never train on evaluation examples.
- Never inspect hidden expected outputs while modifying the system.
- Never select eval examples because the current model performs well on them.
- Never modify an existing eval definition without versioning the eval.
- Never let the model being evaluated see judge instructions.
- Never report only the aggregate score; retain per-example results.

## Scoring priority

Prefer, in order:

1. deterministic checks
2. source-grounded checks
3. human labels
4. calibrated LLM judges
5. uncalibrated LLM judges

LLM judges should not be treated as ground truth.

## Model judges

When adding or modifying an LLM judge:

- evaluate it against a human-labeled calibration set
- inspect false positives and false negatives
- use pairwise comparisons when absolute scoring is unreliable
- pin the judge model
- preserve judge explanations for debugging
