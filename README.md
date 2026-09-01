# GoodProse

GoodProse is a deliberately small pipeline for fine-tuning a model on one author's blog
writing. It turns reviewed outlines, notes, or rough drafts into the author's exact published
prose and measures whether a fine-tune beats the prompted base model.

```text
rough draft, outline, or factual brief -> finished blog post
```

The repository contains no third-party writing corpus and no synthetic training targets.

## Workflow

1. Export the blog as Markdown and import the posts.
2. Write or review one input brief for each post and assign its split.
3. Join briefs to the exact published posts to create canonical pairs.
4. Export `train` and `dev` pairs in chat-style SFT JSONL.
5. Compare base and fine-tuned outputs on the frozen `test` cases in a blind review.

```bash
uv sync

uv run goodprose import-posts path/to/markdown \
  --output data/posts/posts.jsonl \
  --url-base https://example.com/blog/

uv run goodprose build-pairs \
  --posts data/posts/posts.jsonl \
  --briefs data/briefs.jsonl \
  --output data/pairs.jsonl

uv run goodprose build-sft \
  --pairs data/pairs.jsonl \
  --output-dir data/sft \
  --eval-output evals/cases.jsonl
```

The Markdown importer understands simple front matter keys: `id`, `title`, `url`, `date`, and
`series`. A first-level heading supplies the title when front matter does not.

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

# Fill in the five empty review fields in review.jsonl, then:
uv run goodprose eval summarize \
  --packet evals/results/review.jsonl \
  --key evals/results/review-key.json \
  --output evals/results/summary.json
```

The primary decision is simple: prefer the system that wins more blind comparisons and requires
less editing, provided it does not introduce more unsupported facts.

## Repository map

```text
data/posts/             imported canonical blog posts
data/briefs.jsonl       reviewed inputs and split assignments
data/pairs.jsonl        canonical source-to-target pairs
data/sft/               generated training files
evals/cases.jsonl       generated frozen test cases
evals/results/           local model outputs and reviews
src/goodprose/           importer, pair builder, exporter, and evaluator
tests/                   deterministic unit tests
```

The previous executive-writing research program remains available in Git history and at the tag
`archive/executive-writing-program-2026-08-31`.
