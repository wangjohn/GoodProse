# Model card: compact-ledger local research leader v2

## Identity and status

- Candidate: `qwen2.5-0.5b-retrieval-ledger-draft-v2`.
- Status: visible-development directional leader; not finalist-ready and not
  production-qualified.
- Base: `qwen2.5:0.5b-instruct`, Qwen2.5 0.5B Instruct, Apache-2.0.
- Runtime: local Ollama 0.9.6 on loopback.
- Exact manifest: `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`.
- Exact primary blob: `c5396e06af294bd101b30dce59131a76d2b773e76950acc870eda801d3ab0515`.
- Quantization: Q4_K_M; 494,032,768 parameters; 397,821,319 installed bytes.
- Training: none by GoodProse. This is a prompt/retrieval/structured-inference
  system over the untuned base.

## Architecture

The system selects one project-owned, retrieval-approved example by task family
and format. It makes two temperature-zero calls:

1. extract a compact 192-token atomic ledger of facts, qualifiers, preserved
   spans, and delivery constraints;
2. draft up to 512 tokens from the full authoritative source, using the ledger
   only as a fallible checklist and the approved example only for structure and
   abstract writing characteristics.

The production-facing profile is `executive-house-v1`. The system prohibits
named-person imitation, unsupported facts, silent certainty changes, and output
other than the requested artifact. Intermediate hashes, timings, and token
counts are retained in ignored run artifacts.

## Intended use

Permitted current uses are local research, failure analysis, and manually
reviewed demonstrations on source material the operator is authorized to
process. The application interface enforces the exact local model pins and
marks every output as requiring manual factual review.

Do not use it for autonomous production communication, legal or financial
decisions, high-stakes factual publication, private material sent to an
external provider, identity imitation, or claims of endorsement.

## Evaluation

On 24 visible project-authored GoodProse B1 v1 cases rescored with deterministic
v1.1:

| Metric | Result |
| --- | ---: |
| Mean development score | 87.1981 |
| Median development score | 91.2353 |
| Hard-gate pass rate | 12/24 (50.00%) |
| Fidelity dimension mean | 82.3165 |
| Clarity/coherence mean | 98.2007 |
| Concision mean | 83.3145 |
| Organization/actionability mean | 75.0000 |
| Audience/format mean | 100.0000 |
| Mean latency | 2,850.46 ms |
| Prompt/output tokens | 22,812 / 6,362 |
| Settled cost | $0 |

Against the matched single-pass retrieval baseline, the paired mean difference
was +2.3698 points, median +0.5852, with 13/4/7 wins/ties/losses and a 10,000-
resample 95% interval of -2.0211 to +6.7390. It cleared the preregistered
visible-development iteration gate.

It did not clear production requirements. Twelve cases had deterministic
omissions and five had poor actionability. B1 is visible, small, synthetic,
project-authored, and was used during search. The lexical scorer cannot detect
every unsupported semantic expansion or establish publish-ready prose.

Subsequent alternatives did not displace it as an accepted local leader:
four-stage verification regressed; both LoRA candidates failed quality or
memorization controls; Ox Alpha candidates failed artifact/grounding gates;
the 7B matched probe passed only 7/24 gates and had 15 material source-expansion
findings. These are negative comparisons, not confirmation that this candidate
is production ready.

## Data, rights, and privacy

Retrieval examples are project-authored and explicitly
`retrieval_approved_project_owned`. B1 cases are project-owned evaluation data
and are never retrieval examples. No named-source body, private corpus, hidden
case, grader rubric, or reference answer enters the prompt.

Application requests remain on the loopback Ollama service. Result manifests
omit the raw source and intermediate ledger, but the generated artifact can
still reveal source information and must be stored as sensitive material.

## Limitations and risks

- A 50% hard-gate rate is unacceptable for autonomous use.
- The model can omit caveats, actions, names, numbers, or dependencies.
- A model-generated ledger can itself corrupt or omit source facts.
- Deterministic temperature-zero decoding improves repeatability, not truth.
- Approved-example retrieval can bias structure and may not cover a requested
  genre well.
- Visible B1 improvement is exploratory and vulnerable to selection effects.
- No sealed Tier C result or intended-audience human rating exists.
- No latency, memory, privacy, or reliability evidence exists for a hosted
  multi-user deployment.

## Reproduction and review

The frozen config is under `configs/baselines/`; the analysis and case-level
records are `goodprose-compact-ledger-draft-v2-*` under `experiments/`. Use the
commands in `REPRODUCTION.md` and the manual checklist in `APPLICATION.md`.
Reject any output that cannot be verified line by line against the source.
