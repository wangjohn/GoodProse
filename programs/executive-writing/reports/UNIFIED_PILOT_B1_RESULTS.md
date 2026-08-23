# Unified pilot matched B1 result

## Outcome

Reject the unified LoRA adapter for quality use. Retain it only as evidence
that the frozen unified training pipeline completed a genuine model update.

The preregistered deterministic comparison did not clear the +2-point
advancement threshold under either inference strategy. A separately declared
post-run audit then found exact fictional training-scenario labels in 20 of 24
profile-prompt outputs and 15 of 24 ledger-draft outputs, compared with zero in
both exact-base controls. This is a memorization and unsupported-claim risk,
not evidence of useful profile control.

## Frozen comparison

All candidates used the same 24 visible B1 cases, deterministic scorer v1.1,
temperature 0, seed 20260822, and pinned 4-bit Qwen2.5 0.5B base weights. The
only weight difference within each pair was the final unified adapter with
SHA-256 `3f2826e…`.

| Strategy | Candidate | Mean | Median | Hard-gate pass | Output tokens | Mean latency |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Profile | Exact base | 71.3900 | 75.8441 | 16.67% | 9,784 | 1,470.6 ms |
| Profile | Unified LoRA | 70.7185 | 72.6965 | 37.50% | 7,369 | 1,627.9 ms |
| Ledger-draft | Exact base | 73.8629 | 73.3232 | 29.17% | 12,780 | 2,163.7 ms |
| Ledger-draft | Unified LoRA | 74.5449 | 74.1624 | 29.17% | 10,114 | 2,434.6 ms |

The profile pair changed by -0.6715 points with a 95% paired bootstrap
interval of -13.2339 to +11.8394 and 11/0/13 wins/ties/losses. The ledger-draft
pair changed by +0.6820 points with an interval of -7.6786 to +9.1114 and
12/0/12 wins/ties/losses. Neither comparison met the frozen advancement gate.

## Post-run failure audit

The diagnostic was specified only after the permitted B1 outputs were
generated. It therefore supplements, but does not alter, the preregistered
score. Its config binds all four output hashes and defines two deterministic
checks:

- An introduced label is a case-insensitive whole-token match to one of the 30
  fictional unified-pilot scenario labels when that label is absent from the
  B1 source material.
- Severe repetition is an exact nonempty line repeated at least four times or
  an exact contiguous four-word n-gram repeated at least eight times.

| Strategy | Candidate | Introduced-label cases | Severe-repetition cases |
| --- | --- | ---: | ---: |
| Profile | Exact base | 0/24 | 16/24 |
| Profile | Unified LoRA | 20/24 | 10/24 |
| Ledger-draft | Exact base | 0/24 | 7/24 |
| Ledger-draft | Unified LoRA | 15/24 | 8/24 |

The tuned outputs introduced labels including `Ember`, `Indigo`, `Lantern`,
`Northstar`, and `Summit` into unrelated B1 cases. Two profile outputs also
showed extreme exact-line repetition: 164 repetitions on `b1-018` and 162 on
`b1-023`. The profile adapter reduced the base model's already poor repetition
count, but that does not offset label leakage in 83.33% of cases. The
ledger-draft adapter both leaked labels in 62.50% of cases and increased the
severe-repetition count by one.

## Decision and limits

The adapter fails the program's memorization, unsupported-claim, and quality
requirements. Do not select its checkpoint, tune around this result, or use
its synthetic test loss as a quality claim. The negative result is still
useful: a 90-record renderer-structured corpus can fit quickly while teaching
scenario-label shortcuts that generalize badly.

The label detector is exact and can miss paraphrased memorization or count a
coincidental whole-token use. The repetition detector is a collapse heuristic,
not a semantic score. B1 is visible, small, synthetic, and project-authored.
These limitations make the result exploratory, but the adapter does not need a
stronger benchmark to be rejected after its observed failures.

Machine records:

- `../experiments/mlx-qwen2.5-0.5b-unified-pilot-b1-v1-analysis.json`
- `../experiments/mlx-qwen2.5-0.5b-unified-pilot-b1-v1-case-results.jsonl`
- `../experiments/mlx-qwen2.5-0.5b-unified-pilot-b1-v1-failure-audit.json`

Reproduce the compact post-run audit with:

```bash
uv run python -m goodprose.executive_writing mlx-eval audit-failures \
  --config programs/executive-writing/configs/training/UNIFIED_PILOT_B1_FAILURE_AUDIT_v1.json \
  --run-dir programs/executive-writing/artifacts/mlx-evaluations/mlx-qwen2.5-0.5b-unified-pilot-b1-v1-20260823T191717Z \
  --cases evals/executive-writing/goodprose-b1-v1/cases.jsonl \
  --output /tmp/unified-pilot-b1-failure-audit.json \
  --generated-at 2026-08-23T19:28:59Z
```
