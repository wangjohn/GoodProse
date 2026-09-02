#!/usr/bin/env bash
# Rebuild the canonical data from private sources after the September 2026 data decisions.
#
# Runs on the author's machine, where data/private/ exists. Stops before approval: reading the
# review packet and running approve-prompts is deliberately a human step.
#
# Usage: scripts/rebuild-data.sh            (from the repository root)
set -euo pipefail
cd "$(dirname "$0")/.."

PRIVATE=data/private
RAW=$PRIVATE/posts/raw-posts.jsonl

echo "==> 1. Merge external snapshots, repair code from manuscripts, target the scaling-llms manuscript"
uv run goodprose build-external-posts \
  --catalog data/external/posts.jsonl \
  --snapshot-root $PRIVATE/external/published-raw \
  --base-posts $PRIVATE/posts/johnjwang-posts.jsonl \
  --source-map $PRIVATE/external/source-map.jsonl \
  --source-root $PRIVATE/external/blogposts-source \
  --repair-code \
  --fence-heuristic go \
  --target-from-manuscript external-scaling-llms-golang \
  --output "$RAW"

echo "==> 2. Normalize to the author's conventions (records what fired on each post)"
uv run goodprose normalize-posts \
  --raw "$RAW" \
  --config data/posts/normalization.json \
  --output data/posts/posts.jsonl

echo "==> 3. Rebuild chunks; approvals carry forward when only normalization changed a target"
uv run goodprose build-chunks \
  --posts data/posts/posts.jsonl \
  --splits data/splits.jsonl \
  --exclusions data/chunks/exclusions.jsonl \
  --supplemental-targets data/chunks/supplemental-targets.jsonl \
  --full-posts \
  --normalization data/posts/normalization.json \
  --output data/chunks/candidates.jsonl \
  --review-output data/chunks/REVIEW.md

echo "==> 4. Align the existing briefs: drop demoted posts, rehash formatting-only changes, reset real changes"
uv run goodprose refresh-prompts \
  --prompts $PRIVATE/prompts/candidates.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --roles data/training-roles.jsonl \
  --normalization data/posts/normalization.json

echo "==> 5. Attach the whole-post brief drafts to the --full chunks"
uv run goodprose build-prompt-candidates \
  --drafts data/prompts/full-post-drafts.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --base-prompts $PRIVATE/prompts/candidates.jsonl \
  --output $PRIVATE/prompts/candidates.jsonl

echo "==> 6. Render the review packet with the system prompt and venue lines"
uv run goodprose review-prompts \
  --prompts $PRIVATE/prompts/candidates.jsonl \
  --chunks data/chunks/candidates.jsonl \
  --posts data/posts/posts.jsonl \
  --roles data/training-roles.jsonl \
  --output $PRIVATE/prompts/REVIEW.md

cat <<'EOF'

Done. Now the human steps:

  * Read data/private/prompts/REVIEW.md. Edit or reject briefs directly in
    data/private/prompts/candidates.jsonl. Briefs flagged "Missing code block(s)" need the
    target's fenced code pasted in verbatim.
  * Approve (this stamps the system prompt onto every approval):
      uv run goodprose approve-prompts \
        --prompts data/private/prompts/candidates.jsonl \
        --chunks data/chunks/candidates.jsonl \
        --reviewer-note 'Re-read with the system prompt and venue line on <date>.'
  * Then build pairs and export:
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
        --train-cases-output data/private/train-cases.jsonl \
        --dev-cases-output data/private/dev-cases.jsonl
      uv run goodprose train-lora-plus --config configs/qwen3-8b-lora.json --validate-only
EOF
