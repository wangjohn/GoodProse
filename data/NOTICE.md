# Third-party data notice

Files under `data/raw/` are copied from the upstream repositories listed in [`sources.json`](sources.json). They are not covered by GoodProse's root MIT license merely because they are stored in this repository.

The default seed corpus currently includes:

| Source | Upstream license | Default role |
| --- | --- | --- |
| Go proposals | BSD-3-Clause | training reference + public dev holdout |
| React RFCs | MIT | training reference |
| Rust RFCs | MIT OR Apache-2.0 | training reference + public dev holdout |
| Python Enhancement Proposals | document-level public domain or CC0-1.0 | training reference |
| Swift Evolution proposals | Apache-2.0 | training reference |
| Kubernetes Enhancement Proposals | Apache-2.0 | training reference |
| Bytecode Alliance RFCs | Apache-2.0 | source-family test holdout |

The upstream license or licensing-policy file is fetched into each corresponding `data/raw/<source-id>/` directory. Each selected Python PEP also contains its own public-domain or CC0-1.0 notice. Preserve those files, document notices, and attribution when redistributing the corpus.

Teleport RFDs are recorded as candidates under an AGPL-3.0-only repository license. They are not fetched by default. This is an engineering safeguard, not a legal conclusion; decide explicitly how the license applies to redistribution, derivative examples, and model training before enabling that source.
