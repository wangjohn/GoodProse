# Unified profile-conditioned MLX LoRA pilot v1

Status: frozen before the training configuration's commit and before model
loading or training.

## Question and scope

Can one small genuine LoRA update consume the frozen task-pair, style-target,
and preference-chosen mixture, preserve three explicit profile controls, and
complete the full integrity and evaluation path on the available Apple Silicon
machine? This is an architecture pilot, not an authentic-task quality run.

## Frozen run

- Base: `mlx-community/Qwen2.5-0.5B-Instruct-4bit` at immutable revision
  `a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3`, derived from
  `Qwen/Qwen2.5-0.5B-Instruct`; Apache-2.0.
- Framework: `mlx-lm==0.31.3`, MLX `0.32.1`; local Apple M3 Pro with 18 GiB
  unified memory; settled provider cost exactly $0.
- Data: `goodprose-project-authored-unified-pilot-v1` at the exact manifest,
  source, dataset, split, preference, compiler, schema, and B1 hashes recorded
  in the committed config and manifest. The 60/15/15 splits contain 54 task
  pairs, 22 style targets, and 14 preference chosen responses overall.
- Update: LoRA on the final eight transformer layers, rank 8, scale 20,
  dropout 0, Adam, learning rate 1e-4, batch size 1, gradient accumulation 2,
  prompt masking, maximum sequence length 1,536, and seed 20260823.
- Budget: exactly 80 optimizer iterations, report every 10, validate every 20,
  save at iteration 80, and evaluate the complete synthetic test split after
  training. Timeout is 60 minutes.
- Selection: `fixed_final_iteration` only. Do not search checkpoints, alter the
  mix, or change hyperparameters after inspecting loss or B1 behavior.
- Preference scope: chosen responses participate in supervised LoRA training;
  rejected responses and reason labels are preserved but no DPO or preference
  objective runs in v1.

## Pass and failure rules

The run passes as genuine training plumbing only if all config/manifest/source/
split/preference and materialized-row checks pass, the log reports positive
trained tokens and test loss, the final Safetensors adapter is nonempty and has
at least one nonzero tensor, and the run manifest preserves exact config,
model, dataset, revision, runtime, timing, memory, and zero-cost evidence.

Any validation, model, Metal, memory, timeout, training, or artifact failure is
preserved as a failed run. An environmental repair may rerun this exact config
under a new run ID; scientific hyperparameter changes require a new version.

## Frozen evaluation policy

After successful adapter validation, create a machine config that binds the
fixed final adapter and base-weight hashes. Before any B1 inference, commit
that config and run four matched candidates in this fixed order: base profile,
base compact-ledger/draft, unified adapter profile, unified adapter
compact-ledger/draft. Reuse the existing profile/retrieval prompts, all 24 B1
cases, scorer v1.1, deterministic decoding, seed 20260822, and the existing
512/192/512 token limits. Report paired 10,000-resample intervals and hard-gate
differences. No result from the synthetic pilot can establish authentic model
quality or production readiness.
