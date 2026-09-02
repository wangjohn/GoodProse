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

Use temperature `0` for the primary pass. If deployment will use sampling, run repeated robustness
checks afterward; do not mix repeated samples into the primary decision count.

## Freeze run provenance

For every output file, save a `GenerationRunManifest` JSON record containing:

- exact base model, model revision, tokenizer revision, and adapter identifier;
- prompt strategy plus SHA-256 hashes of the system prompt and rendered chat template;
- SHA-256 hashes of the frozen case file and training-dataset manifest; and
- temperature, top-p, maximum new tokens, and seed.

When both manifests are passed to `eval prepare`, the evaluator rejects stale case hashes,
different base-model revisions, different tokenizers, different prompt/template/dataset hashes,
or different decoding settings. The run IDs are copied into the final summary. A strong-prompt
comparison is deliberately separate.

Generate matched outputs directly from the pinned training config. The generator uses greedy
decoding, the dataset system prompt, and Qwen's non-thinking chat-template path for both roles:

```bash
uv run goodprose eval generate \
  --config configs/qwen3-8b-lora-plus.json \
  --cases evals/cases.jsonl \
  --role baseline \
  --run-id base \
  --output evals/results/base.jsonl \
  --manifest evals/results/base-run.json

uv run goodprose eval generate \
  --config configs/qwen3-8b-lora-plus.json \
  --cases evals/cases.jsonl \
  --role candidate \
  --adapter runs/qwen3-8b-lora-plus/checkpoint-N \
  --run-id checkpoint-N \
  --output evals/results/checkpoint-N.jsonl \
  --manifest evals/results/checkpoint-N-run.json
```

Use an actual `checkpoint-N` directory from the training run and repeat for each checkpoint or the
final adapter you want to compare. Keep `--max-new-tokens` and `--seed` identical if overriding
their defaults.

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
