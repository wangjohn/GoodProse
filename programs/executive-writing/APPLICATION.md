# Local application interface

GoodProse exposes the provisional research leader through a source-bound,
local-only command. It is a research preview, not a production-qualified
system. Every artifact requires manual comparison with the source before use.

## Prerequisites

- Work from the repository root with the committed `uv` environment.
- Run Ollama `0.9.6` on loopback at `http://127.0.0.1:11434`.
- Install the exact `qwen2.5:0.5b-instruct` model pinned by manifest and blob
  hashes in the selected baseline config.
- Keep requests and results out of git when they contain private material. The
  ignored `programs/executive-writing/artifacts/application/` directory is the
  recommended location.

The command refuses a non-loopback provider, model/version/hash drift, an
unrecognized profile, malformed input, or an existing output file. The result
does not repeat the raw source or intermediate ledger, but it does contain the
generated artifact and may therefore still be sensitive.

## Run the synthetic example

```bash
uv run python -m goodprose.executive_writing apply \
  --request programs/executive-writing/configs/application/example-request-v1.json \
  --output programs/executive-writing/artifacts/application/example-result-v1.json
```

Copy the example request to the ignored artifact directory before replacing
its source with private material. Do not edit the committed example with real
content.

The JSON result records the source and artifact hashes, exact model identity,
config and approved-retrieval hashes, pipeline step hashes, latency, token
counts, settled cost, code revision, and whether the working tree was dirty.
`production_qualified` is always `false` and
`manual_factual_review_required` is always `true` for this provisional system.

## Supported input

The request schema accepts the task families and output formats defined by the
versioned GoodProse benchmark. It currently binds the descriptive
`executive-house-v1` profile and frozen
`qwen2.5-0.5b-retrieval-ledger-draft-v2` two-stage pipeline. Source text is
limited to 20,000 characters, individual request fields to 1,000 characters,
and constraints to 20 items. Unknown fields are rejected.

The `topic` field affects deterministic selection among project-owned,
retrieval-approved examples. It does not retrieve external content.

## Review checklist

Before sending or publishing an artifact, verify every:

- fact, number, unit, name, date, attribution, and decision;
- negation, uncertainty, dependency, caveat, scope limit, and placeholder;
- requested action, owner, deadline, audience, format, and length constraint.

Reject the artifact if it expands beyond the source, loses a material item, or
changes the source's intent. The current automated evidence shows only a
50.00% hard-gate pass rate on the 24-case B1 development benchmark, so manual
review is mandatory.
