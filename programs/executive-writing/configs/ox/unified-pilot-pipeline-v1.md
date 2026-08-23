# Ox assignment: unified three-corpus pilot pipeline v1

Status: frozen before delegation. Implement infrastructure only. Do not author
or receive training examples, benchmark rows, evaluator criteria, private data,
hidden content, model outputs, or grader rubrics.

## Objective

Implement and test the generic local pipeline needed for one genuine,
rights-safe, profile-conditioned unified MLX LoRA pilot:

1. compile a project-authored three-corpus source file into lineage-isolated
   MLX train/valid/test JSONL plus a compact committed manifest; and
2. generalize the proven MLX smoke runner so the same integrity, failure,
   artifact, and genuine-update checks can run either the existing smoke
   configuration or the new unified-pilot configuration without weakening
   prior validation.

This assignment must not create the real pilot examples or run training.
Codex will author and audit the project-owned source records, freeze the real
config at a later committed revision, execute the run, and evaluate it.

## Allowed edits

- new `src/goodprose/executive_writing/unified_data.py`
- `src/goodprose/executive_writing/training.py`
- `src/goodprose/executive_writing/__main__.py`
- new `tests/executive_writing/test_unified_data.py`
- `tests/executive_writing/test_training.py`
- new files under `data/executive-writing/unified-pilot-v1/`
- `data/executive-writing/README.md`

Do not edit dependency files, evaluation code/cases/results, existing smoke
data metadata, program reports/registry/costs, any Ox record, holdout code,
baseline code, or any other namespace. Do not commit or push.

## Frozen dataset boundary

Dataset ID:
`goodprose-project-authored-unified-pilot-v1`.

Rights status:
`training_permitted_project_owned_architecture_pilot`.

Intended use/status:
`unified_profile_conditioning_architecture_pilot_only`. It must never be
described as authentic human data, named-source data, final model-quality
evidence, or permission for external redistribution.

The compiler input is one ignored local JSONL source file supplied by Codex.
Each line must validate as exactly one strict frozen Pydantic record with:

- version 1;
- unique nonempty `example_id`;
- nonempty `lineage_group`;
- split in `train`, `valid`, `test`;
- corpus in `task_pair`, `style_target`, `preference_pair`;
- profile ID in exactly `concise-decision-v1`,
  `technical-explanatory-v1`, `operational-update-v1`;
- genre in exactly `email`, `memo`, `strategy_document`,
  `engineering_document`, `blog_post`, `short_post`, `revision`;
- creation method `codex_project_authored_v1`;
- authoring system `goodprose-unified-pilot-content-v1`;
- the frozen rights and intended-use strings above;
- nonempty system prompt and user prompt;
- for task/style records, one nonempty assistant target and no preference
  object;
- for preference records, one strict preference object containing nonempty,
  unequal `chosen` and `rejected`, a rejection-reason tuple drawn only from
  `unsupported_claim`, `intent_change`, `caveat_loss`, `number_error`,
  `attribution_error`, `unnecessary_rewrite`, `verbosity`, `organization`,
  `audience_mismatch`, and no standalone assistant target;
- normalized SHA-256 commitments for system, user, chosen/target, rejected
  when present; and
- a source-provenance object declaring `project_owned`, no named source,
  no external source, no personal/private data, and a nonempty transformation
  history.

The exact field names may be refined for clarity, but all semantics above must
be explicit, serialized, validated, and tested. Unknown fields are errors.

## Compiler requirements

Provide a pure loader/validator plus a compiler callable and CLI. The CLI shape
should follow:

```sh
python -m goodprose.executive_writing unified-data build \
  --source <ignored source-records.jsonl> \
  --output-dir <ignored derived directory> \
  --manifest data/executive-writing/unified-pilot-v1/manifest.json \
  --b1-cases evals/executive-writing/goodprose-b1-v1/cases.jsonl
```

The compiler must:

1. Refuse every existing output artifact and create no partial published
   manifest before all validation succeeds.
2. Validate exactly 90 input records, exactly 30 independent lineage groups,
   and exact split counts train 60, valid 15, test 15. Related lineage groups
   must never cross splits.
3. Validate exact corpus counts task_pair 54, style_target 22,
   preference_pair 14. Validate all three corpora occur in train and at least
   task_pair plus style_target occur in both valid and test. Record exact
   overall and per-split ratios; do not round ratios for integrity checks.
4. Validate every profile and every genre occurs overall and in train. Reject
   pathological imbalance: no overall profile count may differ from another
   by more than one; no overall genre may have fewer than six records.
5. Reject duplicate IDs, duplicate normalized prompts within a split,
   duplicate `(lineage_group, profile_id, genre, corpus)` cells, source/target
   hash mismatches, empty material, preference chosen/rejected equality, and
   any forbidden identity/person/source field.
6. Validate B1 separation by lineage, normalized exact hash, and exact
   contiguous 12-word n-grams across every user, target/chosen, and rejected
   text. Preserve the existing B1 benchmark bytes and never inspect anything
   outside the visible B1 path supplied by the CLI.
7. Materialize MLX chat records for all three corpora. Preference records use
   `chosen` as the SFT assistant message but preserve the rejected response,
   reasons, corpus, profile, genre, lineage, rights, transformation history,
   and all commitments in metadata. No information may be silently dropped.
8. Write deterministic `train.jsonl`, `valid.jsonl`, `test.jsonl`, and
   `preferences.jsonl` (the last contains all 14 preference records for future
   optional preference training). Preserve deterministic source order within
   each split; no random reshuffle in v1.
9. Produce a compact deterministic manifest containing input source byte hash,
   compiler hash, schema hash, B1 hash, all counts/ratios/balance evidence,
   split and preference-file hashes, contamination result, rights/intended-use
   fields, build command, and explicit limitations. Commit no source records or
   derived chat rows.
10. Use atomic writes and no network/model calls.

## Generalized MLX runner requirements

Preserve every existing smoke behavior and public function/CLI unless a
backward-compatible alias is provided. Generalize only the concrete hard-coded
parts needed for the pilot:

1. Strict frozen config validation must accept exactly two dataset/run kinds:
   the existing smoke dataset with its existing literal fields and 1/0/0
   ratios, or the unified dataset above with run kind
   `unified_profile_conditioned_lora_pilot` and exact ratios 0.6 task pairs,
   22/90 style targets, 14/90 preference pairs. Reject cross-combinations.
2. Keep the exact existing base model/framework/hardware/cost boundary:
   `mlx-community/Qwen2.5-0.5B-Instruct-4bit` at its pinned revision,
   MLX-LM 0.31.3, MLX 0.32.1, Apple M3 Pro 18 GiB, LoRA, settled cost $0.
3. Validate the committed manifest bytes, dataset ID/hash, rights/status,
   source-file hash when declared, split hashes, preference hash, split counts,
   corpus counts/ratios, and that every materialized record carries matching
   dataset, rights, split, corpus, profile, and lineage metadata. Do not trust
   only the compact manifest.
4. Add a generic `mlx-train run` CLI for either config while preserving
   `smoke-train run` as a backward-compatible route to the same core runner.
5. Preserve exact run-directory non-overwrite, pre-run running manifest,
   resolved config, timeout, combined log, failed manifest, model artifact
   inventory, positive trained-token proof, test loss, nonempty/nonzero adapter
   tensors, final checkpoint selection, runtime versions, elapsed time, and
   zero-cost evidence.
6. Add no checkpoint search. The config may use only
   `fixed_final_iteration` in this pilot.
7. Do not run MLX or download a model in tests. Extend mocked tests to cover
   both dataset kinds, invalid cross-combinations, tampered source/split/
   preference metadata, failure preservation, and successful genuine-update
   evidence.

## Public documentation

Under `data/executive-writing/unified-pilot-v1/`, commit only a concise README
and machine-readable record schema if useful. Explain the ignored source and
derived paths, the exact rights/intended-use boundary, three corpora, lineage
isolation, reproducible build command, contamination checks, and why this
project-authored synthetic architecture pilot cannot establish model quality.
Do not create the real manifest yet; Codex will generate it only after the
90-record source is independently authored and reviewed.

## Tests and output contract

All fixtures must be unmistakably synthetic, smaller count expectations must
be injectable only into pure/compiler test functions (never exposed as public
CLI verification bypasses), and no fixture may be presented as a real pilot
dataset. Cover strict schemas, all corpus forms, exact counts, balancing,
lineage isolation, contamination, deterministic hashes/order, atomic
non-overwrite, backward-compatible smoke behavior, and mocked runner success/
failure.

Run focused tests, the complete repository suite, Ruff lint/format, and
Pyright. Finish with a concise summary of files, exact tests, design choices,
and concerns for Codex review. Do not commit or push.
