# Ox Alpha B1 quality-ceiling preregistration v1

Status: frozen before candidate generation.

## Question and boundary

Can the exact free Ox Alpha endpoint provide a materially stronger source-only
candidate baseline than the current local compact-ledger leader on the 24
visible, project-authored B1 cases?

Ox receives only each case's task family, objective, audience, requested output
format, constraints, and source material. It receives no expected facts,
forbidden claims, scorer rules, reference answers, prior outputs, B2/Tier C
content, private material, or human ratings. Ox is the candidate generator only;
it is not a teacher or judge in this experiment and its outputs are not training
data.

## Frozen candidate

- Experiment: `ox-alpha-b1-ceiling-v1`
- Candidate: `ox-alpha-b1-profile-v1`
- Provider/model: OpenRouter / `stealth/ox-alpha`
- Harness: Ori `0.8.0+3511459`, official OpenCode `1.18.21`, high reasoning
- Agent config: `opencode-ceiling-v1.json`, SHA-256 `deadcb6…`
- Decoding: temperature 0, top-p 1, one agent step, tools denied, external
  plugins disabled
- Prompt: deterministic `goodprose-ox-ceiling-prompt-v1` built from B1 input
  fields only
- Attempts: one candidate generation per case. One retry is allowed only after
  a timeout, nonzero harness exit, empty event stream, or empty candidate; a
  nonempty candidate is never resampled.
- Cost: execute only if the public inventory still reports the exact model,
  required capabilities, and every reported price field as zero.

Each of the 24 cases uses a separate session. The runner must validate the
exported model/provider/OpenCode version, zero session and event cost, absence
of file changes and tool calls, exact session/output/prompt hashes, token use,
latency, and completion reason. Raw events and output bodies remain ignored;
only compact hashes, scores, failure labels, and aggregate evidence are
committed.

## Frozen comparison and decision

Primary comparison: `qwen2.5-0.5b-retrieval-ledger-draft-v2` under deterministic
scorer v1.1 on identical B1 cases. Its outputs, scores, and summary are pinned
in `OX_B1_CEILING_v1.json`.

Advance Ox to the common automated frontier only if its paired mean score is at
least two points higher and its hard-gate pass rate does not regress. Report the
10,000-resample paired bootstrap interval, median effect, wins/ties/losses,
dimension means, errors, latency, tokens, and settled cost. Also report whether
all 24 hard gates pass; advancement does not imply production selection.

After scoring, Codex may inspect these permitted B1 outputs for unsupported
claims, prompt leakage, collapse, or other scorer-blind failures and publish a
separate clearly post-run audit. No observed result may change this candidate
in place.

## Validity limits

B1 is a visible, small, lexical, project-authored development benchmark. Ox
Alpha has a stealth identifier, external-provider data boundary, and unstable
availability and pricing. Even a large B1 win is only a quality-ceiling and
candidate-baseline result until privacy, deployment, B2, genuinely sealed Tier
C, and intended-audience human gates are satisfied.
