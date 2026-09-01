# Semantic chunk candidates

Run `goodprose build-chunks` to deterministically split imported posts at Markdown headings and
paragraph boundaries. Chunk targets are exact contiguous spans of `data/posts/posts.jsonl`.

`candidates.jsonl` is the complete chunk inventory, not itself an SFT dataset. All chunks inherit
the frozen split of their post lineage. The 68 chunks referenced by the approved training prompts
have status `approved`. The 19 development and 20 test chunks deliberately remain `candidate`;
they are useful for inspection but must never be used to derive training inputs. Canonical SFT
pairs are promoted through the guarded pair builder rather than read directly from this file.
