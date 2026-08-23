# Common architecture frontier

## Decision

No evaluated candidate is finalist-ready. The strongest accepted local system
remains `qwen2.5-0.5b-retrieval-ledger-draft-v2`; the strongest score ceiling
is `ox-alpha-b1-profile-v2`, but its raw outputs are rejected for source-
grounding risk. The h11 7B probe improved mean score while regressing hard
gates and failing the full-output audit. Zero of fifteen common 24-case
candidates pass every hard gate without a disqualifying audit result.

All currently identified safe, affordable, high-value automated architecture
hypotheses are exhausted. The plateau rule is still not satisfied because the
leading accepted local candidate passes only 50% of hard gates. Do not call
this a successful plateau, invent a finalist, or proceed to B2, Tier C, or
human evaluation.

## Comparable B1 evidence

All rows use the 24 visible GoodProse B1 cases and deterministic scorer v1.1.
Scores are development evidence, not sealed or human quality.

| Candidate | Architecture | Mean | Hard gates | Mean latency | Disposition |
| --- | --- | ---: | ---: | ---: | --- |
| `qwen2.5-0.5b-minimal-v1` | Minimal prompt | 67.5522 | 25.00% | 1.294 s | Latency exploration |
| `qwen2.5-0.5b-profile-v1` | Profile single pass | 84.2839 | 20.83% | 2.114 s | Baseline |
| `qwen2.5-0.5b-retrieval-v1` | Retrieval single pass | 84.8283 | 37.50% | 1.703 s | Competitive baseline |
| `qwen2.5-0.5b-retrieval-ledger-verify-v1` | Full local verify/revise | 81.3694 | 33.33% | 7.240 s | Rejected |
| `qwen2.5-0.5b-retrieval-ledger-draft-v2` | Compact ledger/draft | 87.1981 | 50.00% | 2.850 s | Local directional leader |
| `mlx-qwen2.5-0.5b-base-profile-v1` | MLX profile control | 71.3900 | 16.67% | 1.839 s | Matched control |
| `mlx-qwen2.5-0.5b-base-ledger_draft-v1` | MLX compact ledger | 73.8629 | 29.17% | 2.629 s | Matched control |
| `mlx-qwen2.5-0.5b-smoke-lora-profile-v1` | Smoke LoRA profile | 67.9030 | 0.00% | 0.807 s | Rejected training evidence |
| `mlx-qwen2.5-0.5b-smoke-lora-ledger_draft-v1` | Smoke LoRA ledger | 60.2537 | 4.17% | 1.228 s | Rejected training evidence |
| `mlx-qwen2.5-0.5b-unified-pilot-lora-profile-v1` | Unified LoRA profile | 70.7185 | 37.50% | 1.628 s | Rejected: memorization risk |
| `mlx-qwen2.5-0.5b-unified-pilot-lora-ledger_draft-v1` | Unified LoRA ledger | 74.5449 | 29.17% | 2.435 s | Rejected: memorization risk |
| `ox-alpha-b1-profile-v1` | External one-step single pass | 91.0738 | 50.00% | 31.845 s | Rejected: meta/grounding |
| `ox-alpha-b1-profile-v2` | External two-step single pass | 93.5438 | 54.17% | 18.073 s | Rejected: grounding |
| `ox-alpha-b1-source-reviser-v1` | External draft + source revision | 93.3607 | 54.17% | 21.232 s | Rejected: hard gates/grounding |
| `qwen2.5-7b-retrieval-ledger-draft-h11-v1` | 7B compact ledger/draft | 90.6529 | 29.17% | 15.423 s | Rejected: hard gates/grounding |

The small-model fine-tunes are not competitive: the smoke adapter regressed
both matched branches, and the unified adapter failed its +2-point gate and
introduced training-scenario labels into unseen B1 cases. Training loss is
therefore excluded from model selection.

Ox v2 dominates Ox v1 on score, hard gates, latency, output tokens, and artifact
compliance. It does not become a finalist because six outputs contain material
unsupported commitments or guarantees and one introduces a placeholder. The
external provider, stealth identifier, and private-input boundary also remain
deployment risks.

The h10 source-reviser reduced material source-expansion findings from six to
two and eliminated the remaining introduced placeholder, but it still passed
only 13 of 24 hard gates. It scored -0.1831 paired mean points versus v2 while
using 3.14 times its prompt tokens and 1.17 times its mean latency. The branch
is rejected rather than repaired in place.

The h11 7B probe changed only the same-family base-model scale while retaining
the compact-ledger pipeline. It improved the paired mean by +3.4548, but its
95% interval (-1.3847 to +8.8440) crossed zero and its hard-gate rate fell by
20.83 percentage points. Full review found 15 material source-expansion risks,
five prompt/model/process-commentary cases, two introduced-placeholder cases,
and only seven no-flag outputs. Scale alone is rejected as the remaining
source-discipline fix.

## Evidence excluded from winner selection

- Source-profile coverage uses six cases per candidate and was explicitly
  frozen as coverage-only.
- The first Ox v1 publication mixed scorer versions and is invalid.
- Public evaluation adapters are implemented and validated, but no source suite
  has been acquired or executed.
- Synthetic training/test loss does not establish writing quality.
- True B2 and Tier C results do not exist; B1 cannot substitute for either.

## Remaining externally blocked branches

1. Authentic-task unified training — externally blocked. The synthetic unified
   pilot failed, and no authentic named-source rows are both sufficient and
   training-approved.
2. Public compatibility suites — partially completed. Exact real sources for
   six suite IDs have now been hash-validated and adapted. WritingBench still
   lacks an exact judge pin; YapBench remains blocked by missing dataset rights.
3. Profile-specific LoRA sweep — not justified; no named profile clears both
   rights and data-sufficiency gates.
4. B2, Tier C, and human confirmation — blocked by zero eligible finalists and
   the required external access-separated operators/data.

Completed and pruned: `h10-ox-source-verifier-reviser` and
`h11-larger-local-open-model` both failed the all-hard-gates and zero-risk
grounding requirements. Do not repeat either branch without a material new
factor and a new preregistered candidate lineage.

The hash-bound machine frontier and hypothesis registry live at
`../experiments/architecture-frontier-v3.json` and
`../experiments/hypothesis-registry-v1.json`. They prevent rejected ideas from
being repeated without a material new factor.
