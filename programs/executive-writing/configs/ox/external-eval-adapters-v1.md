# Ox assignment: external evaluation adapters v1

Status: frozen before delegation. All repository fixtures must be synthetic.
The public benchmark files inspected by Codex remain temporary local research
inputs and must not be copied into git or sent through model context.

## Objective

Implement strict, tested GoodProse adapters and reproducible acquisition
metadata for every external evaluation named by the research contract:

1. WritingBench Business
2. WritingBench Engineering
3. IteraTeR
4. EditEval clarity
5. EditEval coherence
6. Revision for Concision
7. YapBench

Adapters normalize externally acquired inputs to a single versioned GoodProse
case boundary while keeping source text, references, criteria, and generated
outputs out of the committed repository. They must distinguish a tested
adapter from an executed benchmark and must never claim leaderboard parity
when an upstream judge, metric, or exact model version is not reproducible.

## Independently verified source pins

Use these facts as frozen inputs. Do not browse or update them.

### WritingBench

- Canonical repository: `https://github.com/X-PLUG/WritingBench`
- Commit: `ae2d5176449b7b769815482641d35926f26793eb`
- Repository license: Apache-2.0. Treat bundled query/material component rights
  as `evaluation_only`; the repository does not enumerate a separate license
  for every underlying collected material.
- Dataset path: `benchmark_query/benchmark_all.jsonl`
- Git blob: `2d04c2d4c82f8c2d615e963393c7808f64b97129`
- Exact file bytes: 14,726,077; SHA-256
  `18fee37c645166eb2e206b36366b2e354265b1e4201db2c86e759e825eaddcbe`
- Schema: `index`, `domain1`, `domain2`, `lang`, `query`, `checklist`.
- Exact full counts: 210 `Finance & Business`; 167
  `Academic & Engineering`.
- Upstream prompt path/blob/SHA-256: `prompt.py` /
  `8f81b8670e2b09717c4d25c7328ecb87a2e657ec` /
  `c5bf21f28d4b4e54b682236cbe815831f3e362ff9b4f3e8c7c10467c491ecad1`.
- Upstream evaluator path/blob/SHA-256: `evaluate_benchmark.py` /
  `f22c145567472d25ed6368cfb2465e4be27e9fd8` /
  `64707256e39e0533a020fe8042152b63ec706b63cbaa18d251030c71b0095e34`.
- LLM wrapper SHA-256:
  `28a609a8ed070b2ab54fa8ff659b700175c20945c2b7cc670d106156aee2c0d5`.
  It freezes temperature 1, top-p 0.95, max 2,048, but leaves the judge model
  and endpoint blank. The README says Claude Sonnet 4.5, not an exact API
  model version. Therefore require a separately pinned exact judge run config
  and label the adapter unexecuted; never claim reproduction of the upstream
  leaderboard from the repository alone.
- Build one deterministic 32-case development subset per requested domain,
  stratified by `domain2`; reserve all 210/167 cases for finalist/milestone
  use. Freeze the selected source indices in the public manifest.

### IteraTeR and EditEval clarity/coherence

- IteraTeR repository/commit/license:
  `https://github.com/vipulraheja/iterater` /
  `41adc0818356f78b362a9382a3732e0529f3fe35` / Apache-2.0.
- Repository archive path/blob/SHA-256: `dataset/IteraTeR.zip` /
  `d8ad5197667fe015007280dc24117beca9a67b84` /
  `386824f3310fca318351c0c76ed6475f99ed85dee0512e0da623af27b35e3ca7`.
- Use the human sentence-level set for evaluation, not the model-labeled full
  set and not IteraTeR-v2/IteraTeR-plus (the upstream README requires Newsela
  acquisition and author contact for those later datasets).
- Pinned Hugging Face dataset revision:
  `wanyu/IteraTeR_human_sent@e22e0371dac444239b944f9293f5b491d62b73f0`,
  tagged Apache-2.0. Test file Git oid
  `04b93aef8a9db2576dd81541343f841bd7081971`, 294,380 bytes,
  SHA-256 `1a30452c33bd5379ff56159016d68ecd7e2669ede1e4ea77244c6e300952e9cb`.
- Test JSONL schema: `before_sent`, `before_sent_with_intent`, `after_sent`,
  `labels`, `doc_id`, `revision_depth`. Exact test counts: 364 total; clarity
  186; coherence 36; fluency 88; meaning-changed 35; others 4; style 15.
- Canonical IteraTeR diagnostic: clarity + coherence + fluency (310 test
  records), using the provided labels as task filters only. Never use the
  released intent classifier as an authoritative long-form judge; its reported
  F1 is 0.69 clarity, 0.32 coherence, and 0.13 style.
- EditEval repository/commit/code license:
  `https://github.com/facebookresearch/EditEval` /
  `013cd20aa73be0016041201454b3fcd7c2250fb4` / CC0-1.0.
- Its pinned `ITERProcessor` SHA-256 is
  `93c810c62c7aefa2723cf5e951e6bf6d59ce77ffef060cdbb4116ee35586cd29`;
  it loads `wanyu/IteraTeR_human_sent`, maps `before_sent` to input and
  `after_sent` to edits, filters exact task labels, and removes references of
  length one or less. Adapt clarity and coherence as separate diagnostics.
  Dataset rights remain those of IteraTeR, not EditEval's code license.

### Revision for Concision

- Canonical paper/data page: `https://aclanthology.org/2022.tsar-1.6/`;
  DOI `10.18653/v1/2022.tsar-1.6`.
- Attachment URL:
  `https://aclanthology.org/attachments/2022.tsar-1.6.dataset.zip`.
- ZIP SHA-256:
  `6ae45cc974caf9ffc7d7eca305b2f6d5fe1045af34bbe4073c30cd103652d9b2`.
- Primary XLSX `sac.xlsx` SHA-256:
  `77f05c87f48f3e6dd25197bc921d38032ef145d834fce2d35e6e0125e798889e`.
- The paper reports 536 sentence pairs. XLSX columns are `cite`, `wordy`,
  `concise`, `category`, `link`, `id`; `concise` contains a Python-style list
  of one or more references.
- ACL states post-2016 Anthology materials are CC BY 4.0, but the spreadsheet
  compiles examples from multiple college writing centers. Treat it as local
  `evaluation_only`, do not redistribute it, and preserve its per-row source
  citation/link metadata only in local adapted artifacts.
- Implement a dependency-free reader for this narrow XLSX shared-strings form,
  or a strict CSV normalization path plus reproducible conversion command. Do
  not add a spreadsheet framework solely for this adapter.

### YapBench

- Paper: `arXiv:2601.00624`, YapBench v0.1.
- Pinned dataset: `tabularisai/yapbench_dataset` revision
  `be8427ddf7780201b73676c1563bc3ea6d0a71ca`.
- Parquet path/LFS SHA-256/bytes:
  `data/train-00000-of-00001.parquet` /
  `6bf58b51cef6b26e78cf462ff78d43d1b80d1162268be6019918036212430d5e` /
  24,703. Schema: `id`, `category`, `prompt`, `baseline`, `baseline_type`,
  `domain`, `notes`; 304 rows.
- The separate dataset has no license metadata. Mark its rights unverified,
  prohibit redistribution, and keep execution blocked until clarified; still
  provide and test a normalized-JSONL adapter and exact local acquisition/
  conversion instructions.
- Pinned public leaderboard Space revision
  `fd2f0e6ba21f4311a2e667bd2ce470bafa50788e` is Apache-2.0, but that does not
  cure the dataset-license omission.
- Implement the published deterministic metric as a GoodProse-labeled
  compatibility variant: per-case YapScore is
  `max(0, visible_response_characters - visible_baseline_characters)`;
  category score is the median; YapIndex is the uniform mean of category
  medians. Freeze the exact markdown-character normalization and label it if
  upstream implementation parity cannot be proven. Never treat it as an
  executive-writing quality score or allow brevity to bypass fidelity gates.

## Required implementation

Allowed edits:

- new `src/goodprose/executive_writing/external_evals.py`
- new `tests/executive_writing/test_external_evals.py`
- `src/goodprose/executive_writing/__main__.py`
- new files under `evals/executive-writing/external-v1/`
- `evals/executive-writing/README.md`

Do not modify program reports, experiment records, costs, registry, dependency
files, or any other implementation namespace. Codex will review and publish.

Implement:

1. Strict frozen Pydantic v2 models (`extra="forbid"`) for the public source
   registry, normalized cases, adapted manifest, prediction records, and
   deterministic YapBench result.
2. Exact SHA-256 verification before parsing every external input. Reject
   unknown fields, duplicate case IDs, missing/extra expected rows, invalid
   labels/domains, empty source/reference material, non-English WritingBench
   rows, and accidental reference/criteria exposure in candidate payloads.
3. Pure adapters for WritingBench JSONL, IteraTeR/EditEval JSONL, Revision for
   Concision XLSX or normalized CSV, and YapBench normalized JSONL. The same
   source file may feed multiple benchmark IDs, but each normalized case must
   retain benchmark/source/split/task provenance.
4. A deterministic, stratified WritingBench development selector with the
   exact selected source indices frozen in the registry. Candidate-generation
   payloads expose only ID and instruction/input; references and checklist
   criteria remain in the local evaluator artifact.
5. Exact prediction-set validation: one nonempty output per case, no duplicate,
   missing, or extra IDs. Do not include candidate outputs in committed
   examples or results.
6. YapScore/YapIndex plus deterministic 1,000-resample category-stratified
   percentile intervals under a pinned seed. Report raw category medians,
   aggregate index, interval, count, metric version, and normalization version.
7. A CLI for validating the registry, adapting a locally acquired source to an
   ignored output directory, emitting a candidate-only payload, validating
   predictions, and scoring YapBench. It must never download data, call a
   model/judge, expose criteria/references in candidate payloads, or overwrite
   an existing artifact.
8. A concise public README with exact acquisition commands, pins/hashes,
   source-component license distinctions, expected counts, upstream judge
   limitation, development/full-suite policy, and output-status language.
   Commit no benchmark rows, references, criteria, predictions, or results.
9. Synthetic deterministic tests covering all seven IDs and source shapes,
   exact-hash rejection, fixed WritingBench selection, leakage separation,
   IteraTeR/EditEval task counts, XLSX parsing, YapBench scoring/bootstrap,
   rights/status distinctions, CLI non-overwrite behavior, and no network or
   model calls.

Use Python 3.12+, type hints, standard library plus existing dependencies,
small pure functions, Pydantic at boundaries, deterministic tests, and no live
API calls. Run focused tests, Ruff lint/format, and Pyright on touched files.

## Output contract

Finish with a concise summary of files, exact test counts, design choices, and
concerns for Codex review. Do not commit or push. A passing adapter test proves
schema and acquisition compatibility only; it is not a benchmark result.
