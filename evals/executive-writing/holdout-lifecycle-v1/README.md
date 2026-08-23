# Protocol: aggregate-only holdout lifecycle v1 (`holdout-lifecycle-v1`)

Status: frozen public protocol. Everything in this directory is explicitly
synthetic. **No true Tier B2 or Tier C content exists in this repository**, and
nothing here is genuinely sealed; every example, fixture, and repository-local
run is a procedural demonstration only.

Implementation: `src/goodprose/executive_writing/holdout.py`, CLI subcommands
under `holdout` in `src/goodprose/executive_writing/__main__.py`, deterministic
tests in `tests/executive_writing/test_holdout.py`.

## What it covers

1. **Tier B2 shadow development** — queried only at a preregistered cadence,
   reported only through aggregate candidate results via an external
   append-only receipt chain (`b2-receipt-NNNN.json`). The broker proves, per
   query: the candidate/configuration is new, the configuration is frozen, the
   B1 promotion claim contains the exact registered evidence fields and a
   hash-pinned evidence artifact, the accepted-candidate ordinal satisfies the
   cadence gap, the prior receipt chain verifies, and the maximum query count
   is not exceeded. A single aggregate regression count is tracked across
   receipts; once the registered threshold is reached the outcome is
   `advancement_blocked` and later queries fail before hidden scores are used,
   with no item-, case-, output-, rationale-, rubric-, or slice-level detail.
2. **Tier C burn-before-read one-shot lifecycle** — a finalist freeze (three to
   five unique configurations plus the frozen automated selection procedure and
   passing contamination attestation) is committed before an exclusive
   `opened` state is created; if evaluation crashes after that point the
   benchmark remains consumed and any second run fails. On success exactly one
   aggregate-only receipt and a separate exclusive `completed` state are
   created. Completion preflights the registration, freeze, and state before
   loading score files. The frozen selection rule considers only hard-gate-
   passing finalists and reports no selection if none pass. Retirement
   preserves the receipt chain while making the benchmark ineligible for
   future selection.

## Public/private process boundary

Pure validation/aggregation functions are separated from file/process
wrappers so deterministic tests prove the logic without reading true private
content. The worker that reads hidden records and all durable lifecycle state
(`submit_b2_query`, `open_tier_c`, `complete_tier_c`, `retire`) must run in
the access-controlled evaluator environment — never in a candidate-development
checkout. The repository-side verifier accepts only registration/freeze
metadata and a receipt (`holdout validate-registration`, `validate-freeze`,
`verify-receipt`, `verify-chain`). No command copies or prints hidden records.

Hidden evaluator input records are strict: opaque case IDs, registered
candidate IDs, exact registered numeric metrics and gates, audit metadata only.
Free-text payloads and leaking keys (input, source, prompt, output, rationale,
rubric, expected, answer, reference, slice, example, document, topic, person,
publication) are rejected.

## Access posture

Access posture is exactly `sealed` or `procedurally_held_out`. A local or
agent-readable boundary must always be `procedurally_held_out`. `sealed`
requires a positive external access-separation attestation naming the
independently controlled evaluator and affirming that training, retrieval,
the model under development, teacher/synthetic generators, candidate
developers, and orchestration agents cannot read the content or rubrics.
Validation enforces the attestation's structure only; it never proves the
claim.

## Receipts

Receipt hashes cover a documented canonical payload: canonical UTF-8 JSON with
sorted keys over the full receipt document minus the `receipt_sha256` and
`authenticator` fields. An HMAC-SHA256 authenticator may be supplied by the
external evaluator's key file; the key never appears in a receipt, log,
fixture, or the repository. The key must contain at least 32 bytes and is
mandatory for a `sealed` execution. Verification without a key validates
schema and hash integrity but reports authentication as `unverified_no_key`;
verification with a key fails closed on a missing or bad authenticator.
Repository-side receipt verification is also bound to the registration and,
for Tier C, the finalist freeze. All lifecycle and receipt writes use
exclusive creation and fail rather than overwrite; confidential request/score
files are hash-verified immediately before use; timestamps are timezone-aware
ISO 8601 UTC; non-finite metrics are rejected.

## CLI

```
python -m goodprose.executive_writing holdout validate-registration --registration R [--expect-sha256 H]
python -m goodprose.executive_writing holdout validate-freeze --freeze F --registration R \
    [--expect-registration-sha256 H] [--expect-freeze-sha256 G]
python -m goodprose.executive_writing holdout verify-receipt --receipt T --registration R \
    [--freeze F] [--key-file K]
python -m goodprose.executive_writing holdout verify-chain --state-dir D --registration R \
    [--key-file K]
python -m goodprose.executive_writing holdout b2-query --registration R --request Q --state-dir D \
    --expect-request-sha256 QH --executed-at T --code-revision X \
    [--signing-key-file K] [--expect-registration-sha256 H]
python -m goodprose.executive_writing holdout tier-c-open --registration R --freeze F --state-dir D --opened-at T \
    [--expect-registration-sha256 H] [--expect-freeze-sha256 G]
python -m goodprose.executive_writing holdout tier-c-complete --registration R --freeze F --state-dir D \
    --scores CANDIDATE_ID=SHA256=PATH ... --completed-at T --code-revision X \
    [--signing-key-file K]
python -m goodprose.executive_writing holdout retire --registration R --state-dir D \
    --authorized-by A --reason REASON --retired-at T
```

Registration/freeze `--expect-*-sha256` values are canonical document hashes
(SHA-256 over canonical sorted-key JSON of the parsed model). Confidential B2
request and Tier C score hashes cover the exact file bytes.

## Files

- `schemas/` — JSON schemas generated from the strict frozen Pydantic models.
- `examples/synthetic-*` — explicitly synthetic example registration, freeze,
  query request, and hidden-score documents used by tests and documentation.

## Frozen output contract

The public B2 result is exploratory aggregate-only shadow-development
evidence. It may detect search overfit but cannot reveal which item or slice
drove the change. The public Tier C result is confirmatory only when the
registration is genuinely access-separated and labeled `sealed`; otherwise it
is explicitly procedural evidence and cannot satisfy the goal's sealed-evidence
stopping condition.

The cryptographic receipt proves canonical payload integrity and, when a key
held by the named external authority verifies, authenticates that authority's
emission. It does not by itself prove the truth of an access-separation
attestation.
