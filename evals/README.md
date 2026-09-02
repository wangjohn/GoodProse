# Evaluation

`cases.jsonl` is generated from the `test` split by `goodprose build-sft`. It contains the held-out
input and the owner's published reference. The evaluator validates the reference checksum, then
omits the reference from the model inputs and blind review packet. This avoids grading by phrase
matching and keeps the review focused on whether the result is useful from the supplied material.

## Comparison design

Run these comparisons separately:

1. **Matched baseline:** base model and LoRA+ candidate use the same system prompt, chat template,
   decoding settings, and test inputs. This isolates the adapter's effect.
2. **Strong prompted baseline:** compare the candidate with the best practical base-model prompt,
   such as a reviewed few-shot prompt. Keep this in a separate review packet because the prompt
   strategies intentionally differ.

Each output file contains exactly one record per case:

```json
{"id":"held-out-post","output":"The model's proposed post."}
```

The primary pass uses the deployment decoding: sampled at temperature 0.7, top-p 0.9, repetition
penalty 1.05, with a fixed seed re-derived per case so any single case can be regenerated alone.
Greedy decoding over 1,500-word outputs mostly measures repetition failures, not voice; run it as
a secondary pass with `--temperature 0` if you want it. Both arms must use identical settings, and
`eval prepare` rejects manifests that differ.

## Freeze run provenance

For every output file, save a `GenerationRunManifest` JSON record containing:

- exact base model, model revision, tokenizer revision, and adapter identifier;
- prompt strategy (the chat-template kwargs), SHA-256 hashes of the system prompt and chat
  template, and a hash of the rendered assistant prefix the model was conditioned on;
- SHA-256 hashes of the frozen case file and training-dataset manifest; and
- temperature, top-p, repetition penalty, maximum new tokens, and seed.

When both manifests are passed to `eval prepare`, the evaluator rejects stale case hashes,
different base-model revisions, different tokenizers, different prompt/template/dataset hashes,
or different decoding settings. The run IDs are copied into the final summary. A strong-prompt
comparison is deliberately separate.

Generate matched outputs directly from the pinned training config. The generator uses the
dataset system prompt and the same chat-template kwargs as training (Qwen's non-thinking path)
for both roles, and verifies the rendered assistant prefix before loading the model:

```bash
uv run goodprose eval generate \
  --config configs/qwen3-8b-lora.json \
  --cases evals/cases.jsonl \
  --role baseline \
  --run-id base \
  --output evals/results/base.jsonl \
  --manifest evals/results/base-run.json

uv run goodprose eval generate \
  --config configs/qwen3-8b-lora.json \
  --cases evals/cases.jsonl \
  --role candidate \
  --adapter runs/qwen3-8b-lora/checkpoint-N \
  --run-id checkpoint-N \
  --output evals/results/checkpoint-N.jsonl \
  --manifest evals/results/checkpoint-N-run.json
```

Use an actual `checkpoint-N` directory from the training run and repeat for each checkpoint or the
final adapter you want to compare. Keep `--max-new-tokens`, `--seed`, `--temperature`, `--top-p`,
and `--repetition-penalty` identical if overriding their defaults.

## Inner loop: rank checkpoints without reading

A four-case human review is the shipping gate, not a tuning signal. Three cheaper proxies rank
checkpoints, data mixes, and model sizes in minutes; calibrate them once against a completed
blind review and then trust them for the inner loop.

1. **Dev NLL.** `eval nll --records data/sft/dev.jsonl` scores the three authentic dev pairs'
   completions under a checkpoint with the exact training render. Dev NLL rising while train
   loss falls is the memorisation signal.
2. **Stylometric proxy.** `eval proxy` compares each output file with your published training
   prose: sentence-length distribution, paragraph length, moving-window type-token ratio, and
   per-thousand-word rates of em dashes, parentheticals, questions, colons, list items,
   headings, links, bold, contractions, hedges, and first/second person, plus a cosine distance
   over function-word rates. Per case it also reports the length ratio to the reference, how
   much of the input was copied through, repeated 4-gram share (looping), and the longest
   verbatim run against any training post (regurgitation; flagged at 30 words). Lower distance
   is closer to you. The report ranks the systems it was given.
3. **Blinded frontier judge.** `eval judge-packet` renders one prompt per case with three of
   your training posts as the author samples, both responses in random order, and a single
   question: which is more likely written by this author. Run the prompts with any provider,
   save one `{"id", "more_like_author": "a"|"b"|"tie", "confidence", "reason"}` record per
   case, then `eval judge-summarize --verdicts ... --key ...` unblinds the tally.

```bash
uv run goodprose eval proxy \
  --cases evals/cases.jsonl \
  --outputs base=evals/results/base.jsonl \
  --outputs epoch3=evals/results/checkpoint-75.jsonl \
  --outputs epoch5=evals/results/checkpoint-125.jsonl \
  --posts data/posts/posts.jsonl --splits data/splits.jsonl \
  --output evals/results/proxy.json

uv run goodprose eval judge-packet \
  --cases evals/cases.jsonl \
  --baseline evals/results/base.jsonl --candidate evals/results/checkpoint-125.jsonl \
  --posts data/posts/posts.jsonl --splits data/splits.jsonl \
  --packet evals/results/judge.jsonl --key evals/results/judge-key.json
```

Run the strong prompted frontier baseline (three of your posts plus a short style guide) on the
four test inputs early, not last. It sets the bar, and if it wins it is the natural teacher for a
later distillation step.

## Quick review set: section-scale cases

Reading two whole posts per case is slow, and four cases give a coarse preference count. The
held-out posts are already split into verbatim sections, and each has an authentic draft, so
`build-short-cases` cuts every whole-post case into section-scale cases: for each held-out
section it finds the window of draft paragraphs that produced it (best F1 over word alignment),
prefixes a one-line scope instruction and the post title, and writes a candidate with recall and
precision scores. You approve or edit each candidate in `short-cases.candidates.jsonl`, then
promote the approved ones:

```bash
uv run goodprose build-short-cases \
  --cases evals/cases.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --posts data/posts/posts.jsonl \
  --output evals/short-cases.candidates.jsonl \
  --review-output evals/SHORT_CASES_REVIEW.md

# set "review_status": "approved" on the candidates you accept (edit "input" where needed), then
uv run goodprose promote-short-cases \
  --candidates evals/short-cases.candidates.jsonl \
  --output evals/short-cases.jsonl
```

`evals/short-cases.jsonl` is an ordinary case file: run `eval generate`, `eval proxy`,
`eval judge-packet`, `eval prepare`, and `eval summarize` on it exactly as on `cases.jsonl`. Each
row is a 250-word section instead of a 1,500-word post, so a full blind pass over 18 sections
takes about as long as one whole-post case, and the preference count is 18 instead of 4.
Sections still carry their `lineage_id`, so the per-lineage rules apply. Rebuilding keeps your
edits and decisions for any section whose text is unchanged, and promotion refuses an input that
contains its reference section verbatim.

Candidates with low recall mean you wrote most of that section fresh rather than from the draft,
so the aligned window is a weak brief; rewrite the input by hand from the draft or reject it.
Promotional sections are skipped. The whole-post cases in `cases.jsonl` stay the shipping gate:
the short set is for choosing between checkpoints, not for the final go/no-go.

`build-sft --dev-cases-output` writes the three development pairs in the same case format so the
same cut can be made for dev and used to calibrate the proxies.

## Blind review

Put outputs under ignored `results/`, then prepare a randomized packet and reviewer guide:

```bash
uv run goodprose eval prepare \
  --cases evals/cases.jsonl \
  --baseline evals/results/base.jsonl \
  --candidate evals/results/lora.jsonl \
  --baseline-manifest evals/results/base-run.json \
  --candidate-manifest evals/results/lora-run.json \
  --packet evals/results/review.jsonl \
  --key evals/results/review-key.json \
  --guide evals/results/REVIEW.md
```

Complete the packet without opening the unblinding key or published references. For A and B,
record factuality, every unsupported claim when factuality fails, instruction following, voice
preference, overall preference, and edit burden. The anchored edit-burden scale is:

1. publishable as written;
2. light wording or transition edits;
3. substantial paragraph or structural edits;
4. rewrite most of it, though some material is reusable;
5. unusable or complete rewrite.

Unsupported facts are a hard failure even when the response sounds better.

## Decision

Summarize only after every required review field is complete:

```bash
uv run goodprose eval summarize \
  --packet evals/results/review.jsonl \
  --key evals/results/review-key.json \
  --decision-rules evals/decision-rules.json \
  --output evals/results/summary.json
```

The checked-in rule set recommends the candidate only when all of these are true:

- every candidate output passes factuality and instruction following;
- the candidate wins more cases overall than the baseline;
- no held-out blog lineage is a net loss and at least one is a net win; and
- mean edit burden improves by at least 0.5 on the five-point scale.

The summary preserves per-case findings and reports results by lineage and input method, rather
than treating related sections as independent posts. It also lists every failed decision check.
With a small test set, treat the rule as a shipping gate for this run, not a claim of statistical
significance.

## Prospective check

After the offline gate passes, use five fresh, real writing requests that were never derived from a
published target. Blindly compare the full workflow against the strong prompted baseline. Ship the
adapter only if it wins at least four of five, has no unsupported-fact failures, and actually lowers
the author's editing burden. Keep these requests out of training even after the review if they may
be reused as a stable prospective benchmark.
