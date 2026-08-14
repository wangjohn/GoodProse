# RFClear

RFClear turns coding-agent output into clear, decision-ready technical specifications.

This repository currently contains the foundation for a provenance-aware dataset and an honest evaluation suite. The seed corpus includes selected Go, React, and Rust documents as training references; public development holdouts; and a Bytecode Alliance source-family holdout. Teleport RFD candidates are recorded but gated on a separate license review.

## Quick start

```bash
make corpus
make validate
```

The fetcher downloads exact upstream revisions and verifies every file against the SHA-256 recorded in [`data/sources.json`](data/sources.json). It does not fetch manual-review sources unless explicitly requested.

## Repository map

```text
data/
  raw/                    exact, pinned upstream documents and licenses
  derived/                generated supervised examples (not committed by default)
  schemas/                canonical, provider-neutral record formats
  sources.json            provenance, checksums, splits, and selection rationale
evals/
  cases/                  runnable agent-output-to-spec cases
  private/                non-public final holdout (not committed)
  results/                generated evaluation runs (not committed)
  targets.json            public held-out reference targets
  RUBRIC.md                scoring dimensions and failure gates
scripts/
  fetch_corpus.py          reproducible downloader
  validate_corpus.py       checksum and split-leakage checks
docs/
  DATASET_STRATEGY.md      collection, pairing, splitting, and evaluation plan
```

The upstream specifications are reference material, not supervised examples by themselves. A useful training record must pair a messy but truthful coding-agent output with a human-approved specification. See [`docs/DATASET_STRATEGY.md`](docs/DATASET_STRATEGY.md) for the recommended path from this corpus to a fine-tuning dataset.

## Licensing

RFClear's own code is MIT-licensed. Files under `data/raw/` retain their upstream licenses; the root MIT license does not relicense them. Review [`data/NOTICE.md`](data/NOTICE.md) and the copied license in each source directory before redistributing a derived dataset or trained model.
