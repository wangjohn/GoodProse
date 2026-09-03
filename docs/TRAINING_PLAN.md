# GoodProse training plan

State and plan as of 2 September 2026. The mechanics are in `README.md`, `data/README.md`, and
`evals/README.md`; this file says where the project stands and what happens next.

## Goal

A local adapter that turns John's rough drafts, outlines, and notes into finished blog prose in
his own voice, judged by a blind paired review against the prompted base model on four frozen
held-out posts, then on five fresh real drafts.

## Where we are

- 22 published posts, about 30k words, frozen by lineage into 15 train, 3 dev, 4 test posts.
  Canonical text is normalized to the author's conventions (straight quotes, `*italics*`,
  `#` sections), with what fired recorded per post.
- Target voice is the personal site. The Assembled posts had an editor's pass, so the four
  without a manuscript are `raw_only`, the one with a manuscript targets the manuscript, the two
  Assembled dev posts are excluded, and every user turn opens with a venue line.
- Chunks: 131 total. The supervised training material is 57 reviewed targets: 41 sections, 6
  sentence rewrites, and 10 whole-post `--full` chunks. Another 33 Assembled chunks feed raw
  completions only; their four full-post chunks remain eligible because they have no supervised
  pair.
- Development set: the watermarking post alone (about 3.4k words). Test: four posts, unchanged.
- All 57 prompts are approved against the current system prompt and match their current target
  hashes. Short cases: 14 candidates and 4 rejected, none approved yet.
- The current export has 57 supervised and 103 raw-completion records (160 total), 1 development
  case, and 4 frozen test cases. It contains 71,110 exact Qwen completion tokens; the longest
  rendered record is 5,138 tokens against a 6,144-token limit.
- The pipeline is complete and hash-checked end to end: import, normalize, chunk, brief,
  refresh, review, approve, pair, export, train, generate, dev NLL, stylometric proxy, judge
  packet, blind review, preference build, DPO. Training itself has not run on the new data.

## Before the next training run

The local promotion and validation gates are complete. On the RunPod machine, in this order:

1. Pull the repository and transfer the ignored generated/private artifacts needed by the run,
   especially `data/sft/`, or rebuild them from `data/private/` on the pod.
2. Install the GPU dependencies with `uv sync --extra train`.
3. Re-run `train-lora-plus --config configs/qwen3-8b-lora-plus.json --validate-only` on the pod.
4. Start the LoRA+ run. The validated recipe uses Qwen3-8B, learning rates 5e-5 for LoRA A and
   8e-4 for LoRA B, five epochs, and 200 optimizer steps.
5. Score development NLL and generate the deterministic checkpoint outputs before human review.

Keep the watermarking post as the development set. Dev NLL is the memorization detector and the
checkpoint selector; without it, selection would fall to the test short cases and weaken the
blind gate.

## Plan

### 1. Grow the training set at the scope of the test (John's time, highest value)

- Whole-post briefs for every `--full` chunk (ten drafted, one pending).
- Two to four more prompt forms per section chunk (bullets, rough sentences, phrases, near-final
  draft), roughened to look like real drafts, on the personal-site posts first.
- More of your own writing (memos, RFCs, long Slack posts, PR descriptions, talk scripts) under
  `data/private/` for the raw-completion mix.
- Capture every new draft with `capture-draft` before polishing; five of those become the
  prospective test set.

### 2. Run the recipe grid, picked by cheap proxies

- Arms: Qwen3-8B plain LoRA at 2e-4 (control), Qwen3-8B LoRA+ (16x ratio), Qwen3-14B 4-bit
  LoRA at 2e-4. Rank 32 on all linear layers, effective batch 4, 5 epochs, every epoch saved,
  dev loss every epoch.
- Decoding for every comparison is the deployment setting: sampled at 0.7 / top-p 0.9 /
  repetition penalty 1.05, fixed per-case seed, identical for both arms, with
  `Venue: johnjwang.com (2026)` on the user turn and `--ban-string` for em dashes if needed.
- For each checkpoint run `eval nll` on dev, `eval generate` on the test cases, `eval proxy`
  with `--reference-url-substring johnjwang.com`, and the blinded judge packet. Choose the
  checkpoint these agree on. Calibrate them once against the first blind review.
- Generate the strong prompted frontier baseline (three of your posts plus a style guide) on the
  test cases early. It is the bar, and the fallback teacher.

### 3. One preference pass

- Sample the chosen SFT adapter on the training inputs, build preference pairs with the
  published text as chosen and the sample as rejected, and run one DPO epoch that keeps an SFT
  term. Re-run the proxies and check for length or formatting drift.

### 4. Ship gate

- Short-case blind pass first (`build-short-cases`, approve, then review), then the blind human
  review on the four frozen test cases with the existing decision rules: every candidate output
  passes factuality and instruction following, more overall wins than the baseline, no held-out
  lineage lost, mean edit burden better by at least 0.5.
- Then five fresh real drafts against the prompted baseline. Ship only on at least four of five
  wins with no unsupported facts.

## Checks before a run you intend to keep

- Train prompt prefix byte-identical to the generation prompt (the manifests record the hash).
- No dev or test chunk text in any training record, including raw completions.
- Dev NLL logged per epoch; rising after epoch 2 means memorizing.
- Sampled dev outputs contain no 30-word verbatim runs from other published posts.
- Strong prompted frontier baseline generated for the four test cases.
- Pin `Qwen/Qwen3-14B` to a commit hash; drop `max_length` to 4096 on a 24 GB GPU.
- The first GPU run of `train-lora-plus`, `eval nll`, and `train-dpo` is a smoke test; the
  validate-only paths are unit-tested, the training paths are not.

## Guardrails already in place

- Training, scoring, DPO, and generation render the prompt through one function with
  `enable_thinking: false`; the assistant-prefix hash is recorded and compared across runs.
- Held-out chunks can never become training inputs; rebuilds preserve approvals only when a
  target is unchanged up to the recorded normalization; approvals are bound to the system prompt.
- Briefs must carry a target's code blocks verbatim; promotional footers are excluded; the pair
  builder rejects hiring CTAs and posts whose role is not `pairs`.

## Time split

Data 60 percent, proxy calibration 20 percent, recipe and model size 15 percent,
infrastructure 5 percent. Infrastructure is done; stop investing there.

## Sources

- LoRA Without Regret (Thinking Machines): https://thinkingmachines.ai/blog/lora/
- TRL summary: https://huggingface.co/docs/trl/en/lora_without_regret
- Qwen3 chat template deep dive: https://huggingface.co/blog/qwen-3-chat-template-deep-dive
- On-Policy Distillation (Thinking Machines): https://thinkingmachines.ai/blog/on-policy-distillation/
