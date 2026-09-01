# Evaluation Rules

- Freeze test cases before training.
- Never include a test example in an SFT export.
- Compare the prompted base model and fine-tuned candidate on identical inputs.
- Hide system identity during review.
- Treat unsupported facts as a hard failure.
- Record voice preference and expected editing burden separately.
- Keep per-case review records; do not report only an aggregate.
