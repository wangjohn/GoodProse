# Qwen2.5 7B compact-ledger h11 preregistration v1

Status: frozen before B1 generation. No B1 generation is permitted until the
runner, candidate config, and this record are committed together.

## Question and causal change

Can model scale close the remaining quality/fidelity gap when the strongest
local compact-ledger architecture is held fixed? The only intended candidate
change is `qwen2.5:0.5b-instruct` to the same-family
`qwen2.5:7b-instruct` Q4_K_M artifact. Retrieval examples, ledger and draft
prompts, token caps, decoding, seed, context, source boundary, B1 order,
scorer, and comparison baseline remain unchanged.

This is the one h11 larger-local-model probe. It is not a model sweep. No
result may cause a different size, quantization, prompt, or candidate to be run
under this hypothesis.

## Frozen model and resource boundary

- Local runtime: Ollama 0.9.6 on Apple M3 Pro with 18 GiB unified memory
- Model tag: `qwen2.5:7b-instruct`
- Manifest SHA-256: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- Primary GGUF blob SHA-256:
  `2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730`
- Identity: 7,615,616,512 parameters, Q4_K_M, 32,768 native context,
  Apache-2.0; 4,683,087,332 installed bytes
- Resource record: `qwen2.5-7b-local-feasibility-v1.json`

The acquisition and one non-B1 resource smoke passed before freeze. At exact
pin validation, 37,681,135,616 bytes (35.09 GiB) of disk remained; Ollama
reported a 6.0 GB fully GPU-loaded model; free memory was 24%; throttled pages
remained zero; and the cold request completed in 14.038 seconds. Execution is
allowed only while the exact manifest/blob and loopback endpoint validate.
Abort before generation on identity drift or less than 30 GiB available disk.

## Frozen candidate

- Candidate: `qwen2.5-7b-retrieval-ledger-draft-h11-v1`
- Config: `qwen2.5-7b-retrieval-ledger-draft-h11-v1.json`
- Config SHA-256: `44b5934ba1df5e89e4329448456a2f95087f39ee96389aa660f3a0cd55d0f1c2`
- Baseline: `qwen2.5-0.5b-retrieval-ledger-draft-v2`, directly pinned
  deterministic-v1.1 24-case artifacts
- Cases: all 24 visible project-authored B1 examples in benchmark order
- Pipeline: exactly one compact ledger and one draft per case; 48 local calls
- Prompt: unchanged `retrieval-ledger-draft-v2`; the source remains
  authoritative and evaluator fields are absent
- Retrieval: unchanged project-owned `retrieval-examples-v1.json`
- Decoding: temperature 0, seed 20260822, context 4096; ledger cap 192 tokens,
  draft cap 512 tokens
- Cost: local only, settled $0; no external provider receives data

## Frozen decision gates

The candidate enters the common automated frontier only if every condition
passes:

1. paired mean improvement over compact ledger is at least two points;
2. hard-gate pass rate does not regress;
3. all 24 deterministic hard gates pass;
4. no deterministic fabrication or placeholder-loss case occurs;
5. mean end-to-end latency is at most 60 seconds and total final-output tokens
   are at most 16,800;
6. every final response is artifact-only, with no model, prompt, instruction,
   task-status, or process commentary;
7. permitted full-output review finds no material unsupported fact, decision,
   attribution, owner, approval, commitment, deadline, guarantee, restriction,
   workflow, rationale, or follow-up channel;
8. privacy, rights, leakage, model-pin, provenance, resource, and zero-cost
   checks all pass.

Report the 10,000-resample paired interval, paired mean and median effects,
wins/ties/losses, dimensions, deterministic failures, stage tokens/latency,
resource evidence, and compact hash-bound audit findings. A usable output is
final; no quality retry, repair, filtering, or resampling is allowed.

## Stopping implication

If h11 fails, every currently identified safe, affordable, high-value
automated architecture hypothesis is exhausted. Do not call that a successful
plateau unless the contract's hard-gate definition is satisfied. Instead,
refresh the frontier, audit remaining external blockers, and continue only
evidence-bearing work that does not fabricate finalists, hidden data, rights
approval, Tier C results, or human judgments.
