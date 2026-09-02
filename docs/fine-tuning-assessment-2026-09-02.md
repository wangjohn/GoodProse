# GoodProse fine-tune assessment (2 Sep 2026)

Assessed branch: `codex/goodprose-v0` at `6a4b5e3` (Enforce non-promotional SFT pairs).
Repo checks on that branch: 39 tests pass, ruff clean.

## Verdict

The pipeline is finished; the dataset is not. Training teaches "expand a synthetic brief into a
~260-word section." The test asks "turn my real 900–2,200-word rough draft into a finished post."
The adapter is graded on a job it never practised. Infrastructure work should stop. Remaining
leverage is almost entirely data, followed by a short list of recipe fixes and a cheap iteration
loop.

## Where you are

| Split | Posts | Words  | Input type                                  | Target granularity                 |
|-------|------:|-------:|---------------------------------------------|------------------------------------|
| train |    15 | 19,021 | 68 synthetic derived briefs, one per chunk  | section or sentence (median 263 w) |
| dev   |     3 |  5,534 | authentic drafts / notes                    | whole post                         |
| test  |     4 |  6,207 | authentic drafts                            | whole post                         |

- 75 approved training targets: 61 default sections, 4 cleaned closers, 10 single sentences.
  About 18.6k words (~25k tokens) of supervised completion text.
- Recipe: Qwen3-8B (pinned), LoRA r=32 α=64 all-linear, LoRA+ (A 5e-5, B 8e-4), 3 epochs,
  effective batch 8 → ~27 optimizer steps total, cosine, warmup 5% (~1 step), completion-only
  loss, `eval_strategy: "no"`. Generation: greedy, thinking disabled, 8,192 max new tokens.
- Eval: blind paired human review, factuality hard gate, voice vs overall preference, 1–5 edit
  burden, explicit decision rules.
- Not visible from the repo: whether a full run completed and what the loss did (results are
  gitignored).

## What is strong

- Targets are your unedited published words. No synthetic completions.
- Lineage-level frozen splits with hash-checked manifests.
- Evaluation design is the right shape (blind, paired, factuality gate, edit burden).
- Seven posts have authentic recovered inputs, correctly reserved for dev/test.

## Problems, ranked by quality cost

### 1. Training and evaluation are different tasks (highest)

Share of each test reference already present verbatim in its input:

| Test case                              | In words | Out words | Output in input | Longest shared run |
|----------------------------------------|---------:|----------:|----------------:|-------------------:|
| learnings-from-the-codex-repo          |    2,218 |     2,147 |             84% |          761 words |
| external-new-products-team             |    1,391 |     1,417 |             90% |          353 words |
| external-database-abstractions-golang  |    1,305 |     2,017 |             41% |           42 words |
| why-we-built-143                       |      888 |       620 |             20% |            9 words |

Two test cases are light-edit tasks; one is a true rewrite. Training has zero post-scale examples
of either, and no target longer than ~500 words, so the model never learns openings, transitions,
or closings.

**Fix:** add whole-post pairs for all 15 train posts (brief → post; rough draft → post). Add
"polish" pairs with a deliberately roughened published post as input. Keep section pairs. Match
the training input mix to the test input mix.

### 2. Synthetic inputs do not look like your real inputs (high)

Real drafts have lowercase "i", typos, run-ons, prose followed by a bullet dump. Synthetic briefs
were written to a review rubric and are tidy.

**Fix:** give the brief generator 2–3 real drafts as exemplars of *input* style; vary form per
target; keep the roughness.

### 3. One prompt per target caps the dataset at 68 examples (high)

`_candidate_chunk_map` rejects multiple candidates per chunk. You cannot get more targets, so get
more views: 3–5 diverse briefs per chunk → 250–350 examples with no new writing.

**Fix:** uniqueness key `(chunk_id, prompt_form)`; generate several forms per chunk.

### 4. Dev set unused in training; eval loop too expensive to iterate (medium)

No held-out loss curve; the only checkpoint signal is a 4-case blind review.

**Fix:** `eval_strategy: "epoch"` with per-token dev NLL. Add an automatic proxy run on every
checkpoint: dev NLL, stylometric distance to your published posts (sentence-length distribution,
type-token ratio, function-word profile, em-dash/parenthetical rate), repetition check, and a
frontier judge asked only "which is more likely by the author of these three reference posts."
Human blind review stays as the final gate.

### 5. Qwen3 chat-template mismatch (medium, verify)

Inference renders with `enable_thinking=False`, appending `<think>\n\n</think>\n\n` after the
assistant header. TRL renders the training prompt with default kwargs, so completions start right
after `<|im_start|>assistant\n`. The adapter never sees the prefix it is conditioned on.

**Fix:** dump one tokenized train example and compare prefixes to the generation prompt. Pass
`enable_thinking=False` through the training template, or prepend the empty think block to every
completion and match at generation.

### 6. Greedy decoding for long prose (medium)

Greedy on an 8B fine-tune over 1,500 words loops and flattens, and is not the deployment setting.

**Fix:** primary config = deployment config: temperature 0.7, top-p 0.9, repetition penalty ~1.05,
fixed seed, identical for both arms.

### 7. Recipe details (low, free)

- 27 steps is too few for a cosine schedule to matter. With 4× data, sweep epochs {3, 5, 8} by dev
  NLL + proxy; watch for memorisation.
- LoRA+ B at 8e-4 is aggressive. Best evidence (LoRA Without Regret) puts optimal LoRA LR ~10×
  full FT, roughly 1e-4–2.5e-4 with Adam; rank matters little at small data; LoRA dislikes large
  batches. Run plain LoRA at 2e-4 as a control. Keep effective batch ≤ 8.
- Rank 32 all-linear is fine. Weight decay 0 is fine.

### 8. Some targets may not be your voice (low, check)

Nine of fifteen train posts are Assembled/Medium snapshots that may have been edited by others.
Where private author Markdown exists (five posts), diff against the published text; if edits are
heavy, prefer the manuscript or down-weight the post.

## Method landscape

- **LoRA SFT** — still the backbone. All-layer LoRA incl. MLP matches full FT at this scale.
  LoRA+ is one arm of a comparison, not the default. Skip DoRA/rsLoRA novelty.
- **Continued pretraining on raw text** — add. Promptless completions of your posts/sections teach
  unconditional voice statistics; cheapest way to extract more signal from 19k words.
- **DPO with the model as the negative** — add second. Chosen = your published text, rejected =
  SFT-model output for the same brief (on-policy). One epoch, moderate β, consider DPO+SFT (RPO).
  Watch for length/format reward hacking via the stylometric proxy.
- **On-policy distillation** — skip for now; no teacher yet. Revisit if a frontier few-shot
  prompt beats the adapter; then it becomes the teacher.
- **Model size** — change. The adapter nudges the base; prose competence comes from the base.
  Compare 8B vs Qwen3-14B (QLoRA on 24 GB); consider 32B / Gemma 3 27B on 48 GB.
- **Strong prompted baseline** — run it now, not last. It sets the bar and is a candidate teacher.

## Time budget

| Area                   | Share | What                                                                  |
|------------------------|------:|-----------------------------------------------------------------------|
| Data                   |   60% | see below                                                             |
| Fast eval loop         |   20% | automatic proxy calibrated once against a blind review                |
| Recipe and model size  |   15% | template parity, decoding, then {8B,14B}×{LoRA,LoRA+}×{3,6 ep}, 1 DPO |
| Infrastructure         |    5% | stop                                                                  |

Data, in order:

1. Write a realistic whole-post brief or messy draft for each of the 15 train posts yourself, the
   way you would actually hand it off. Highest-value hours in the project.
2. Generate 3–5 briefs per training chunk in different forms, roughened with real drafts as
   exemplars; skim-review in the existing packet.
3. Emit promptless completions of every train post/section for the CPT mix (no review needed).
4. Bring in more of your own writing (memos, RFCs, long Slack posts, PR descriptions, talk
   scripts, threads) under `data/private/`; even CPT-only, +30–50k words likely matters more than
   any modelling change.
5. Start the prospective test set now: save your next five real rough drafts the moment you start
   writing.

## Concrete repo changes

```
configs/qwen3-8b-lora-plus.json (and a 14B sibling)
  "eval_strategy": "epoch"            # was "no"
  "num_train_epochs": 5               # sweep 3/5/8 once data is 4x larger
  "gradient_accumulation_steps": 4
  "save_total_limit": 8

generation.py
  do_sample=True, temperature=0.7, top_p=0.9, repetition_penalty=1.05, fixed seed, both arms

training.py
  assert tokenized train prompt prefix == rendered generation prompt prefix
  pass enable_thinking=False into the training template, or prepend the empty think block

prompts.py
  uniqueness key (chunk_id, prompt_form) instead of chunk_id

sft.py
  whole-post pairs for train lineages; promptless CPT completions;
  later: preference records {prompt, chosen=published, rejected=sft_output}
```

## Verify before the next run

- [ ] Train prompt prefix byte-identical to generation prompt (think-block parity).
- [ ] No dev/test chunk text in any training record, including multi-prompt and CPT records.
- [ ] Dev NLL logged per epoch; rising after epoch 2 means memorising.
- [ ] Sampled dev outputs contain no 30+-word verbatim runs from other published posts.
- [ ] Strong prompted frontier baseline generated for the 4 test cases.
- [ ] Assembled snapshots kept as targets are your prose, not an editor's.

## Sources

- LoRA Without Regret (Thinking Machines): https://thinkingmachines.ai/blog/lora/
- TRL summary: https://huggingface.co/docs/trl/en/lora_without_regret
- TRL SFTTrainer docs: https://github.com/huggingface/trl/blob/main/docs/source/sft_trainer.md
- Qwen3 chat template deep dive: https://huggingface.co/blog/qwen-3-chat-template-deep-dive
- On-Policy Distillation (Thinking Machines): https://thinkingmachines.ai/blog/on-policy-distillation/
