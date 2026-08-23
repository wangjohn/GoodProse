# Ox assignment: aggregate-only holdout lifecycle v1

Status: frozen before delegation. No true Tier B2 or Tier C content exists in
the agent-readable repository, and this assignment must not create or inspect
any true hidden evaluation content.

## Objective

Implement and test the public protocol and local tooling for two related but
distinct evaluation boundaries:

1. Tier B2 shadow-development, queried only at a preregistered cadence and
   reported only through aggregate candidate results.
2. Tier C, opened exactly once per benchmark version after the complete
   finalist set and every behavior-affecting configuration are frozen.

The implementation must preserve the repository rule that per-example results
are retained for audit while reconciling it with the research contract: hidden
records are retained only inside the separately controlled evaluator boundary,
never returned to or written by the orchestration process. The committed side
receives aggregate metrics, hashes, timestamps, lifecycle state, and an
immutable receipt only.

Do not run either tier on real content. Use obviously synthetic, project-
authored fixtures for tests and protocol demonstrations. Do not claim that a
fixture or a repository-local run is genuinely sealed.

## Required implementation

Create a focused module at
`src/goodprose/executive_writing/holdout.py`, mocked/deterministic tests at
`tests/executive_writing/test_holdout.py`, and `holdout` CLI commands in
`src/goodprose/executive_writing/__main__.py`. Add a public protocol package at
`evals/executive-writing/holdout-lifecycle-v1/` with concise documentation,
machine-readable example registrations/freezes, JSON schemas generated from
or exactly matching the Pydantic models, and explicitly synthetic fixtures.
Update only the root executive-writing eval README if needed to route users to
the protocol. Do not update program reports, results, registry, costs, or
progress; Codex will do that after review.

Use strict frozen Pydantic v2 models (`extra="forbid"`) at every serialized
boundary and canonical UTF-8 JSON with sorted keys for all hashes. Reuse the
repository's atomic JSON and SHA-256 helpers when appropriate. Keep the module
small and concrete rather than building a general workflow framework.

### Shared registration and evidence rules

1. A registration contains a unique tier/version identifier; creation time;
   case count; opaque content commitment; canary commitment; split-grouping
   dimensions (`document`, `thread`, `source`, `person`, `publication`,
   `topic`, and `time_period`); exact preregistered aggregate metrics and hard
   gates; scorer/judge, contamination-scan, protocol, and code hashes; access
   posture; retention location identifier; and responsible external authority.
   It contains no path, source text, expected answer, rubric, case identifier,
   slice value, or other item-level material.
2. Access posture is exactly `sealed` or `procedurally_held_out`. A local or
   agent-readable boundary must always be `procedurally_held_out`. A `sealed`
   registration requires a positive external access-separation attestation
   naming the independently controlled evaluator and affirming that training,
   retrieval, Ox Alpha, teacher/synthetic generators, candidate developers,
   and orchestration agents cannot read the content or rubrics. Validation can
   enforce the attestation's structure but must not pretend to prove the claim.
3. Hidden evaluator input records are strict and may contain only opaque case
   IDs, registered candidate IDs, registered numeric metrics, registered hard
   gates, and audit metadata needed inside the boundary. They must reject free
   text and suspicious/leaking keys such as input, source, prompt, output,
   rationale, rubric, expected, answer, reference, slice, example, document,
   topic, person, or publication. Hidden records are never embedded in a
   public receipt.
4. Every evaluation identity field required by `evals/AGENTS.md` and the goal
   contract must be frozen or committed by hash: candidate/model and exact
   version; base model and adapter/checkpoint; prompt; inference/decoding;
   retrieval corpus and configuration; dataset/split; grader and version;
   seed; code revision; hardware/provider; and cost/token-accounting policy.
5. A receipt contains only the exact preregistered aggregate candidate
   metrics/gates, allowed aggregate counts, content/config/freeze/registration
   hashes, execution timestamp, protocol/code identity, aggregate usage/cost,
   access posture, lifecycle outcome, a prior-receipt hash where applicable,
   and cryptographic receipt fields. No dynamic field name or nested payload
   may provide an item-, case-, output-, rationale-, rubric-, or slice-level
   side channel.
6. Build receipt hashes from a documented canonical payload. Support an
   HMAC-SHA256 authenticator supplied by a key file controlled by the external
   evaluator; never put the key or its bytes in a receipt, log, fixture, or
   repository. Verification without a key must validate schema and hash-chain
   integrity but explicitly report authentication as unverified. Verification
   with a key must fail closed on a bad authenticator. Synthetic tests may use
   an in-memory test key that is unmistakably non-production.
7. All lifecycle and receipt writes use exclusive creation and fail rather
   than overwrite. Input artifacts are hash-verified immediately before use.
   Timestamps are timezone-aware ISO 8601 UTC. Non-finite numeric metrics are
   rejected.

### Tier B2 aggregate-only broker

8. The B2 registration freezes a concrete cadence/promotion policy from B1,
   including the eligible B1 evidence fields, minimum improvement or milestone
   condition, maximum query count, minimum accepted-candidate gap between
   queries, reference candidate/configuration, regression margin, and the
   number of aggregate regressions that blocks advancement. No B2 item/slice
   can influence the cadence.
9. The broker keeps an external append-only state/receipt chain. Before
   accepting hidden scores, it proves the candidate is new, its complete
   configuration is frozen, the B1 promotion claim satisfies the registered
   policy, the gap/cadence is met, and the maximum query count is not exceeded.
   Duplicate candidate/configuration queries and receipt-chain forks fail.
10. Aggregate each registered metric deterministically per candidate, report
    registered hard-gate pass rates/counts, and compare only the candidate's
    registered primary aggregate with the frozen reference aggregate. Track a
    single aggregate regression count across eligible receipts. Once the
    preregistered repeated-regression threshold is reached, return
    `advancement_blocked`; never return cases, outputs, explanations, slices,
    or per-error examples to explain the regression.

### Tier C burn-before-read one-shot lifecycle

11. A finalist-freeze artifact contains three to five unique finalist
    candidate configurations plus the frozen automated selection procedure.
    Every behavior-affecting field listed above must be present or committed by
    hash. The freeze must be created before the one-shot state and receipt and
    may not be changed in place.
12. Before opening or accepting any hidden Tier C score record, atomically and
    exclusively create a durable `opened` state that commits to the
    registration and finalist-freeze hashes. If evaluation crashes after that
    point, the benchmark remains consumed and a second run must fail. On
    success create a separate exclusive `completed` state and aggregate-only
    receipt; never erase or replace `opened`.
13. Reject Tier C execution unless the freeze contains three to five
    finalists, all registered metrics/gates are present exactly, case and
    candidate coverage is complete with no duplicate pair, the contamination
    attestation reports passing exact-match, n-gram, embedding, and canary
    scans with pinned hashes, and all candidates share the frozen selection
    procedure. The receipt must make `procedurally_held_out` limitations
    prominent and must never equate that posture with sealed evidence.
14. Provide an explicit retirement record/state transition for authorized
    item-level inspection. Retirement preserves aggregate receipts and their
    hash chain, makes the benchmark ineligible for future selection, and does
    not copy hidden content or rubrics into the repository.

### Public/private process boundary

15. Separate pure validation/aggregation functions from file/process wrappers
    so deterministic tests can prove the logic without reading true private
    content. Clearly document that the worker which reads hidden records and
    its durable lifecycle state must run in the access-controlled environment,
    not in the candidate-development checkout. The repository-side verifier
    accepts only registration/freeze metadata and a receipt.
16. CLI commands must cover at least registration/freeze validation, receipt
    verification, the B2 external broker path, the Tier C external one-shot
    path, and retirement. Names and arguments should make the boundary obvious.
    Never offer a convenience command that copies or prints hidden records.
17. The synthetic protocol example must demonstrate one permitted B2 query,
    a blocked duplicate or cadence violation, one successful procedural Tier C
    run, a rejected second Tier C run, bad-hash/tamper rejection, bad-HMAC
    rejection, and retirement. Synthetic receipts may be stored only in test
    temporary directories unless a small clearly labeled example receipt is
    useful for the documentation.

## Frozen output contract

The public B2 result is exploratory aggregate-only shadow-development evidence.
It may detect search overfit but cannot reveal which item or slice drove the
change. The public Tier C result is confirmatory only when the registration is
genuinely access-separated and labeled `sealed`; otherwise it is explicitly
procedural evidence and cannot satisfy the goal's sealed-evidence stopping
condition.

The cryptographic receipt proves canonical payload integrity and, when a key
held by the named external authority verifies, authenticates that authority's
emission. It does not by itself prove the truth of an access-separation
attestation. State these limitations directly.

## Allowed files and checks

Limit edits to:

- `src/goodprose/executive_writing/holdout.py`
- `src/goodprose/executive_writing/__main__.py`
- `tests/executive_writing/test_holdout.py`
- new files under `evals/executive-writing/holdout-lifecycle-v1/`
- `evals/executive-writing/README.md` only if routing documentation is useful

Do not add dependencies, inspect ignored private/result directories, access
the network, call a model, run a true holdout, modify other files, commit, or
push. Run the focused tests and Ruff/Pyright on touched Python files. End with
a concise file/change/test summary and any concerns Codex should review.
