# External evaluation adapters v1 (`external-v1`)

Status: **adapters implemented and tested; nothing has been executed.** This
directory contains acquisition metadata only. No benchmark rows, references,
checklist criteria, predictions, or results are committed. All locally adapted
artifacts belong in ignored output directories.

A passing adapter test proves schema and acquisition compatibility only. It is
never a benchmark result, never a leaderboard reproduction, and never a
quality claim.

## Benchmarks covered

| # | Benchmark ID | Source | Expected rows | Rights | Execution status |
|---|--------------|--------|---------------|--------|------------------|
| 1 | `writingbench-business` | WritingBench `benchmark_all.jsonl` (Finance & Business) | 1,000 file / 210 domain / 115 English eligible | `evaluation_only` | adapter tested; judge unpinned |
| 2 | `writingbench-engineering` | same file (Academic & Engineering) | 1,000 file / 167 domain / 107 English eligible | `evaluation_only` | adapter tested; judge unpinned |
| 3 | `iterater-diagnostic` | `wanyu/IteraTeR_human_sent` test split (clarity+coherence+fluency) | 364 test / 310 labeled / 308 usable | Apache-2.0 | adapter tested; not executed |
| 4 | `editeval-clarity` | same IteraTeR test split, EditEval semantics | 186 labeled / 185 usable | dataset: IteraTeR Apache-2.0 (not EditEval's CC0 code license) | adapter tested; not executed |
| 5 | `editeval-coherence` | same IteraTeR test split, EditEval semantics | 36 labeled / 35 usable | same as above | adapter tested; not executed |
| 6 | `revision-for-concision` | ACL 2022.tsar-1.6 `sac.xlsx` | 536 sentence pairs | `evaluation_only`; do not redistribute | adapter tested; not executed |
| 7 | `yapbench` | `tabularisai/yapbench_dataset` train parquet → local normalized JSONL | 304 source / 300 nonempty-prompt cases | **unverified — execution blocked until clarified** | blocked |

## Source pins

### WritingBench

- Repository: `https://github.com/X-PLUG/WritingBench`
- Commit: `ae2d5176449b7b769815482641d35926f26793eb` (Apache-2.0)
- Dataset: `benchmark_query/benchmark_all.jsonl`, blob
  `2d04c2d4c82f8c2d615e963393c7808f64b97129`, 14,726,077 bytes,
  SHA-256 `18fee37c645166eb2e206b36366b2e354265b1e4201db2c86e759e825eaddcbe`
- Schema: `index`, `domain1`, `domain2`, `lang`, `query`, `checklist`;
  `checklist` is a five-item list of structured criteria and score anchors.
- Auxiliary pins: `prompt.py` blob `8f81b8670e2b09717c4d25c7328ecb87a2e657ec`
  SHA-256 `c5bf21f28d4b4e54b682236cbe815831f3e362ff9b4f3e8c7c10467c491ecad1`;
  `evaluate_benchmark.py` blob `f22c145567472d25ed6368cfb2465e4be27e9fd8`
  SHA-256 `64707256e39e0533a020fe8042152b63ec706b63cbaa18d251030c71b0095e34`;
  LLM wrapper SHA-256
  `28a609a8ed070b2ab54fa8ff659b700175c20945c2b7cc670d106156aee2c0d5`

Acquisition:

```sh
git clone https://github.com/X-PLUG/WritingBench
cd WritingBench && git checkout ae2d5176449b7b769815482641d35926f26793eb
shasum -a 256 benchmark_query/benchmark_all.jsonl   # expect 18fee37c…ddcbe
```

Judge limitation: the upstream wrapper freezes temperature 1, top-p 0.95,
max 2,048 output tokens, but leaves the judge model and endpoint blank. The
README names Claude Sonnet 4.5 without an exact API model version. Any future
execution requires a separately pinned exact judge run config. We do not claim
reproduction of the upstream leaderboard from the repository alone.

License distinction: the repository is Apache-2.0, but the bundled query and
material components are not separately licensed upstream; treat all of it as
local `evaluation_only`.

The source has 1,000 multilingual rows. The requested domains contain 210 and
167 rows; rejecting their non-English rows leaves 115 Business and 107
Engineering cases. The frozen 32-case development source indices are:

- Business: `48, 49, 55, 60, 61, 64, 65, 77, 81, 82, 88, 89, 91, 92, 99,
  103, 104, 106, 108, 111, 113, 114, 119, 309, 322, 505, 565, 568, 624,
  671, 771, 842`.
- Engineering: `2, 3, 7, 8, 12, 13, 19, 20, 22, 23, 24, 26, 27, 29, 30,
  31, 33, 34, 36, 38, 39, 40, 43, 46, 258, 489, 490, 491, 493, 658, 719,
  956`.

### IteraTeR and EditEval clarity/coherence

- IteraTeR repository: `https://github.com/vipulraheja/iterater`, commit
  `41adc0818356f78b362a9382a3732e0529f3fe35`, Apache-2.0;
  `dataset/IteraTeR.zip` blob `d8ad5197667fe015007280dc24117beca9a67b84`,
  SHA-256 `386824f3310fca318351c0c76ed6475f99ed85dee0512e0da623af27b35e3ca7`
- Pinned dataset revision:
  `wanyu/IteraTeR_human_sent@e22e0371dac444239b944f9293f5b491d62b73f0`
  (Apache-2.0). Test split Git oid `04b93aef8a9db2576dd81541343f841bd7081971`,
  294,380 bytes,
  SHA-256 `1a30452c33bd5379ff56159016d68ecd7e2669ede1e4ea77244c6e300952e9cb`.
- Test counts: 364 total — clarity 186, coherence 36, fluency 88,
  meaning-changed 35, others 4, style 15.
- The canonical IteraTeR diagnostic has 310 clarity + coherence + fluency
  labels. Two released references contain only one whitespace character, so
  the strict nonempty-reference boundary emits 308 usable cases.
- EditEval: `https://github.com/facebookresearch/EditEval`, commit
  `013cd20aa73be0016041201454b3fcd7c2250fb4`, CC0-1.0 for code only.
  Pinned `ITERProcessor` SHA-256
  `93c810c62c7aefa2723cf5e951e6bf6d59ce77ffef060cdbb4116ee35586cd29`.
  Its exact `len(after_sent) > 1` filter emits 185 clarity and 35 coherence
  cases. Dataset rights remain IteraTeR's, not EditEval's code license.

Acquisition:

```sh
python - <<'PY'
from huggingface_hub import hf_hub_download
print(hf_hub_download("wanyu/IteraTeR_human_sent", "test.json",
                      revision="e22e0371dac444239b944f9293f5b491d62b73f0"))
PY
# verify SHA-256 1a30452c…e9cb before adapting
```

### Revision for Concision

- Paper/data page: `https://aclanthology.org/2022.tsar-1.6/`
  (DOI `10.18653/v1/2022.tsar-1.6`)
- ZIP SHA-256: `6ae45cc974caf9ffc7d7eca305b2f6d5fe1045af34bbe4073c30cd103652d9b2`
- Primary XLSX `sac.xlsx` SHA-256:
  `77f05c87f48f3e6dd25197bc921d38032ef145d834fce2d35e6e0125e798889e`
- Columns: `cite`, `wordy`, `concise`, `category`, `link`, `id`;
  `concise` holds a Python-style list of one or more references.

Acquisition:

```sh
curl -O https://aclanthology.org/attachments/2022.tsar-1.6.dataset.zip
unzip 2022.tsar-1.6.dataset.zip
shasum -a 256 2022.tsar-1.6.dataset.zip sac.xlsx   # verify both hashes above
```

Rights: ACL applies CC BY 4.0 to post-2016 Anthology materials, but this
spreadsheet compiles college writing-center examples; treat it as local
`evaluation_only`, do not redistribute it or adapted rows, and keep per-row
citation/link metadata only in local adapted artifacts.

The adapter accepts either the XLSX directly (dependency-free shared-strings
reader) or a strict CSV with the exact six columns; no spreadsheet framework
is used.

### YapBench

- Paper: `arXiv:2601.00624`, YapBench v0.1
- Pinned dataset: `tabularisai/yapbench_dataset@be8427ddf7780201b73676c1563bc3ea6d0a71ca`
- Parquet `data/train-00000-of-00001.parquet`: LFS SHA-256
  `6bf58b51cef6b26e78cf462ff78d43d1b80d1162268be6019918036212430d5e`,
  24,703 bytes; schema `id`, `category`, `prompt`, `baseline`,
  `baseline_type`, `domain`, `notes`; 304 rows.
- Leaderboard Space revision `fd2f0e6ba21f4311a2e667bd2ce470bafa50788e` is
  Apache-2.0, which does **not** cure the dataset-license omission.

Acquisition and conversion (outside this repository; parquet support is
intentionally not vendored):

```sh
python - <<'PY'
import json
import pyarrow.parquet  # or pandas.read_parquet / duckdb
from huggingface_hub import hf_hub_download
path = hf_hub_download("tabularisai/yapbench_dataset",
                       "data/train-00000-of-00001.parquet",
                       revision="be8427ddf7780201b73676c1563bc3ea6d0a71ca")
rows = pyarrow.parquet.read_table(path).to_pylist()
with open("yapbench.normalized.jsonl", "w", encoding="utf-8") as handle:
    for row in rows:
        normalized = {k: row[k] for k in
            ("id", "category", "prompt", "baseline", "baseline_type",
             "domain", "notes")}
        handle.write(json.dumps(normalized, ensure_ascii=False, sort_keys=True,
                                separators=(",", ":")) + "\n")
PY
# verify the parquet LFS SHA-256 before converting; the adapter records the
# normalized JSONL SHA-256 before parsing it
```

Rights status is unverified: redistribution is prohibited and execution stays
blocked until the license is clarified.

Four pinned prompts contain only whitespace. The strict nonempty-input boundary
records and excludes them, yielding 300 compatibility cases; this deviation is
part of the GoodProse variant and is not upstream leaderboard parity.

## Metric policy (YapBench)

GoodProse compatibility variant, explicitly labeled:

- Per-case YapScore = `max(0, visible(response chars) − visible(baseline chars))`
- Category score = median of per-case scores; YapIndex = uniform mean of
  category medians
- Normalization `goodprose-visible-chars-v1`: strip code fences, image/link
  markup (keep link text), HTML tags, heading/quote/list prefixes, emphasis
  markers; collapse whitespace runs. Upstream implementation parity is not
  proven and the variant is labeled accordingly.
- Intervals: 1,000 category-stratified bootstrap resamples under pinned seed
  `42`; results report raw medians, the aggregate index, the percentile
  interval, count, metric version, and normalization version.

YapScore measures verbosity only. It is never an executive-writing quality
score, and brevity never bypasses fidelity gates.

## Development vs full-suite policy

- WritingBench: one deterministic 32-case development subset per requested
  domain, stratified by `domain2` via round-robin over sorted subdomains. The
  exact indices above are frozen in the code registry and verified during
  adaptation. All remaining English-eligible cases are reserved for
  finalist/milestone use.
- Everything else: evaluation-split only; no development iteration on these
  sets.

## Output-status language

- `adapter_tested_not_executed`: schema/acquisition verified locally; no run
  against any candidate has occurred.
- `adapter_tested_unexecuted_judge_unpinned`: additionally, the upstream judge
  is not exactly pinned; execution requires a separately frozen judge config.
- `execution_blocked_rights_unverified`: execution is prohibited pending
  license clarification.

## CLI

```sh
python -m goodprose.executive_writing external-evals validate-registry
python -m goodprose.executive_writing external-evals adapt \
    --benchmark-id writingbench-business --source <local benchmark_all.jsonl> \
    --output-dir <ignored dir>
python -m goodprose.executive_writing external-evals emit-candidates \
    --cases <adapted cases.jsonl> --suite development \
    --output <candidates.jsonl>
python -m goodprose.executive_writing external-evals validate-predictions \
    --cases <adapted cases.jsonl> --suite development \
    --predictions <predictions.jsonl>
python -m goodprose.executive_writing external-evals adapt \
    --benchmark-id yapbench --source <normalized.jsonl> \
    --upstream-source <pinned.parquet> --output-dir <ignored dir>
python -m goodprose.executive_writing external-evals score-yapbench \
    --cases <adapted cases.jsonl> --predictions <predictions.jsonl> \
    --result <result.json>
```

The YapBench scoring command remains blocked by the registry until the dataset
license is clarified; its pure deterministic metric stays unit-tested.

The CLI never downloads data, calls a model or judge, exposes references or
checklist criteria in candidate payloads, or overwrites an existing artifact.

## Committed content boundary

This directory must contain only this README and acquisition metadata. Commit
no benchmark rows, references, checklist criteria, predictions, or results.
