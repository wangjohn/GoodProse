# Ox Alpha B1 quality-ceiling preregistration v2

Status: frozen before candidate generation.

## Reason for a new candidate

The v1 candidate's corrected deterministic comparison cleared its numerical
rule, but 8 of 24 responses began with an OpenCode step-limit or tool-status
preamble. Five added the run date, three added a non-source placeholder, and
six had material source-expansion risk. Those evaluated outputs are rejected
and will not be stripped, repaired, or relabeled.

V2 tests the narrow harness hypothesis that two allowed agent steps avoid the
first-step finalization reminder while wildcard tool denial and source-only
generation remain intact. Its prompt also bans invented metadata, governance,
owners, guarantees, workflows, and follow-up channels observed in v1. V2 is a
fresh candidate with fresh sessions and output hashes.

## Question and boundary

Can `stealth/ox-alpha` produce 24 artifact-only, source-grounded B1 responses
that materially outperform the local compact-ledger baseline and pass every
deterministic hard gate when run through the revised no-tools harness?

Ox receives only task family, objective, audience, requested output format,
constraints, and source material from the visible project-authored B1 cases.
It receives no expected facts, forbidden claims, scorer rules, reference
answers, v1 outputs, audit findings, B2/Tier C content, private material, or
human ratings. The v2 generic prompt states behavioral prohibitions but does
not reveal any case-specific evaluator content. Ox remains candidate generator
only, never teacher or judge, and its outputs remain excluded from training.

## Frozen candidate

- Experiment: `ox-alpha-b1-ceiling-v2`
- Candidate: `ox-alpha-b1-profile-v2`
- Provider/model: OpenRouter / `stealth/ox-alpha`
- Harness: Ori `0.8.0+3511459`, official OpenCode `1.18.21`, high reasoning
- Agent config: `opencode-ceiling-v2.json`, tools denied, two agent steps,
  temperature 0, top-p 1
- Prompt: deterministic `goodprose-ox-ceiling-prompt-v2`; return the artifact
  from the first line with no tool/step/session/task commentary; do not add
  sender, recipient, date, placeholder, owner, governance body, approval,
  guarantee, workflow, deadline, commitment, or follow-up channel unsupported
  by the source
- Attempts: one usable generation per case. A single retry is allowed only
  after transport timeout, nonzero harness exit, empty event stream, or empty
  candidate; any nonempty candidate is final and cannot be resampled for
  quality.
- Cost: run only while the public inventory reports the exact model, required
  parameters, and every reported price field as zero.

Each case uses an isolated session. The runner must validate exact exported
model/provider/OpenCode version, zero event and session cost, zero file changes,
absence of tool events, prompt/output/event/session hashes, token counts,
latency, and finish reason. Raw events and output bodies remain ignored; only
compact hashes, scores, and audit evidence may be committed.

## Frozen scoring and artifact gates

Primary score comparison: corrected deterministic-v1.1 artifacts for
`qwen2.5-0.5b-retrieval-ledger-draft-v2`, pinned directly in
`OX_B1_CEILING_v2.json`. Report the paired 10,000-resample interval, median
effect, wins/ties/losses, dimensions, errors, latency, tokens, and settled cost.

V2 enters the common automated frontier only if all conditions hold:

1. paired mean improvement is at least two points;
2. hard-gate pass rate does not regress;
3. all 24 deterministic hard gates pass;
4. no output contains agent, harness, tool, step, session, task-status,
   instruction, or model commentary;
5. no output introduces a placeholder or run-date metadata absent from source;
6. permitted full-output review finds no material unsupported fact, decision,
   owner, governance body, approval, commitment, deadline, guarantee,
   restriction, workflow, or follow-up channel.

The post-run audit will be hash-bound to the exact run, outputs, score analysis,
and compact case results. Literal checks are deterministic; the final source-
grounding condition is an explicitly post-run reviewer judgment. Any failure
rejects the raw candidate while preserving its preregistered score as diagnostic
evidence. Observed results cannot change v2 in place.

## Validity limits

B1 is visible, small, lexical, and project-authored. Two steps test a harness
effect, not a model-version change. A stealth identifier, external-provider
boundary, and current zero price are not durable deployment properties. Even a
full v2 pass establishes only automated development-frontier eligibility;
privacy, deployability, true separated B2, genuinely sealed Tier C, and
intended-audience human evaluation remain mandatory.
