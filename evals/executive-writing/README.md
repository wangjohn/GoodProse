# Executive-writing evaluations

This namespace contains GoodProse program evaluation definitions and adapters.
Use public development cases for iteration, a sealed private holdout exactly
once per version after finalists are frozen, and a blinded human evaluation for
the final production recommendation.

Public definitions and acquisition adapters may be committed. Hidden answers,
private cases, and generated result payloads belong in the ignored `private/`
and `results/` directories. Follow `evals/AGENTS.md` for every evaluation.
