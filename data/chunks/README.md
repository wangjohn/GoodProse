# Semantic chunk candidates

Run `goodprose build-chunks` to deterministically split imported posts at Markdown headings and
paragraph boundaries. `exclusions.jsonl` removes seven reviewed promotional or mixed-footer
chunks. `supplemental-targets.jsonl` adds reviewed sentence spans and clean endings when a default
section also contains promotional footer material. Every target remains an exact contiguous span
of `data/posts/posts.jsonl`; exclusions and supplemental targets are restricted to train lineages.

`candidates.jsonl` is the complete chunk inventory, not itself an SFT dataset. All chunks inherit
the frozen split of their post lineage. The 75 chunks referenced by the approved training prompts
have status `approved`. The 19 development and 20 test chunks deliberately remain `candidate`;
they are useful for inspection but must never be used to derive training inputs. Canonical SFT
pairs are promoted through the guarded pair builder rather than read directly from this file.
