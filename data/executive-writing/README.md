# Executive-writing data boundary

This directory contains public metadata, source manifests, profile
specifications, collection plans, and dataset indexes for the executive-writing
program. It must not contain private corpus bodies, unsanitized email, raw
litigation exhibits, credentials, or model-generated material presented as an
original author's writing.

Training records belong in ignored `data/derived/` snapshots. Local private
material and caches belong in the ignored `private/` and `cache/` directories.
All records must follow `data/AGENTS.md` and preserve rights and provenance.

Subdirectories:

- `smoke-v1/`: compact manifest for the pipeline smoke fine-tune dataset.
- `unified-pilot-v1/`: documentation and frozen record schema for the
  project-authored unified three-corpus architecture pilot; its manifest is
  generated later from an independently reviewed local source file.
