# Named source manifest v1

`named-sources-v1.json` is the machine-readable manifest for the eleven named
executive-writing research sources. It contains, for each person:

- source audit and evidence routes (only collections whose canonical routing
  or authorship was independently supported by an official page);
- a data-availability report evaluated against the frozen default standalone
  threshold of 50,000 effective clean training-approved tokens, 100
  independent examples, three relevant genres, and 30 independent held-out
  cases;
- a provisional rights assessment with approved uses, evidence URL, reviewer
  role and date, unresolved questions, and promotion authority;
- an abstract, non-identity profile specification with a descriptive
  production-facing name, two to five testable traits, and anti-impersonation
  limits;
- a content-controlled evaluation subset referencing six shared project-authored
  B1 case IDs plus protocol declarations or explicit current limitations;
- a reference to the source-specific run configuration under
  `programs/executive-writing/configs/source-profiles/`.

## Provenance and boundaries

- Assignment: `ox-source-artifacts-implementation-v1`
- Drafted by: `stealth/ox-alpha` via OpenRouter through Ori/OpenCode, pending
  Codex review. Session timestamps belong in the experiment record, not here.
- Public metadata only; no corpus bodies, copied passages, quoted text, email,
  litigation exhibits, or distinctive phrases are stored here.
- No verified authored public-email collection was found for any profile.
- Nothing in this manifest is `training_approved`. Only the user or qualified
  counsel may promote a source; every record is `permission_required` except
  Pluralistic, which is `evaluation_only` under its official terms.
- Validate the manifest together with the evaluation manifest and all eleven
  run configs via `tests/executive_writing/test_sources.py`.
