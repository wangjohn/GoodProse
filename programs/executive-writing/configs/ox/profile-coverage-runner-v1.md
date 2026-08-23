# Ox assignment: source-profile coverage runner v1

Status: frozen before delegation and before any source-profile generation.

## Objective

Implement a deterministic, source-text-free coverage runner for the eleven
descriptive executive-writing profiles already committed in
`data/executive-writing/sources/named-sources-v1.json`. Run the identical six
project-authored B1 cases for each profile and for the existing GoodProse house
profile as a paired control. This is exploratory profile-card coverage only,
not imitation, endorsement, training, standalone-adapter evidence, or a model
selection gate.

Do not execute the real 72-generation evaluation. Codex will review and commit
the implementation before any model call, then execute and interpret the run.

## Required implementation

Create a focused module at
`src/goodprose/executive_writing/profile_coverage.py`, mocked deterministic
tests at `tests/executive_writing/test_profile_coverage.py`, and CLI commands in
`src/goodprose/executive_writing/__main__.py`. Add one exact machine-readable
run config under
`programs/executive-writing/configs/source-profile-evaluation/` and one human
preregistration beside it. Do not place extra JSON in the existing
`configs/source-profiles/` directory because its layout validator requires
exactly eleven profile files.

The runner must:

1. Load and cross-validate the named-source manifest, source-profile eval
   manifest, all eleven source-profile configs, the B1 cases, the B1 benchmark
   manifest, and the existing pinned local Ollama house-profile baseline
   config. Reuse `validate_repository_layout`, `load_cases`, `OllamaClient`,
   `Generation`, and shared JSON/hash helpers where appropriate.
2. Select exactly the six frozen shared case IDs in manifest order and reject
   missing, duplicate, extra, or mismatched cases/profiles/configs.
3. Evaluate exactly twelve candidates: one house-profile control and eleven
   descriptive profile-card candidates. Use one generation call per
   candidate/case, for exactly 72 calls. Candidate IDs and ordering must be
   deterministic.
4. Build each descriptive prompt only from the profile production name,
   description, trait strings, anti-impersonation limits, the GoodProse safety
   rules, and the project-authored task/source. Never include the source
   person's name, source URLs, source IDs, third-party text, or retrieved
   examples. Explicitly state that the descriptive profile is an abstract
   register, that the model must not name or imitate a person or imply
   endorsement, and that only the supplied project-authored task source is
   authoritative. Set and record `retrieval_enabled: false`.
5. Use the exact local model, endpoint, hashes, decoding, timeout, license, and
   Ollama version pinned by
   `programs/executive-writing/configs/baselines/qwen2.5-0.5b-profile-v1.json`.
   Reject non-local endpoints and nonzero temperature through the existing
   baseline config validation. Settled provider cost is exactly zero.
6. Score every generated output with `score_output_v1_1`, never the superseded
   v1 scorer. The model prompt must receive no rubric, expected checks,
   reference answer, scorer details, or prior case result.
7. Write raw ignored run artifacts atomically under the supplied output root:
   `outputs.jsonl`, `scores.jsonl`, per-candidate `summary.json` data or one
   equivalent complete summary artifact, and `run-manifest.json`. Record exact
   prompt/output hashes, artifact hashes, input file hashes, candidate/profile
   mappings, candidate order, case order, timestamps, code revision, model and
   decoding identity, latency/tokens, scorer version, evaluation ID, rights
   posture, no-source-text policy, retrieval disabled, and zero cost.
8. Provide a separate offline publisher that verifies every raw artifact and
   generation hash before producing committed compact results and case-level
   records. It must compute descriptive per-candidate summaries and paired
   differences versus the house control. Because n=6 and this is coverage, it
   must never set an advancement winner or production gate. Include explicit
   limitations for current topic-swap and leave-time-out gaps and label all
   comparisons exploratory. Do not publish raw generated text.
9. Make reruns safe: fail if the exact raw run directory already exists rather
   than overwriting evidence. Publisher outputs may also not silently overwrite
   existing committed evidence.
10. Tests must mock `OllamaClient.generate`; prove exactly 72 calls, exact
    candidate/case ordering, no person names/source IDs/URLs in model prompts,
    no rubric leakage, scorer v1.1 use, hash verification/tamper rejection,
    cross-artifact validation, safe non-overwrite behavior, and compact
    source-text-free publication.

## Frozen analysis contract

Primary outputs are per-candidate mean development score, hard-gate pass rate,
error counts, and paired mean/median difference plus win/tie/loss versus the
house-profile control on the same six cases. Bootstrap intervals may be
reported only as exploratory. No candidate can advance, become a production
default, or satisfy the contract's model-quality stopping condition from this
six-case coverage run.

The run exists to test whether each descriptive profile is executable,
provenance-complete, and directionally distinct under identical content. All
eleven profiles remain in the program regardless of score.

## Allowed files and checks

Limit edits to:

- `src/goodprose/executive_writing/profile_coverage.py`
- `src/goodprose/executive_writing/__main__.py`
- `tests/executive_writing/test_profile_coverage.py`
- new files in
  `programs/executive-writing/configs/source-profile-evaluation/`

Run only the new mocked tests plus Ruff and Pyright on the files you touch. Do
not run a live model, change existing source/profile facts, update program
results/registry/reports, commit, or push. End with a concise file/change/test
summary and any concerns Codex should review.
