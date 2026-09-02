# Data

The canonical data flow is:

```text
Markdown blog export -> posts/posts.jsonl
external snapshots   -> posts/posts.jsonl (approved published targets)
frozen lineage split -> splits.jsonl
semantic candidates  -> chunks/candidates.jsonl
synthetic candidates -> private/prompts/candidates.jsonl (review only)
approved train inputs -> private/pairs.jsonl
authentic eval inputs -> private/eval/pairs.jsonl + private/external/eval-pairs.jsonl
SFT build            -> sft/train.jsonl and sft/dev.jsonl
test split           -> ../evals/cases.jsonl
```

Canonical posts, briefs, and pairs may be committed when they are safe to publish. Generated SFT
files are ignored because they can be rebuilt byte-for-byte from the canonical pairs.

`provenance/inventory.jsonl` records which posts have recoverable authentic authoring inputs
without publishing raw conversation text. Unreviewed extracts remain under ignored
`data/private/`. Semantic chunks are deterministic, verbatim spans. The 68 chunks referenced by
training prompts were approved by the author on 2026-09-01; development and test chunks remain
candidates and cannot pass the training promotion gate.

Synthetic prompts are built only against training chunks and remain under ignored `data/private/`.
The 68 current prompts are approved reviewed-derived briefs. The local review packet pairs each
input with its exact completion, requires target citation URLs to be present in the input, and
reports the longest verbatim word run as a leakage-review aid.

`external/posts.jsonl` catalogs thirteen approved Assembled and Medium posts. Their normalized
published snapshots are canonical targets in `posts/posts.jsonl`. Recovered author Markdown,
public snapshots, line-range maps, authentic held-out inputs, and generated pairs stay under
ignored `private/external/`. The two development and two test posts have authentic drafts or
outlines; synthetic inputs are generated only for training chunks.

`build-prompt-pairs` is the promotion gate for section-level training data. It verifies frozen
metadata and target hashes, rejects any prompt or chunk that is not explicitly approved, and can
merge the resulting training sections with authentic held-out pairs for `build-sft`.
