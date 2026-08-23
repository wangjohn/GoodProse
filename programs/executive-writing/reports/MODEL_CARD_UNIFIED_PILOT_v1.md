# Model card: Qwen 0.5B unified-pilot LoRA v1

## Summary

`qwen2.5-0.5b-unified-pilot-lora-v1` is a 5.88 MB LoRA adapter trained locally
on the fixed 4-bit Qwen2.5 0.5B Instruct base. It is a genuine parameter update
for testing GoodProse's profile-conditioned, three-corpus architecture. It is
not a production model and is not evidence of quality on authentic executive
writing.

## Base and update

- Base: `mlx-community/Qwen2.5-0.5B-Instruct-4bit` at revision
  `a5339a4131f135d0fdc6a5c8b5bbed2753bbe0f3`, Apache-2.0.
- Base weight SHA-256:
  `ddffab9cbc7bf6dde941c6724841eeca8981fcfa81ca20ff8efff1396326d153`.
- Framework: MLX-LM 0.31.3 and MLX 0.32.1 on Apple M3 Pro with 18 GiB unified
  memory.
- Update: final eight layers, LoRA rank 8, scale 20, dropout 0, Adam at 1e-4,
  batch size 1, gradient accumulation 2, prompt masking, seed 20260823, and 80
  fixed iterations.
- Adapter SHA-256:
  `3f2826e671c316dca9731179a66299a119ca98c31fefbfad33b747b4c03b2ee6`.
  All 112 adapter tensors are nonzero.

## Training data

The adapter uses `goodprose-project-authored-unified-pilot-v1`: 90 synthetic,
project-owned records from 30 fictional scenario lineages. It contains 54 task
pairs, 22 style targets, and the chosen responses from 14 preference pairs,
balanced across three descriptive profiles and seven genres. Rejected answers
were retained for future experiments but were not used by a preference
objective.

No named-source, external-source, personal, private, B1, B2, Tier C, or human
evaluation material was used. Rights are limited to this project-owned
architecture pilot, with no permission for external redistribution.

## Training evidence

- Run revision: `370739dcae219480a75fc3571ee47e2f31a962bb`.
- Runtime excluding cached snapshot resolution: 27.593 seconds; settled cost
  $0; peak memory 1.471 GiB.
- 10,917 trained tokens; final train loss 0.041.
- Validation loss: 1.417 initially, minimum 0.226 at iteration 60, and 0.253
  at the preregistered final iteration 80.
- Synthetic test loss 0.274; perplexity 1.315.

The rise after iteration 60 is possible overfitting evidence. The final
iteration remains selected because `fixed_final_iteration` was frozen before
training; no checkpoint search was performed.

## Intended and prohibited uses

Permitted: local architecture research, deterministic profile-control checks,
matched base-versus-adapter B1 evaluation, and pipeline reproducibility.

Prohibited claims or uses: production deployment; authentic human preference;
general executive-writing quality; named-person imitation, endorsement, or
fidelity; handling of private material; external weight or dataset
redistribution; or selection based only on synthetic loss.

## Evaluation status and limitations

At publication of this card, genuine-update checks pass but matched B1 and
profile-control inference have not yet run. Synthetic training and test rows
share a renderer family, so low loss can reflect template learning rather than
general task skill. The 0.5B base, 30 scenario lineages, deterministic error
constructions, and repeated formatting patterns sharply limit effective sample
size. B1 is visible search-development data with lexical deterministic scoring,
not sealed or human evidence.

The adapter remains local and ignored under the training run directory. The
committed experiment record contains its exact hash, run evidence, and
reproduction command; no model weights are committed to Git.
