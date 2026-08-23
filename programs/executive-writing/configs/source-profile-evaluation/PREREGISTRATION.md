# Preregistration: source-profile coverage run v1

Status: frozen before any generation call. Assignment:
`ox-profile-coverage-runner-v1`.

## Hypothesis

Each of the eleven descriptive executive-writing profiles is executable as a
prompt-time profile card, provenance-complete, and directionally distinct from
the GoodProse house profile under identical project-authored content.

## Design

- Twelve candidates: the GoodProse house-profile control
  (`qwen2.5-0.5b-profile-v1`) plus one descriptive profile-card candidate per
  committed source profile, in manifest order.
- Exactly six frozen shared B1 cases per candidate in manifest order:
  `b1-001-migration-email`, `b1-004-hiring-memo`,
  `b1-007-launch-decision-memo`, `b1-011-concise-onboarding-revision`,
  `b1-015-europe-strategy-update`, `b1-020-cache-blog`.
- One local Ollama generation call per candidate/case: exactly 72 calls.
  Model, endpoint, hashes, decoding (temperature exactly zero), timeout,
  license, and Ollama version are pinned by
  `configs/baselines/qwen2.5-0.5b-profile-v1.json`. Settled cost is zero.
- Descriptive prompts contain only the production name, description, trait
  strings, anti-impersonation limits, GoodProse safety rules, and the
  project-authored task. No person names, source URLs, source IDs,
  third-party text, retrieved examples, rubric material, or prior results are
  ever prompted. Retrieval is disabled.

## Primary outputs

Per-candidate mean development score, hard-gate pass rate, error counts, and
paired mean/median difference plus win/tie/loss versus the house control on
the same six cases. Any bootstrap interval is exploratory only.

## Hard constraints

- Scoring uses `score_output_v1_1` only; the model never sees rubric or
  reference material. The publisher rebuilds every prompt and independently
  rescores every saved output before publishing compact results.
- n=6 coverage evidence can never advance a candidate, set a production
  default, or satisfy the model-quality stopping condition.
- All eleven profiles remain in the program regardless of score.
- Raw artifacts stay in ignored output directories; committed publications
  carry compact statistics only, with no generated text.

## Known limitations

Topic-swap variants and leave-time-out splits do not exist for these six
cases yet, so trait effects are not separated from topic or time effects.
All comparisons are exploratory.
