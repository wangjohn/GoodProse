# Derived data

Generated supervised examples go here and are ignored by Git by default. Use the canonical schema in [`../schemas/training-example.schema.json`](../schemas/training-example.schema.json), retain lineage/provenance metadata, and publish only records that have passed privacy, license, and human-quality review.

Recommended local layout:

```text
staging/          annotation seeds, redacted candidates, and reviewed exports
privacy-reports/ reports bound to the exact SHA-256 of the JSONL they scanned
argilla-backups/ immutable exports from each versioned human workflow
snapshots/        content-addressed, training-ready dataset releases
```

Do not edit a snapshot in place. `goodprose dataset snapshot` sorts records canonically, validates provenance and split isolation, checks the corresponding clean privacy report, produces a token report, and writes the result under the first 12 characters of its dataset SHA-256. Re-running the same input is idempotent; conflicting files are rejected.
