# GoodProse training plan

Executive summary as of 2 September 2026. The long-form reasoning is in
`docs/fine-tuning-assessment-2026-09-02.md`; the mechanics are in `README.md` and `evals/README.md`.

## Goal

A local adapter that turns John's rough drafts, outlines, and notes into finished blog prose in
his own voice, judged by a blind paired review against the prompted base model on four frozen
held-out posts, then on five fresh real drafts.

## Where we are

- 22 published posts, about 30k words, frozen by lineage into 15 train, 3 dev, 4 test posts.
- Every training target is John's verbatim published text. No synthetic completions.
- The pipeline is complete: import, chunk, brief, review, approve, pair, export, train, generate,
  proxy-score, blind-review, preference-build, DPO. Hash-checked end to end.
- The dataset is the constraint. It has 68 section-level briefs and no whole-post training pairs,
  while the test asks for whole posts from real drafts.

## Plan

### 1. Rebuild the training set at the scope of the test (John's time, highest value)

- Write one realistic whole-post brief or messy draft for each of the 15 training posts,
  targeting the 15 new `--full` chunks. Match how you actually hand notes to an assistant.
- Add two to four more prompt forms per section chunk (bullets, rough sentences, phrases,
  near-final draft), roughened to look like your real drafts. Review and approve in the existing
  packet.
- Bring in other writing you own (memos, RFCs, long Slack posts, PR descriptions, talk scripts)
  under `data/private/` for the raw-completion mix.
- Target: roughly 300 supervised pairs plus 15 whole-post pairs plus raw completions of every
  target, up from 68 pairs.

### 2. Run the recipe grid, picked by cheap proxies

- Arms: Qwen3-8B plain LoRA at 2e-4 (control), Qwen3-8B LoRA+ (16x ratio), Qwen3-14B 4-bit
  LoRA at 2e-4. Rank 32 on all linear layers, effective batch 4, 5 epochs, every epoch saved,
  dev loss every epoch.
- Decoding for every comparison is the deployment setting: sampled at 0.7 / top-p 0.9 /
  repetition penalty 1.05, fixed per-case seed, identical for both arms.
- For each checkpoint run `eval nll` on dev, `eval generate` on the test cases, `eval proxy`
  against the published training prose, and the blinded frontier judge packet. Choose the
  checkpoint these agree on. Calibrate them once against the first blind review.
- Also generate the strong prompted frontier baseline (three of your posts plus a style guide)
  on the test cases early. It is the bar, and the fallback teacher.

### 3. One preference pass

- Sample the chosen SFT adapter on the training inputs, build preference pairs with the
  published text as chosen and the sample as rejected, and run one DPO epoch that keeps an SFT
  term. Re-run the proxies and check for length or formatting drift.

### 4. Ship gate

- Blind human review on the four frozen test cases with the existing decision rules: every
  candidate output passes factuality and instruction following, more overall wins than the
  baseline, no held-out lineage lost, mean edit burden better by at least 0.5.
- Then five fresh real drafts, saved before you polish them, against the prompted baseline.
  Ship only on at least four of five wins with no unsupported facts.

## Data decisions taken on 2 September (later)

- Target voice is the personal site. The Assembled posts had an editor's pass: the four without
  a manuscript are `raw_only` under an `editor-revised` venue note, the one with a manuscript
  targets the manuscript, and the two Assembled dev pairs are excluded.
- Every user turn opens with `Venue: host (year)`; ask for `Venue: johnjwang.com (2026)` at
  inference. Personal-site raw completions are weighted 2x.
- Canonical posts are normalized to the author's conventions (straight quotes, `*italics*`,
  `#` sections); em dashes are not auto-replaced but the proxy reports them and decoding can
  ban them.
- Flattened code in scraped posts is repaired from manuscripts, with a fencing fallback; briefs
  must carry a target's code blocks verbatim.
- New drafts are captured with `capture-draft` before polishing to build the prospective set.

## Guardrails already in place

- Training, scoring, DPO, and generation render the prompt through one function with
  `enable_thinking: false`; the assistant-prefix hash is recorded and compared across runs.
- Held-out chunks can never become training inputs; rebuilds preserve approvals only for
  unchanged targets.
- Promotional footers are excluded from targets; the pair builder rejects hiring CTAs.

## Time split

Data 60 percent, proxy calibration 20 percent, recipe and model size 15 percent,
infrastructure 5 percent. Infrastructure is done; stop investing there.

## Open items

- Pin `Qwen/Qwen3-14B` to a commit hash before a run you intend to keep.
- Drop `max_length` from 6144 to 4096 on a 24 GB GPU.
- Confirm the Assembled and Medium snapshots used as targets are your prose, not an editor's;
  where a private manuscript exists, diff it against the published text.
- First GPU run of `train-lora-plus`, `eval nll`, and `train-dpo` is a smoke test; the
  validate-only paths are unit-tested, the training paths are not.
