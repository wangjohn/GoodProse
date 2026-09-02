# Semantic chunk candidates

Run `goodprose build-chunks` to deterministically split imported posts at Markdown headings and
paragraph boundaries. `exclusions.jsonl` removes seven reviewed promotional or mixed-footer
chunks. `supplemental-targets.jsonl` adds reviewed sentence spans and clean endings when a default
section also contains promotional footer material. With `--full-posts`, every training post also
gets one `<post>--full` chunk: the exact prefix of the published Markdown up to the end of its
last kept default section, so promotional footers fall off the end and the target stays a single
contiguous span. Every target remains an exact contiguous span of `data/posts/posts.jsonl`;
exclusions, supplemental targets, and full-post chunks are restricted to train lineages.

`candidates.jsonl` is the complete chunk inventory, not itself an SFT dataset. All chunks inherit
the frozen split of their post lineage. Rebuilding preserves the review status of any chunk whose
id and target hash are unchanged (`--no-preserve-status` resets everything). The 75 section and
sentence chunks referenced by approved training prompts have status `approved`; the 15 full-post
chunks are `candidate` until they receive an approved prompt. The 19 development and 20 test
chunks deliberately remain `candidate`; they are useful for inspection but must never be used to
derive training inputs. Canonical SFT pairs are promoted through the guarded pair builder rather
than read directly from this file.
