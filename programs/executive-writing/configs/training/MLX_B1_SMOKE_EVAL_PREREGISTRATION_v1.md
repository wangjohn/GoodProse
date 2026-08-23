# Matched MLX smoke-adapter evaluation v1

Status: frozen after the training run and adapter validation, before any B1
inference with either the MLX base or adapter.

## Question

Does the genuine smoke adapter change visible B1 behavior when the exact same
MLX base, prompts, retrieval examples, decoding, and hardware are used? Compare
both the profile single-pass path and the leading compact-ledger/draft path so
the adapter effect is not confounded with inference architecture.

## Frozen comparison

- Exact base and adapter hashes are recorded in the JSON config.
- Run four candidates in this order: base profile, base ledger/draft, tuned
  profile, tuned ledger/draft. Load the base once per untuned/tuned state.
- Use all 24 B1 v1 cases, deterministic scorer v1.1, temperature 0, seed
  20260822, 512 direct tokens, 192 ledger tokens, and 512 draft tokens.
- Use the existing frozen profile config and retrieval examples. Do not expose
  expected checks or scorer details to the model.
- Report each candidate's mean and median score, hard-gate rate, error counts,
  latency, tokens, peak memory, and $0 cost. Preserve per-case outputs and
  scores locally with hashes.
- For each strategy, report tuned minus base paired mean/median difference,
  win/tie/loss, 10,000-resample paired-bootstrap interval, and hard-gate-rate
  difference using the existing B1 method.

## Interpretation

This is exploratory visible-B1 smoke evidence. The fine-tune was trained on a
small synthetic templated corpus; improvement is not expected and regression
does not invalidate the pipeline. Do not select another checkpoint, change
prompts, or retrain based on this result. A gain of at least two points with no
hard-gate regression is the existing B1 advancement threshold, but even a pass
cannot establish authentic-task quality or production readiness.
