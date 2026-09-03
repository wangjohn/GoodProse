# External blog posts

`posts.jsonl` catalogs thirteen owner-authored posts published outside `johnjwang.com`: seven on
Assembled and six on Medium. All thirteen published targets have been approved, normalized from
saved public-page Markdown, added to `data/posts/posts.jsonl`, and assigned a frozen lineage split.

The split is deliberately based on input provenance:

- Training: nine posts, producing 50 exact semantic completions with synthetic prompt candidates.
- Development: two posts with authentic pre-publication inputs (`AI coding interviews` and `LLM
  provider fallbacks`).
- Test: two posts with authentic pre-publication inputs (`Database abstractions for Golang` and
  `New Products Team`).

The saved public pages and authentic inputs remain ignored under `data/private/external/`. Rebuild
the canonical post file from the public snapshots with:

```bash
uv run goodprose build-external-posts \
  --catalog data/external/posts.jsonl \
  --snapshot-root data/private/external/published-raw \
  --base-posts data/private/posts/johnjwang-posts.jsonl \
  --output data/posts/posts.jsonl
```

Five records also have author-controlled Markdown in the ignored private source checkout. Build a
local source sample file with:

```bash
uv run goodprose build-external-samples \
  --catalog data/external/posts.jsonl \
  --source-map data/private/external/source-map.jsonl \
  --source-root data/private/external/blogposts-source \
  --output data/private/external/samples.jsonl
```

`build-external-posts` removes known Assembled/Medium page chrome and image-only lines without
rewriting article prose. The page snapshots flattened fenced code into prose lines (and the
Assembled ones dropped whitespace inside the code), so `--repair-code` with `--source-map` and
`--source-root` splices the author manuscript's fenced blocks over any run of snapshot lines
whose whitespace-stripped tokens match exactly, reporting blocks it could not place.
`--fence-heuristic go` then fences any remaining run of code-looking lines (blank lines between
them removed) as a fallback for blocks the manuscript did not match exactly; it cannot restore
whitespace the snapshot dropped, so exact repair runs first. `--target-from-manuscript POST_ID`
uses the manuscript body itself as the canonical target for posts where the published text
carries an editor's pass. A source-map record may set `target_end_marker` to exclude material such
as archived drafts or outlines that follows the finished post; the marker must occur exactly once.
Catalog approval, snapshot presence, duplicate IDs, and base/external ID collisions are checked
before output. The published snapshot is the exact completion source; the private manuscript is
used only as an authentic input where a frozen held-out mapping selects it.
