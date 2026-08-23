# Qwen2.5 7B compact-ledger h11 result

## Decision

Reject `qwen2.5-7b-retrieval-ledger-draft-h11-v1`. The one frozen
larger-local-model probe improved the deterministic mean but regressed the hard
gate from 12/24 to 7/24 and failed the permitted full-output grounding audit.
No retry, repair, alternate size, quantization change, or prompt change is
authorized under h11.

This is visible B1 development evidence, not a production result. The accepted
local directional leader remains the 0.5B compact-ledger candidate, which also
is not finalist-ready because it passes only 12/24 hard gates.

## Frozen execution

- Candidate: `qwen2.5-7b-retrieval-ledger-draft-h11-v1`
- Baseline: `qwen2.5-0.5b-retrieval-ledger-draft-v2`
- Generation code revision: `db79b0832a032acae89ec5c47e6aa241a822edcb`
- Runtime: local Ollama 0.9.6 on Apple M3 Pro, 18 GiB unified memory
- Model: `qwen2.5:7b-instruct`, 7,615,616,512 parameters, Q4_K_M,
  Apache-2.0
- Model manifest: `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e`
- Primary blob: `2bada8a7450677000f678be90653b85d364de7db25eb5ea54136ada5f3933730`
- Cases/stages: 24 unique B1 cases; exactly 24 ledger and 24 draft calls
- Time: 2026-08-23T22:04:46Z to 2026-08-23T22:10:56Z
- Tokens: 23,261 prompt and 6,257 output; zero cache-read tokens
- Summed end-to-end latency: 370.163 seconds; mean 15.423 seconds per case
- Cost: $0 settled; no external provider received B1 data

The run manifest binds the exact code revision, model/runtime identity,
resource validation, and raw artifact hashes. Available disk was 43,008,446,464
bytes at execution validation, above the frozen 30 GiB floor; the installed
model was 4,683,087,332 bytes, below the 5.0 GB cap.

## Corrected deterministic result

The immutable v1 output bytes were rescored offline with deterministic scorer
v1.1. No inference was repeated.

| Measure | 0.5B compact ledger | 7B h11 | Change |
| --- | ---: | ---: | ---: |
| Mean development score | 87.1981 | 90.6529 | +3.4548 |
| Median development score | — | 91.7083 | paired median +4.3003 |
| Hard-gate passes | 12/24 | 7/24 | -5 cases |
| Hard-gate rate | 50.00% | 29.17% | -20.83 pp |
| Mean latency | 2.850 s | 15.423 s | +12.573 s |
| Final-output tokens | 6,362 | 6,257 | -105 |
| Cost | $0 | $0 | $0 |

The 10,000-resample paired bootstrap interval is -1.3847 to +8.8440 under
seed 20260822. Wins/ties/losses are 13/1/10. The mean-effect gate passed, but
the interval crosses zero, the no-regression gate failed, and the required
24/24 hard gates failed.

Dimension means were 82.2619 fidelity, 97.7115 clarity/coherence, 92.5428
concision, 89.5833 organization/actionability, and 100.0 for both audience/
format and profile control. Deterministic failures were 17 omission cases,
two poor-actionability cases, and one excessive-rewriting case. No
deterministic fabrication or placeholder-loss case fired, illustrating why
the separate semantic audit was necessary.

The ledger stage used 7,861 prompt and 2,686 output tokens at 6.660 seconds
mean latency. The draft stage used 15,400 prompt and 3,571 output tokens at
8.764 seconds mean latency.

## Full-output audit

Codex inspected every final response against its authoritative source and task
fields. The audit commits only output hashes, case IDs, categories, and compact
rationales—no output bodies.

| Audit result | Cases | Rate |
| --- | ---: | ---: |
| Artifact-only | 19/24 | 79.17% |
| Model/prompt/instruction/process commentary | 5/24 | 20.83% |
| Introduced non-source placeholder | 2/24 | 8.33% |
| Material unsupported source expansion | 15/24 | 62.50% |
| No audit flag | 7/24 | 29.17% |

Material findings included invented deadlines, approval steps, owners,
oversight responsibilities, implementation workflows, review boards,
follow-up channels, categorical certainty that replaced statistical
uncertainty, and an unsupported author role. Prompt or compact-ledger text
appeared in five artifacts. The two new-placeholder cases introduced
`[insert date]`, `[Current Date]`, and `[Your Name]`.

## Gate disposition

Passed: +2 mean effect, zero deterministic fabrication, zero deterministic
placeholder loss, mean latency at most 60 seconds, output tokens at most
16,800, exact model/resource/provenance pins, privacy boundary, and zero cost.

Failed: hard-gate non-regression, 24/24 hard gates, zero omissions,
artifact-only responses, zero introduced placeholders under full review, and
zero material unsupported expansion. The candidate is retained only as
negative evidence that base-model scale alone does not repair the frozen
compact-ledger architecture.

## Artifacts

- Analysis: `../experiments/qwen2.5-7b-retrieval-ledger-draft-h11-v1-analysis.json`
  (`ce051249…`)
- Case results: `../experiments/qwen2.5-7b-retrieval-ledger-draft-h11-v1-case-results.jsonl`
  (`bded0304…`)
- Output audit: `../experiments/qwen2.5-7b-retrieval-ledger-draft-h11-v1-output-audit.json`
  (`5a605d3c…`)
- Audit config: `../configs/baselines/QWEN2_5_7B_H11_OUTPUT_AUDIT_v1.json`
  (`ec2e93a1…`)
- Frontier: `../experiments/architecture-frontier-v3.json` (`d05dfe02…`)

Ignored local raw artifacts remain hash-bound: outputs `aac223cd…`, v1
scores `7d668bae…`, v1 summary `51bf0cae…`, and run manifest `b187875b…`.
