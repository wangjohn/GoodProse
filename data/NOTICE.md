# Third-party data notice

Files under `data/raw/` are copied from the upstream repositories listed in [`sources.json`](sources.json). They are not covered by RFClear's root MIT license merely because they are stored in this repository.

The default seed corpus currently includes:

| Source | Upstream license | Default role |
| --- | --- | --- |
| Go proposals | BSD-3-Clause | training reference + public dev holdout |
| React RFCs | MIT | training reference + public dev holdout |
| Rust RFCs | MIT OR Apache-2.0 | training reference + public dev holdout |
| Bytecode Alliance RFCs | Apache-2.0 | source-family test holdout |

The complete upstream license text is fetched into each corresponding `data/raw/<source-id>/` directory. Preserve those files and attribution when redistributing the corpus.

Teleport RFDs are recorded as candidates under an AGPL-3.0-only repository license. They are not fetched by default. This is an engineering safeguard, not a legal conclusion; decide explicitly how the license applies to redistribution, derivative examples, and model training before enabling that source.
