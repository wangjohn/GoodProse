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
rewriting article prose. Catalog approval, snapshot presence, duplicate IDs, and base/external ID
collisions are checked before output. The published snapshot is the exact completion source; the
private manuscript is used only as an authentic input where a frozen held-out mapping selects it.
