# Data review (2 September 2026)

A read of the actual data on this branch: the 22 published targets in `data/posts/posts.jsonl`,
the 129 chunks, the frozen splits, the four whole-post test cases and their drafts, and the 18
short-case candidates. Measurements below come from the repo's own tooling (`goodprose.proxy`
style features and `goodprose.text` alignment) plus a few one-off scans. The private training
briefs under `data/private/` were not available, so this covers targets, inputs, and structure,
not the 68 briefs themselves.

## Summary

Two findings matter more than everything else combined.

1. **Three code-bearing posts were scraped without their code fences, and one lost its
   whitespace.** `external-scaling-llms-golang` is a training post whose three approved chunks
   contain 75 lines of Go rendered as prose with tokens fused (`err!=nil`, `schema,
   err:=jsonschema...`). The dev post `external-llm-provider-fallbacks` has 50 such lines and the
   test reference `external-database-abstractions-golang` has 206 (740 of its 2,106 words), while
   its authentic input carries 8 proper fences. Training on this teaches the adapter to emit
   broken, unfenced code as blog prose; dev loss penalizes correct code; the test reference
   misstates edit burden. All three have recovered author Markdown, so the fences can be restored
   by splicing rather than guessing.
2. **Only 30 percent of training words are in your personal-site voice.** The rest is 40 percent
   Assembled engineering blog and 30 percent Medium essays from 2021 to 2023, and those registers
   are measurably different: the company posts say "we" seven times as often as your personal
   posts, hedge a third as much, use bold three times as often, and use em dashes six times as
   often. The adapter will learn a blend that is mostly not the voice you want.

Everything else is hygiene: quote and heading conventions differ by source, one caption remnant
and one HTML span sit inside approved targets, two chunks end on a colon with their list cut off,
and one approved chunk is 100 percent code. Cross-split leakage is clean and there is no
boilerplate repeated across posts.

## Findings

### 1. Unfenced and mangled code in scraped targets

| Post | Split | Unfenced code lines | Words in them | Author Markdown recovered |
|---|---|---:|---:|---|
| external-database-abstractions-golang | test | 206 of 273 | 740 of 2,106 | yes (input has 8 fences, reference 0) |
| external-scaling-llms-golang | train | 75 of 112 | 180 of 962 | yes |
| external-llm-provider-fallbacks | dev | 50 of 101 | 165 of 1,226 | yes |

The Medium and Assembled page snapshots rendered `<pre>` blocks as plain lines. In the Assembled
snapshots the surrounding whitespace was also dropped, so `if err != nil {` became `if err!=nil {`.
The three approved training chunks `external-scaling-llms-golang--001/002/003` are affected in
full; `external-tests-with-llms--005` has three code-like lines. Because the whole-post
`database-abstractions` reference is a third code, its five short-case candidates also aligned
poorly (recall 0.12 to 0.61) partly for this reason: the input has fenced code and the reference
does not.

### 2. Register imbalance and drift

Style profile per source, rates per 1,000 words, computed on the published targets:

| Feature | johnjwang.com | Assembled | Medium 2021–23 |
|---|---:|---:|---:|
| mean paragraph words | 46.6 | 36.2 | 26.1 |
| "we / our / us" | 3.9 | 28.9 | 19.3 |
| "I / my / me" | 14.0 | 8.7 | 14.5 |
| "you / your" | 15.9 | 8.1 | 13.1 |
| hedges ("I think", "probably", "pretty", …) | 8.5 | 2.5 | 1.2 |
| "I think" | 1.77 | 0.10 | 0.11 |
| em dashes | 0.25 | 1.53 | 1.64 |
| bold spans | 1.8 | 6.3 | 2.7 |
| colons | 10.3 | 20.3 | 17.3 |
| parentheticals | 10.3 | 16.0 | 21.5 |
| exclamation marks | 0.42 | 0.92 | 3.06 |
| curly apostrophes | 1.3 | 10.2 | 20.3 |
| straight apostrophes | 22.1 | 9.8 | 0.0 |

Style distance from the personal-site training profile: Assembled 0.68, Medium 0.59, personal
2026 posts 0.30. The five posts farthest from your personal voice are all Assembled or Medium
technical posts (`llm-provider-fallbacks`, `better-rag`, `scaling-llms-golang`,
`database-abstractions-golang`, `code-review-bottlenecks`). Some of that is genre (code, lists),
but the "we" rate, hedge rate, em dashes, and bold are register, not genre.

Training words by source: johnjwang.com 5,756 (30 percent), Assembled 7,631 (40 percent), Medium
5,634 (30 percent). The Medium share is three posts from 2021 to 2023, so 28 percent of the
training text is three to five years old.

The frozen test set has the same skew: two of four posts are 2023 Medium posts, and the test
profile sits closer to Medium than to your personal site (first person singular 5.6 per 1,000
versus 14.0). The whole-post gate therefore partly measures a 2023 Medium voice. The short cases
inherit this. The test set stays frozen, but the prospective set should be personal-site drafts.

### 3. Formatting conventions differ by source

- Quotes: personal site is straight (22 per 1,000 straight apostrophes, 1.3 curly); Medium is
  entirely curly; Assembled is mixed. The adapter will learn an inconsistent habit.
- Headings: personal posts use `#` for sections; Assembled and Medium snapshots use `##` and
  `###`. Same effect.
- Italics: Medium and Assembled use `_x_`; personal posts use `*x*`.
- `cheap-software-wont-make-engineering-cheap--002` (approved) contains
  `<span class="no-math">…\$200+…\$5k+…</span>`, a Hugo/KaTeX escape in the site source.
- `external-stripe-customer-support--002` (approved) contains the caption remnant
  `Graph from From [https://…](https://…)`, including the "from From" typo.
- `external-ai-coding-interviews` (dev) has one non-breaking space.

### 4. Chunk boundaries

- `how-claude-watermarking-probably-works--008` (dev) ended on a colon with the table it
  introduces cut into the next chunk; the chunker now keeps an introducing colon with its list
  or table. `external-stripe-customer-support--001` also ends on a colon, but what follows is a
  heading: the author is introducing the sections, so that boundary is right.
- `external-tests-with-llms--004` (train, approved, 123 words) is 100 percent code: a prompt
  template inside a fence. `--002` and `--003` are 59 and 78 percent code. These teach the
  adapter to compose code blocks from a brief, which is not the skill you want and is where
  factuality failures will come from.
- Ten approved single-sentence targets (9 to 35 words). Harmless, low signal; the review time
  they cost is worth more elsewhere.

### 5. Things that are fine

- Cross-split leakage: the longest word run shared between any held-out post and any training
  post is 8 words, all generic phrases. Test drafts share at most 6 words with any training post.
- No 6-gram appears in three or more posts, so there is no bio or footer boilerplate left.
- The 15 new `--full` targets contain no hiring calls to action.
- Splits are lineage-clean; every held-out post has an authentic input.

## Recommended changes, in order

Status (2 September 2026, later the same day): the author confirmed the Assembled posts had an
editor's pass, prefers no em dashes, types straight quotes, and wants the personal-site voice.
Items 1, 2, 4, 5, 6, and 7 below are implemented on this branch (`normalize-posts`,
`training-roles.jsonl`, venue lines, `build-external-posts --repair-code`, `--fence-heuristic`
and `--target-from-manuscript`, the chunker fix, code pass-through in briefs, `--reference-url-substring`
for the proxy and judge, `eval generate --ban-string`). Item 3 and the prospective set remain the
author's work. The Assembled decision (item 9) is applied through the roles file.

| # | Change | Effort | Effect |
|---|---|---|---|
| 1 | Repair code blocks in the three scraped posts by splicing the author Markdown's fenced blocks over the mangled runs, matched on whitespace-stripped tokens; until then exclude `external-scaling-llms-golang--001/002/003` from training | half a day | removes corrupt targets from train, dev, and the test reference |
| 2 | Add a register line to every user turn at export, derived from post metadata (`Register: personal blog (johnjwang.com)` / `company engineering blog (Assembled)` / `Medium essay, 2021`), and use the personal register at inference | two hours | turns register contamination into a conditioning signal instead of an average |
| 3 | Up-weight the personal voice: write the extra prompt forms for the six personal-site training posts first, and emit their raw completions twice | your time, mostly | shifts the effective mix toward the voice you want |
| 4 | Reviewed, deterministic normalizer for external targets: curly to straight quotes, `_x_` to `*x*`, top section level to `#`; carry approvals forward when only normalization changed | half a day | one consistent surface convention |
| 5 | Chunker: never end a chunk on a colon when a list follows; merge the list in | an hour | fixes two bad targets |
| 6 | Text exclusions for the `no-math` span and the "Graph from From" caption | ten minutes | removes an HTML artifact and a typo from approved targets |
| 7 | Code policy: pass code blocks through the brief verbatim ("include this block as-is") so targets copy code rather than compose it; exclude `external-tests-with-llms--004` | an hour plus review | stops training code composition as prose |
| 8 | Prospective test set: five personal-site drafts only | ongoing | measures the voice you actually want |
| 9 | Decide on the Assembled posts: confirm whether an editor reshaped them; if so, keep them for raw completions only | your call | removes the largest register contamination if confirmed |

Items 1, 2, 4, 5, and 6 change target text or hashes and will invalidate the affected approvals,
which is the intended behavior. Item 4 can carry approvals forward automatically when the only
difference is the normalization itself.

## Questions only you can answer

- Were the seven Assembled posts edited by someone else before publication? The "we" rate and
  em-dash rate say yes; only you know.
- Is the target voice the 2026 personal site, or a blend that includes the company blog? The
  register line in item 2 lets the adapter do both, but the data weighting and the prospective
  test set should follow whichever you mean.
- Do you type straight or curly quotes? Your published personal posts are straight; the 143
  draft is curly, which suggests the draft was typed in Docs or Notion. The normalizer should
  match what you want the model to emit.
