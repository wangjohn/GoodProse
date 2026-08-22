# Evaluation suite

GoodProse is evaluated on transformation quality, not resemblance to a named writer.

## Evaluation layers

1. Public development cases exercise deterministic checks and rubric plumbing. Public sources may be present in a base model's pretraining data, so these are not a final quality measure.
2. Private cases use permissioned source material and human-approved outputs that never enter training. Use these for prompt and model selection.
3. A sealed final holdout remains untouched by prompt development, judge calibration, and synthetic-data generation.

## Building a runnable case

Each case specifies source material, channel, audience, objective, constraints, and voice profile. Record required facts, forbidden inventions, any required call to action, acceptable variations, and the complete lineage.

Deterministic checks should cover explicit requirements first. Human reviewers then score factuality, objective fulfillment, audience and channel fit, house style, and overall usefulness. Compare every candidate against a strong prompted baseline using blinded pairwise judgments.

Do not create training and evaluation derivatives from the same underlying email, decision, event, draft history, source document, or public article.
