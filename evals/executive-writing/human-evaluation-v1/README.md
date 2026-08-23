# Intended-audience human evaluation v1

Status: protocol implemented and tested; no study is registered, no candidate
packet is frozen, and no human rating has been requested or collected.

This protocol is Tier D. It may start only after three to five diverse
candidates pass every automated fidelity, privacy, rights, leakage, and
deployment gate; the frozen selection rule must then choose two or three
candidate artifacts for the packet. The current B1 frontier has zero eligible
candidates, so creating a packet now would violate the research contract.

## Raters and task

Recruit intended-audience raters in three cohorts: founders or executives,
technical leaders, and experienced business editors. Store only pseudonymous
rater IDs in evaluation artifacts. Raters see the source material, audience,
communication objective, constraints, and one or two opaque-labeled outputs.
They never see the model, provider, training method, profile source, or named
research source.

Use 50–100 difficult representative cases after a documented power analysis.
Seek at least three ratings for every assigned output. Randomize and balance
pairwise first/second position. The assignment manifest and candidate-identity
mapping remain private; the public registration binds them by SHA-256.

## Required rating

Every output receives exactly one operational label:

- `publishable`
- `minor_edits`
- `substantive_edits`
- `unacceptable`

The primary endpoint is `publishable + minor_edits`. Raters also record
editing minutes, structured error labels, and a critical-factual-error veto.
A critical factual error forces `unacceptable`. Pairwise comparison permits
`preferred_first`, `preferred_second`, `tie`, or `both_unacceptable`.

The aggregator reports operational rates, critical-error rates and vetoed
assignments, edit burden, structured errors, pairwise preference counts,
pairwise exact operational-label agreement, and intended-audience cohort
subgroups. Candidate identities stay unresolved until the aggregate is frozen.
The final study analysis must add preregistered confidence intervals and the
power analysis; it must also calibrate any final model judge against these
human results without retuning the frozen candidates.

## Commands

```sh
uv run python -m goodprose.executive_writing human-eval validate-registration \
  --registration <private-registration.json>

uv run python -m goodprose.executive_writing human-eval aggregate \
  --registration <private-registration.json> \
  --ratings <private-ratings.jsonl> \
  --output <ignored-aggregate.json> \
  --generated-at <UTC-timestamp>
```

Private case manifests, assignments, identity maps, rating rows, and any
source/output packets belong outside the agent-readable repository or in the
ignored private evaluation boundary. Never use ratings or Tier D cases to
modify the frozen candidates in place.
