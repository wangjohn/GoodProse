# Evaluation suite

RFClear should be evaluated on transformation quality, not on whether it can imitate familiar RFC prose.

## Two evaluation layers

1. **Public development evals** use the `dev_eval` targets in [`targets.json`](targets.json). They are suitable for building the harness, calibrating the rubric, and comparing prompts. They are not a final measure because public RFCs may already be represented in a base model's pretraining data.
2. **Private final evals** use newly collected coding-agent transcripts and human-written gold specs that have never been published or passed through a training pipeline. Keep them under `private/` or in access-controlled storage. This is the number to use for model selection.

The Bytecode Alliance `test_eval` set is an intermediate source-family holdout. It tests generalization to a new RFC culture and domain, but it is still public data and therefore cannot rule out base-model memorization.

## Building a runnable case

Each target currently has `case_status: target_only`. To turn it into a case:

1. Construct or recover an input that plausibly precedes the target: a coding-agent summary, diff explanation, implementation notes, or linked problem statement.
2. Remove facts that are not evidenced by the input from the expected fact inventory. The model must not be expected to guess facts available only in the reference RFC.
3. Have a reviewer write or adapt the gold spec without changing the underlying technical claims.
4. Record required facts, forbidden inventions, acceptable alternatives, and the target's lineage.
5. Validate against [`schemas/eval-case.schema.json`](schemas/eval-case.schema.json).

Do not create train/eval pairs by independently degrading the same RFC into both splits. All derivatives of one RFC, issue, PR, feature, or implementation belong to the same lineage group.

## Scoring

Use [`RUBRIC.md`](RUBRIC.md) for human and model-judge scoring. Keep exact checks for facts that can be expressed deterministically, then use rubric scoring for organization, decision clarity, and useful completeness. Calibrate any model judge against a doubly reviewed human subset before trusting aggregate scores.
