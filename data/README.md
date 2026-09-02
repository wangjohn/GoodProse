# Data

The canonical data flow is:

```text
Markdown blog export -> private/posts/johnjwang-posts.jsonl (raw)
external snapshots   -> private/posts/raw-posts.jsonl (merged raw; code repaired from manuscripts)
normalization        -> posts/posts.jsonl (configured conventions, recorded per post)
training roles       -> training-roles.jsonl (pairs / raw_only / excluded, venue notes)
frozen lineage split -> splits.jsonl
semantic candidates  -> chunks/candidates.jsonl
synthetic candidates -> private/prompts/candidates.jsonl (review only)
approved train inputs -> private/pairs.jsonl
authentic eval inputs -> private/eval/pairs.jsonl + private/external/eval-pairs.jsonl
SFT build            -> sft/train.jsonl (+ raw completions) and sft/dev.jsonl
test split           -> ../evals/cases.jsonl
train inputs         -> private/train-cases.jsonl (for on-policy rejected sampling)
preference build     -> sft/preference.jsonl (chosen = published, rejected = SFT output)
```

Canonical posts, briefs, and pairs may be committed when they are safe to publish. Generated SFT
files are ignored because they can be rebuilt byte-for-byte from the canonical pairs.

`provenance/inventory.jsonl` records which posts have recoverable authentic authoring inputs
without publishing raw conversation text. Unreviewed extracts remain under ignored
`data/private/`. Semantic chunks are deterministic, verbatim spans. The 75 section and sentence
chunks referenced by training prompts were approved by the author on 2026-09-01; rebuilds keep
those approvals when the target text is unchanged. The 15 `--full` chunks added on 2026-09-02
are post-scale candidates (the prefix of each training post up to its last kept section) and
need a prompt plus approval before they can train. Development and test chunks remain candidates
and cannot pass the training promotion gate.

Synthetic prompts are built only against training chunks and remain under ignored `data/private/`.
Each (chunk, prompt form) pair may appear once, so one target can carry a bullet-notes brief, a
rough-sentences brief, a phrases brief, and for whole posts a `post_brief`, `rough_draft`, or
`near_final_draft`. Write them in the register of your real drafts, roughness included. The
local review packet pairs each input with its exact completion, requires target citation URLs to
be present in the input, and reports the longest verbatim word run as a leakage-review aid
(expected to be long for the draft forms).

`posts/normalization.json` is the only place canonical text differs from the raw import, and
every post records the normalizations that fired. The conventions follow the author's personal
site: straight quotes, `*italics*`, section headings at `#`, plus two reviewed substitutions (a
Hugo math span and a caption remnant). `normalize-posts` must run from the raw file so a stale
substitution fails loudly. `build-chunks --normalization` carries approvals forward when only the
normalization changed a target.

`training-roles.jsonl` records how each post may train. The Assembled posts had an editor's pass,
so the four without a recovered manuscript are `raw_only` (title-conditioned raw completions
under `Venue: assembled.com (year), editor-revised`, never supervised pairs), the one with a
manuscript targets the manuscript text instead, and the two Assembled development pairs are
`excluded` because manuscript-to-edited pairs would measure imitation of the editor. Test posts
cannot be demoted. Every exported user turn opens with a venue line derived from the post's URL
and year, so the 2021 Medium register and the 2026 personal-site register are conditions the
model can tell apart; at inference, ask for `Venue: johnjwang.com (2026)`.

`external/posts.jsonl` catalogs thirteen approved Assembled and Medium posts. Their normalized
published snapshots are canonical targets in `posts/posts.jsonl`. Recovered author Markdown,
public snapshots, line-range maps, authentic held-out inputs, and generated pairs stay under
ignored `private/external/`. The two development and two test posts have authentic drafts or
outlines; synthetic inputs are generated only for training chunks.

Approval covers the whole training conversation, not the brief alone. The review packet quotes
the exact system prompt and its hash, `approve-prompts` records that hash on every approved
candidate, and `build-prompt-pairs` rejects any candidate approved against a different system
prompt. Editing `SYSTEM_PROMPT` therefore invalidates existing approvals until they are
re-reviewed and re-approved.

`build-prompt-pairs` is the promotion gate for section-level training data. It verifies frozen
metadata and target hashes, rejects any prompt or chunk that is not explicitly approved, and can
merge the resulting training sections with authentic held-out pairs for `build-sft`.
