# MLX LoRA smoke run v1

Status: frozen before downloading the base weights or starting training on
2026-08-22.

## Question and scope

Can the repository complete one genuine, reproducible fine-tuning run through
dataset validation, model retrieval, parameter update, checkpoint validation,
test-loss evaluation, and run-manifest generation on the available Apple
Silicon machine?

This is a plumbing test. Its 48 deterministic synthetic examples cannot
establish model quality, profile generalization, or production readiness.

## Frozen run

- Base: `mlx-community/Qwen2.5-0.5B-Instruct-4bit` at immutable revision
  `a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3`, derived from
  `Qwen/Qwen2.5-0.5B-Instruct`; Apache-2.0.
- Framework: `mlx-lm==0.31.3`, MLX `0.32.1`.
- Data: `goodprose-project-authored-smoke-v1`, with the exact manifest and
  split hashes in the JSON config; 32 train, 8 validation, and 8 test records.
- Corpus mix: 100% `task_pairs`; zero `style_targets` and `preference_pairs`.
- Update: LoRA on the 4-bit base, last four transformer layers, rank 8, scale
  20, dropout 0, Adam, learning rate 1e-4, batch size 1, seed 20260822, prompt
  masking, and maximum sequence length 1,024.
- Budget: exactly 40 iterations; validation every 10 iterations; save every 20;
  evaluate the complete synthetic test split after training; 30-minute timeout.
- Selection: use the final iteration fixed in advance. Do not choose a
  checkpoint after viewing B1 or test generation quality.
- Cost: local Apple M3 Pro only, settled provider cost $0. No paid service.

## Pass and failure rules

The plumbing run passes only if it produces a nonempty Safetensors adapter with
at least one nonzero tensor, reports a positive trained-token count, completes
test-loss evaluation, and writes exact configuration, base-model, dataset,
adapter, version, timing, memory, revision, and cost evidence.

Any download, Metal, memory, timeout, training, or artifact-validation failure
is preserved as a failed run rather than silently retried with changed
hyperparameters. A retry after an environmental repair keeps this experiment
configuration and receives a new run ID. No result from this run is a quality
claim, even if B1 improves.
