# GoodProse

GoodProse is a deliberately small pipeline for fine-tuning a model on one author's blog
writing. It turns reviewed outlines, notes, or rough drafts into the author's exact published
blog prose at the requested scope and measures whether a fine-tune beats the prompted base model.

```text
rough draft, outline, or factual brief -> finished blog sentence, paragraph, section, or post
```

The repository contains no third-party writing corpus and no synthetic training targets.

## Workflow

1. Export the blog as Markdown, import the posts, and merge the external snapshots (repairing
   flattened code from the author manuscripts where they exist) into a raw post file.
2. Normalize the raw posts with the configured conventions (straight quotes, `*italics*`,
   section headings at `#`, reviewed substitutions); each post records what fired.
3. Freeze each blog lineage into `train`, `dev`, or `test`, and give each post a training role:
   `pairs` for the author's own text, `raw_only` for editor-revised text that may only teach
   register under its venue line, `excluded` for pairs that would teach the wrong thing.
4. Generate and review verbatim semantic chunk candidates, including one post-scale target per
   training post (`--full-posts`), so training covers the same scope the test cases ask for.
5. Recover an authentic prompt/draft or review derived briefs for each approved target. Several
   prompt forms may target one chunk; write them in the rough register of your real drafts, and
   carry any code block in the target verbatim so the model copies code rather than composing it.
6. Join reviewed inputs to the exact published targets to create canonical pairs.
7. Export `train` and `dev` pairs in chat-style SFT JSONL. Every user turn opens with a venue
   line such as `Venue: johnjwang.com (2026)`; raw completions of sentence- and section-scale
   paired targets and every `raw_only` chunk join the mix with `--raw-completions`. Reviewed
   full-post pairs are not duplicated under a weak title-only prompt.
8. Rank checkpoints with the cheap proxies (dev NLL, stylometry, a blinded frontier judge) and a
   quick blind pass over section-scale cases cut from the held-out drafts (`build-short-cases`),
   then compare base and fine-tuned outputs on the frozen whole-post `test` cases in the final
   blind human review.
9. Capture every new draft with `capture-draft` before polishing; those become the prospective
   test set once the post is published.
10. Optionally run one DPO pass with your published text as chosen and the SFT model's own
   output as rejected.

`scripts/rebuild-data.sh` runs the import, normalization, chunking, brief refresh, and review
steps below in order on a machine that has `data/private/`, then stops at approval.

```bash
uv sync

uv run goodprose import-posts data/private/source/personal_website/content/post \
  --output data/private/posts/johnjwang-posts.jsonl \
  --url-template 'https://johnjwang.com/post/{year}/{month}/{day}/{slug}/'

uv run goodprose build-external-posts \
  --catalog data/external/posts.jsonl \
  --snapshot-root data/private/external/published-raw \
  --base-posts data/private/posts/johnjwang-posts.jsonl \
  --source-map data/private/external/source-map.jsonl \
  --source-root data/private/external/blogposts-source \
  --repair-code \
  --fence-heuristic go \
  --target-from-manuscript external-scaling-llms-golang \
  --output data/private/posts/raw-posts.jsonl

uv run goodprose normalize-posts \
  --raw data/private/posts/raw-posts.jsonl \
  --config data/posts/normalization.json \
  --output data/posts/posts.jsonl

uv run goodprose build-chunks \
  --posts data/posts/posts.jsonl \
  --splits data/splits.jsonl \
  --exclusions data/chunks/exclusions.jsonl \
  --supplemental-targets data/chunks/supplemental-targets.jsonl \
  --full-posts \
  --normalization data/posts/normalization.json \
  --output data/chunks/candidates.jsonl \
  --review-output data/chunks/REVIEW.md

uv run goodprose build-prompt-candidates \
  --drafts data/private/prompts/external-drafts.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --base-prompts data/private/prompts/candidates.jsonl \
  --replace-lineage external-better-rag \
  --replace-lineage external-blocking-llms \
  --replace-lineage external-code-review-bottlenecks \
  --replace-lineage external-product-lessons-dan-robinson \
  --replace-lineage external-scaling-llms-golang \
  --replace-lineage external-startup-journey \
  --replace-lineage external-stripe-customer-support \
  --replace-lineage external-tests-with-llms \
  --replace-lineage external-why-i-code-as-a-cto \
  --output data/private/prompts/candidates.jsonl

uv run goodprose build-prompt-candidates \
  --drafts data/private/prompts/sentence-drafts.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --base-prompts data/private/prompts/candidates.jsonl \
  --output data/private/prompts/candidates.jsonl

# After a rebuild of posts or chunks, align the existing briefs before adding new ones:
# drops briefs on demoted posts, rehashes formatting-only changes, resets material changes.
uv run goodprose refresh-prompts \
  --prompts data/private/prompts/candidates.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --roles data/training-roles.jsonl \
  --normalization data/posts/normalization.json

# Whole-post briefs for the `--full` chunks are drafted in the repository (they contain no
# target text) and attach like any other draft file.
uv run goodprose build-prompt-candidates \
  --drafts data/prompts/full-post-drafts.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --base-prompts data/private/prompts/candidates.jsonl \
  --output data/private/prompts/candidates.jsonl

uv run goodprose review-prompts \
  --prompts data/private/prompts/candidates.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --posts data/posts/posts.jsonl \
  --roles data/training-roles.jsonl \
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
  --text-exclusions data/pair-text-exclusions.jsonl \
  --roles data/training-roles.jsonl \
  --output data/private/pairs.jsonl

uv run goodprose build-sft \
  --pairs data/private/pairs.jsonl \
  --output-dir data/sft \
  --eval-output evals/cases.jsonl \
  --raw-completions \
  --roles data/training-roles.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --posts data/posts/posts.jsonl \
  --train-cases-output data/private/train-cases.jsonl

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

## Training

Three starter configs share one data manifest and one prompt render:

| Config | Base | Update | Learning rate | Use |
|---|---|---|---|---|
| `configs/qwen3-8b-lora.json` | Qwen3-8B (pinned) | rank-32 LoRA, all linear layers | 2e-4 | control arm |
| `configs/qwen3-8b-lora-plus.json` | Qwen3-8B (pinned) | LoRA+ (A 5e-5, B 8e-4) | 16x ratio | comparison arm |
| `configs/qwen3-14b-lora.json` | Qwen3-14B, 4-bit | rank-32 LoRA, 8-bit Adam | 2e-4 | size comparison |

All three evaluate dev loss every epoch, keep every epoch checkpoint, use an effective batch of
4, and run 5 epochs. `--validate-only` reports the optimizer step count so you can see whether a
schedule is meaningful before spending GPU time. Pin the 14B revision to a commit hash before a
run you intend to keep.

Training renders every prompt to text with the same `chat_template_kwargs` used at inference
(`enable_thinking: false` for Qwen3), so the adapter learns the exact assistant prefix,
including the empty think block, that it is conditioned on later. The run manifest and every
generation manifest record a hash of that prefix, and `eval prepare` refuses to compare runs
whose prefixes differ. `max_length` is 6144 to fit whole-post pairs; drop it to 4096 on a
24 GB GPU and accept truncation of the two longest posts.

```bash
uv run goodprose train-lora-plus --config configs/qwen3-8b-lora.json --validate-only

uv sync --extra train
uv run goodprose train-lora-plus --config configs/qwen3-8b-lora.json
```

### Ranking checkpoints before anyone reads them

Score held-out likelihood, generate outputs with the deployment decoding (sampled at
temperature 0.7, top-p 0.9, repetition penalty 1.05, fixed seed; pass `--temperature 0` for a
greedy pass), and run the stylometric proxy against your published training prose:

```bash
uv run goodprose eval nll \
  --config configs/qwen3-8b-lora.json \
  --records data/sft/dev.jsonl \
  --adapter runs/qwen3-8b-lora/checkpoint-N \
  --run-id checkpoint-N \
  --output evals/results/checkpoint-N-nll.json

uv run goodprose eval generate \
  --config configs/qwen3-8b-lora.json \
  --cases evals/cases.jsonl \
  --role baseline --run-id base \
  --output evals/results/base.jsonl --manifest evals/results/base-run.json

uv run goodprose eval generate \
  --config configs/qwen3-8b-lora.json \
  --cases evals/cases.jsonl \
  --role candidate --adapter runs/qwen3-8b-lora/checkpoint-N --run-id checkpoint-N \
  --output evals/results/checkpoint-N.jsonl --manifest evals/results/checkpoint-N-run.json

uv run goodprose eval proxy \
  --cases evals/cases.jsonl \
  --outputs base=evals/results/base.jsonl \
  --outputs checkpoint-N=evals/results/checkpoint-N.jsonl \
  --posts data/posts/posts.jsonl --splits data/splits.jsonl \
  --reference-url-substring johnjwang.com \
  --output evals/results/proxy.json
```

`--reference-url-substring johnjwang.com` measures distance to the personal-site prose alone,
which is the target voice; the same flag on `eval judge-packet` draws the judge's author samples
from those posts only. For deployment you can forbid strings at decode time, for example
`eval generate --ban-string "—"`; leave that off in evaluation so the review measures what the
adapter learned rather than what decoding forbids.

The proxy reports style and function-word distance to your published prose, repeated 4-gram
share, how much of the input was copied through, and the longest verbatim run against any
training post (a memorization flag). `eval judge-packet` renders blinded pairwise prompts for a
frontier model with three of your training posts as the only evidence; run them with any
provider, save `{"id", "more_like_author", "confidence", "reason"}` per case, and unblind with
`eval judge-summarize`. Use these to pick a checkpoint. The blind human review in
`evals/README.md` remains the shipping gate.

### Preference optimisation

After SFT, sample the current adapter on the training inputs and train one DPO epoch with your
published text as the chosen response:

```bash
uv run goodprose eval generate \
  --config configs/qwen3-8b-lora.json \
  --cases data/private/train-cases.jsonl \
  --role candidate --adapter runs/qwen3-8b-lora --run-id sft-final \
  --output data/private/rejected.jsonl --manifest data/private/rejected-run.json

uv run goodprose build-preference \
  --pairs data/private/pairs.jsonl \
  --rejected data/private/rejected.jsonl \
  --rejected-manifest data/private/rejected-run.json \
  --roles data/training-roles.jsonl \
  --output data/sft/preference.jsonl

uv run goodprose train-dpo --config configs/qwen3-8b-dpo.json --validate-only
uv run goodprose train-dpo --config configs/qwen3-8b-dpo.json
```

The DPO config continues the SFT adapter, keeps an SFT term on the chosen text (`rpo_alpha`),
and uses the adapter-disabled model as the frozen reference. Watch the proxy for length or
formatting drift, the usual way DPO cheats.

## Repository map

```text
data/posts/             imported canonical blog posts
data/external/          approved Assembled and Medium source catalog
data/splits.jsonl       frozen lineage-level train/dev/test assignments
data/training-roles.jsonl per-post role (pairs, raw_only, excluded) and venue note
data/posts/normalization.json configured surface conventions and reviewed substitutions
data/provenance/        authoring-history coverage without raw private prompts
data/chunks/            verbatim semantic and reviewed supplemental targets
data/private/prompts/   synthetic training inputs and local review packet
data/private/external/  saved pages and authentic held-out inputs
data/private/eval/      original-site authentic held-out inputs
data/private/pairs.jsonl generated approved source-to-target pairs
data/sft/               generated training files
configs/                validated LoRA, LoRA+, 14B, and DPO run configurations
evals/cases.jsonl       generated frozen whole-post test cases
evals/short-cases.*     section-scale review candidates cut from the held-out drafts
evals/results/           local model outputs, proxy reports, judge packets, and reviews
docs/                    assessments and program notes
src/goodprose/           importer, pair builder, exporter, trainers, proxies, and evaluator
tests/                   deterministic unit tests
```

The previous executive-writing research program remains available in Git history and at the tag
`archive/executive-writing-program-2026-08-31`.
