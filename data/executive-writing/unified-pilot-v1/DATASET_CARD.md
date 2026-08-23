# Dataset card: unified architecture pilot v1

## Intended use

`goodprose-project-authored-unified-pilot-v1` is a small, project-owned,
synthetic dataset for testing GoodProse's three-corpus compilation,
profile-conditioning, local MLX LoRA training, and matched base-versus-adapter
evaluation path. Its only permitted status is
`unified_profile_conditioning_architecture_pilot_only`.

It is not authentic human writing, named-source data, production-quality
training data, or evidence that a model handles real rough executive material.
It does not grant external redistribution rights for source rows, derived rows,
or resulting adapters.

## Composition

- 90 records from 30 fictional, independent project scenarios.
- 60 train, 15 validation, and 15 test records; each three-record scenario
  lineage remains wholly inside one split.
- 54 task pairs, 22 style targets, and 14 preference pairs. Preference chosen
  responses enter supervised training; all 14 rejected responses and reason
  labels remain in the separate ignored preference file for future use.
- 30 records for each of `concise-decision-v1`,
  `technical-explanatory-v1`, and `operational-update-v1`.
- Seven genres with 12 or 13 records each: email, memo, strategy document,
  engineering document, blog post, short post, and revision.
- User prompts contain 11,635 whitespace-delimited words. Chosen targets
  contain 9,053 words; target length ranges from 85 to 128 words with median
  98. Every normalized user prompt and chosen target has a unique hash.

## Creation and provenance

The Codex primary agent authored 30 fictional scenario fact packets and a
deterministic local renderer under
`goodprose-unified-pilot-content-v1`. Each scenario supplies evidence,
constraint, risk, proposed decision, action, owner role, and deadline. The
three related rows vary profile, genre, and corpus while retaining a shared
lineage. No public, private, named-person, benchmark, customer, email, or
external-source text was used.

The source JSONL, local authoring script, compiled chat rows, and privacy report
remain ignored. The committed manifest pins their hashes, the compiler and
schema hashes, exact counts and rational ratios, and the B1 benchmark bytes.
The runtime identified the author as an OpenAI Codex primary agent based on
GPT-5 but did not expose a more specific serving-model build; that limitation
is recorded rather than inventing a model version.

## Rights, privacy, and isolation

- Ownership: `project_owned`.
- Rights: `training_permitted_project_owned_architecture_pilot`.
- Named sources: 0.
- External sources: 0.
- Personal/private records: 0.
- Built-in privacy scanner v1: 90 records, 0 findings; the ignored report hash
  is `983fabd2110edbb1faa10c3f16e6c58a9057a87b8257af7f88dbe42dba2f12a8`.
- B1 separation: no shared lineage, normalized exact hash, or contiguous
  12-word n-gram across user, chosen/target, and rejected text.

The data never moves into B1, aggregate-only B2, Tier C, or human-evaluation
sets. No example may be reassigned across splits to improve a metric.

## Known limitations

The scenario structure and renderer intentionally repeat a small number of
profile and genre patterns. This makes conditioning measurable but reduces
effective sample size and creates an artificial writing distribution. Rejected
answers are deterministic error constructions, not human preferences.
Validation and test rows are synthetic architecture checks, not independent
evidence about authentic task quality. Loss, perplexity, or B1 movement from
this dataset must be reported as exploratory and cannot justify a production
or source-fidelity claim.

## Reproduction

With the exact ignored source file whose SHA-256 is recorded in `manifest.json`:

```sh
uv run python -m goodprose.executive_writing unified-data build \
  --source data/derived/executive-writing/unified-pilot-v1/source-records.jsonl \
  --output-dir data/derived/executive-writing/unified-pilot-v1 \
  --manifest data/executive-writing/unified-pilot-v1/manifest.json \
  --b1-cases evals/executive-writing/goodprose-b1-v1/cases.jsonl
```

The compiler refuses every existing output. Move or archive an earlier local
build before reproducing it; never overwrite the source snapshot in place.
