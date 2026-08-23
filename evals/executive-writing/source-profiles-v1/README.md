# Source profiles evaluation v1

This directory defines `source-profiles-v1`, the content-controlled
evaluation definition for the eleven named executive-writing research sources.

- `manifest.json` declares one slice per source profile. Every slice reuses the
  same six project-authored `goodprose-b1-v1` cases so profile comparisons are
  content-controlled:
  - `b1-001-migration-email`
  - `b1-004-hiring-memo`
  - `b1-007-launch-decision-memo`
  - `b1-011-concise-onboarding-revision`
  - `b1-015-europe-strategy-update`
  - `b1-020-cache-blog`

  These cover multiple task families and topics while referencing only public
  benchmark IDs; no case contents are duplicated here.

- Each slice declares topic-swap, leave-topic-out, and leave-time-out
  protocols. Topic-swap variants and time-based splits are explicit current
  limitations pending project-authored variants and collection dating metadata.

- Slices test abstract writing traits and genre competence. They must never be
  used to ask a model to impersonate a person. Run configurations for these
  slices live under `programs/executive-writing/configs/source-profiles/` and
  select the profile-card/retrieval coverage architecture with standalone
  eligibility disabled.

Validate together with the data manifest using
`tests/executive_writing/test_sources.py`.
