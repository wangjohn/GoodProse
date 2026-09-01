# GoodProse

GoodProse is a deliberately small pipeline for fine-tuning a model on one author's blog
writing. It turns reviewed outlines, notes, or rough drafts into the author's exact published
blog prose at the requested scope and measures whether a fine-tune beats the prompted base model.

```text
rough draft, outline, or factual brief -> finished blog paragraph, section, or post
```

The repository contains no third-party writing corpus and no synthetic training targets.

## Workflow

1. Export the blog as Markdown and import the posts.
2. Freeze each blog lineage into `train`, `dev`, or `test`.
3. Generate and review verbatim semantic chunk candidates.
4. Recover an authentic prompt/draft or review a derived brief for each approved target.
5. Join reviewed inputs to the exact published targets to create canonical pairs.
6. Export `train` and `dev` pairs in chat-style SFT JSONL.
7. Compare base and fine-tuned outputs on the frozen `test` cases in a blind review.

```bash
uv sync

uv run goodprose import-posts data/private/source/personal_website/content/post \
  --output data/private/posts/johnjwang-posts.jsonl \
  --url-template 'https://johnjwang.com/post/{year}/{month}/{day}/{slug}/'

uv run goodprose build-external-posts \
  --catalog data/external/posts.jsonl \
  --snapshot-root data/private/external/published-raw \
  --base-posts data/private/posts/johnjwang-posts.jsonl \
  --output data/posts/posts.jsonl

uv run goodprose build-chunks \
  --posts data/posts/posts.jsonl \
  --splits data/splits.jsonl \
  --output data/chunks/candidates.jsonl \
  --review-output data/chunks/REVIEW.md

uv run goodprose build-prompt-candidates \
  --drafts data/private/prompts/external-drafts.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --base-prompts data/private/prompts/candidates.jsonl \
  --output data/private/prompts/candidates.jsonl

uv run goodprose review-prompts \
  --prompts data/private/prompts/candidates.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --output data/private/prompts/REVIEW.md

uv run goodprose approve-prompts \
  --prompts data/private/prompts/candidates.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --reviewer-note 'Approved by the author after reasonability, provenance, and leakage review.'

uv run goodprose build-prompt-pairs \
  --prompts data/private/prompts/candidates.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --posts data/posts/posts.jsonl \
  --heldout-pairs data/private/eval/pairs.jsonl \
  --heldout-pairs data/private/external/eval-pairs.jsonl \
  --output data/private/pairs.jsonl

uv run goodprose build-sft \
  --pairs data/private/pairs.jsonl \
  --output-dir data/sft \
  --eval-output evals/cases.jsonl

uv run goodprose build-external-samples \
  --catalog data/external/posts.jsonl \
  --source-map data/private/external/source-map.jsonl \
  --source-root data/private/external/blogposts-source \
  --output data/private/external/samples.jsonl
```

The Markdown importer understands simple front matter keys: `id`, `title`, `url`, `date`, and
`series`. A first-level heading supplies the title when front matter does not. For sites with
dated permalinks, `--url-template` accepts `{id}`, `{slug}`, `{year}`, `{month}`, and `{day}`.

## Canonical pair

`data/briefs.jsonl` is the small hand-reviewed file that defines the transformation and split:

```json
{"version":1,"id":"why-tools-matter","post_id":"why-tools-matter","split":"train","input":"An outline or rough draft written or reviewed by the author.","input_method":"original_outline"}
```

`build-pairs` copies the matching published post into the output. Supported input methods are
`original_outline`, `original_draft`, and `derived_brief`. Derived briefs are allowed, but they
must be reviewed and should not copy distinctive phrases from the target.

## Evaluation

Model outputs use one record per held-out case:

```json
{"id":"held-out-post","output":"The model's proposed post."}
```

Prepare and score a blind comparison:

```bash
uv run goodprose eval prepare \
  --cases evals/cases.jsonl \
  --baseline evals/results/base.jsonl \
  --candidate evals/results/sft.jsonl \
  --packet evals/results/review.jsonl \
  --key evals/results/review-key.json

# Complete the factuality, instruction, preference, and edit-burden fields, then:
uv run goodprose eval summarize \
  --packet evals/results/review.jsonl \
  --key evals/results/review-key.json \
  --decision-rules evals/decision-rules.json \
  --output evals/results/summary.json
```

The evaluator applies explicit pass/fail gates, records separate voice and overall preferences,
counts unsupported claims, compares edit burden, and reports outcomes per case, lineage, and input
method. See `evals/README.md` for run manifests, the anchored rubric, and the decision rules.

## LoRA+ training

The checked-in starter config uses Qwen3-8B with rank-32 LoRA adapters. PEFT's LoRA+ optimizer
trains the LoRA A weights at `5e-5` and the B weights at `8e-4` (a 16x ratio). The runner validates
the exact system prompt, dataset counts, and file hashes before loading the model. It converts each
conversation into prompt/completion form so TRL computes loss only on the author's completion.

Validate the run without installing or loading the model:

```bash
uv run goodprose train-lora-plus \
  --config configs/qwen3-8b-lora-plus.json \
  --validate-only
```

On a CUDA machine, install the training dependencies and start the run:

```bash
uv sync --extra train
uv run goodprose train-lora-plus --config configs/qwen3-8b-lora-plus.json
```

For a lower-memory 4-bit run, also install `train-4bit`, then set `load_in_4bit` to `true` and
`optimizer` to `adam8bit` in a copy of the config. Each completed run saves the adapter, tokenizer,
trainer state, metrics, resolved model revisions, dependency versions, and input hashes under
`runs/`. Keep the frozen test cases out of training and use the blind evaluator for the actual
go/no-go decision.

## Repository map

```text
data/posts/             imported canonical blog posts
data/external/          approved Assembled and Medium source catalog
data/splits.jsonl       frozen lineage-level train/dev/test assignments
data/provenance/        authoring-history coverage without raw private prompts
data/chunks/            verbatim semantic chunk candidates and review packet
data/private/prompts/   synthetic training inputs and local review packet
data/private/external/  saved pages and authentic held-out inputs
data/private/eval/      original-site authentic held-out inputs
data/private/pairs.jsonl generated approved source-to-target pairs
data/sft/               generated training files
configs/                validated LoRA+ run configurations
evals/cases.jsonl       generated frozen test cases
evals/results/           local model outputs and reviews
src/goodprose/           importer, pair builder, exporter, trainer, and evaluator
tests/                   deterministic unit tests
```

The previous executive-writing research program remains available in Git history and at the tag
`archive/executive-writing-program-2026-08-31`.
