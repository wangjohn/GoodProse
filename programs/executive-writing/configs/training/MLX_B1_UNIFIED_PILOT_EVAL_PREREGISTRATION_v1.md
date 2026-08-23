# Matched MLX unified-pilot adapter evaluation v1

Status: frozen after the fixed training run and adapter validation, before any
B1 inference with either the exact MLX base or unified adapter.

## Question

Does the genuine unified three-corpus adapter improve or complement visible B1
behavior when the exact base, prompts, retrieval examples, decoding, scorer,
cases, and hardware are held constant? Compare both the profile single-pass
and compact-ledger/draft paths so the adapter effect is separated from the
inference architecture.

## Frozen comparison

- Bind the final iteration-80 adapter SHA-256
  `3f2826e671c316dca9731179a66299a119ca98c31fefbfad33b747b4c03b2ee6`
  and the exact base weight hash in the JSON config.
- Run four candidates in this order: base profile, base ledger/draft, unified
  adapter profile, unified adapter ledger/draft. Load the base once per
  untuned/tuned state.
- Use all 24 B1 v1 cases, deterministic scorer v1.1, temperature 0, seed
  20260822, 512 direct tokens, 192 ledger tokens, and 512 draft tokens.
- Reuse the existing frozen profile config, retrieval examples, and prompt
  builders byte-for-byte. Do not expose expected checks or scorer details to
  the model.
- Report each candidate's mean and median development score, dimensions,
  hard-gate pass rate, error counts, latency, token counts, peak memory,
  length finishes, and $0 cost. Preserve per-case outputs and scores locally
  with exact hashes.
- For each strategy, report tuned-minus-base paired mean and median difference,
  win/tie/loss, the existing 10,000-resample paired-bootstrap interval, and
  hard-gate-rate difference.

## Selection and interpretation

The existing B1 advancement rule is at least +2 mean points with no hard-gate
regression. Preserve a negative result. Do not select another checkpoint,
change prompts, alter decoding, retrain, or omit a candidate after seeing
outputs. The publisher may label the adapter as exploratory-keep only if at
least one matched strategy meets that rule; cross-architecture leadership is a
separate analysis against the retained retrieval and structured baselines.

This is visible-B1 exploratory evidence. The adapter was trained on a small,
synthetic, renderer-structured dataset, and B1 uses an unseen house profile.
Neither a gain nor a loss establishes authentic-task quality, production
readiness, named-source fidelity, sealed performance, or human preference.
