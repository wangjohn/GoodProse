# Cost ledger

## Budget state

- Project ceiling: USD $100 settled spend
- Approved spending envelope: none
- Attempted spend: USD $0
- Settled spend: USD $0
- Refunded spend: USD $0
- Remaining project budget: USD $100

No paid action is authorized by this file. Before the first paid action, Codex
must present the scoped request required by the goal and receive explicit user
approval plus secure agent-card access.

## Transactions

Record proposed, approved, attempted, settled, and refunded amounts with a
timestamp, provider, purpose, experiment identifier, and non-sensitive receipt
reference. Never record payment credentials.

| Timestamp | Provider | Purpose | Experiment | Status | Amount | Reference |
| --- | --- | --- | --- | --- | ---: | --- |
| 2026-08-23T02:02:50Z | OpenRouter | Ox Alpha harness capability gate | `harness-preflight-2026-08-22` | attempted and settled | $0.00 | local sanitized session metadata |
| 2026-08-23T02:26:09Z | OpenRouter | Corrected Ox Alpha harness rerun | `harness-preflight-2026-08-22-rerun` | attempted and settled | $0.00 | local sanitized session metadata |
| 2026-08-23T02:26:09Z | OpenRouter | B1 benchmark design review | `ox-benchmark-design-review-v1` | attempted and settled | $0.00 | committed sanitized result record |
| 2026-08-23T02:26:09Z | Local Apple M3 Pro | Build and validate 24-case B1 v1 benchmark | `goodprose-b1-v1-build` | completed | $0.00 | committed manifest and green verification suite |
| 2026-08-23T02:26:09Z | Local Apple M3 Pro | Implement and validate matched baseline runner | `local-baseline-runner-v1` | completed | $0.00 | pinned configs and green focused suite |
| 2026-08-23T03:48:27Z | Local Apple M3 Pro | Generate three matched 24-case B1 baselines | `goodprose-b1-v1-initial-baselines` | completed; scorer comparison invalidated | $0.00 | preserved local outputs, timings, tokens, scores, and hashes |
| 2026-08-23T04:02:28Z | Local Apple M3 Pro | Offline v1.1 rescore and paired baseline analysis | `goodprose-b1-v1.1-baseline-analysis` | completed | $0.00 | exact output-byte reuse, corrected score hashes, 10,000 paired resamples |
| 2026-08-23T04:08:22Z | OpenRouter | Bounded Ox Alpha baseline-failure critique | `ox-baseline-failure-review-v1` | attempted; empty zero-token runtime | $0.00 | four session IDs and fresh public inventory record |
| 2026-08-23T04:13:23Z | Local Apple M3 Pro | Implement and validate structured retrieval runner | `structured-retrieval-runner-v1` | completed | $0.00 | frozen config, 96-call mocked pipeline, green repository suite |
| 2026-08-23T04:21:41Z | Local Apple M3 Pro | Run and analyze structured retrieval iteration one | `goodprose-structured-retrieval-v1-analysis` | completed; rejected | $0.00 | 96 local calls, exact intermediate hashes, corrected paired analysis |
| 2026-08-23T04:27:11Z | Local Apple M3 Pro | Implement and validate compact ledger-draft runner | `compact-ledger-draft-runner-v2` | completed | $0.00 | frozen two-step config, enforced token limits, green repository suite |
| 2026-08-23T04:34:10Z | Local Apple M3 Pro | Run and analyze compact ledger-draft iteration two | `goodprose-compact-ledger-draft-v2-analysis` | completed; kept | $0.00 | 48 local calls, corrected paired analysis, every frozen gate passed |
| 2026-08-23T05:02:02Z | Local Apple M3 Pro | Install pinned MLX tooling and compile isolated smoke corpus | `goodprose-project-authored-smoke-v1-build` | completed | $0.00 | 48 reproducible records, exact hashes, B1 contamination pass, green suite |
| 2026-08-23T05:07:55Z | Local Apple M3 Pro | Implement and validate bounded MLX training runner | `mlx-smoke-training-runner-v1` | completed | $0.00 | frozen config, mocked genuine-update proof, failure preservation, green suite |
| 2026-08-23T05:14:54Z | Local Apple M3 Pro | Run genuine 40-iteration LoRA smoke fine-tune | `qwen2.5-0.5b-mlx-lora-smoke-v1` | completed; smoke pass | $0.00 | 4,198 trained tokens, 56 nonzero tensors, synthetic test loss 0.190, no remaining process |
| 2026-08-23T05:19:47Z | Local Apple M3 Pro | Implement and freeze matched MLX B1 evaluation | `mlx-qwen2.5-0.5b-smoke-b1-runner-v1` | completed | $0.00 | exact base/adapter hashes, four matched candidates, green 54-test suite |
| 2026-08-23T05:31:13Z | Local Apple M3 Pro | Run four matched MLX base/adapter B1 candidates | `mlx-qwen2.5-0.5b-smoke-b1-v1` | completed; adapter rejected for quality | $0.00 | 144 local generations, paired analysis, 158.463 seconds, no remaining process |
| 2026-08-23T05:53:27Z | OpenRouter | Bounded all-profile public source discovery | `ox-source-discovery-v1` | completed and reviewed | $0.00 | exact Ox session, prompt/response hashes, and Codex primary-source verification |
| 2026-08-23T06:54:38Z | OpenRouter | Draft typed source, rights, profile, eval, and run artifacts | `ox-source-artifacts-implementation-v1` | completed and reviewed with corrections | $0.00 | exact Ox session, 17 drafted files, scoped validation, and Codex review |
| 2026-08-23T07:23:32Z | OpenRouter | Draft the source-text-free profile coverage runner and publisher | `ox-profile-coverage-runner-v1` | completed and reviewed with corrections | $0.00 | exact Ox session, prompt/response hashes, mocked tests, and Codex integrity review |
| 2026-08-23T07:40:01Z | Local Apple M3 Pro | Run and independently publish all-eleven source-text-free profile coverage | `source-profile-coverage-v1` | completed; exploratory coverage only | $0.00 | 72 local calls, exact prompt/output/artifact hashes, v1.1 offline rescore, no raw text published |
| 2026-08-23T08:16:33Z | OpenRouter | Draft aggregate-only B2 and one-shot Tier C lifecycle infrastructure | `ox-holdout-lifecycle-v1` | completed and reviewed with substantial corrections | $0.00 | exact Ox session, prompt/response hashes, synthetic-only fixtures, and Codex trust-boundary audit |
| 2026-08-23T15:31:13Z | Local Apple M3 Pro | Audit and validate holdout lifecycle protocol | `holdout-lifecycle-v1-validation` | completed; infrastructure only | $0.00 | 38 focused and 122 full tests, schema checks, Ruff, format, Pyright, and no true holdout execution |

## Zero-cost feasibility snapshot

- Local system: Apple M3 Pro (12 CPU cores, 18 GPU cores), 18 GiB unified
  memory, macOS arm64, with 48 GiB free disk at the checkpoint.
- Existing environment: Python 3.12 project environment occupies 325 MiB.
- $0 scope: benchmark/schema work, deterministic baselines and gates,
  retrieval, data validation, small local smoke training, tests, reports, and
  source/right audits using public metadata.
- Local training expectation: a tiny or small MLX-compatible model and bounded
  adapter smoke run are plausible. Production-scale claims require measured
  throughput and memory evidence; no larger download is justified yet.
- Ox Alpha/OpenRouter: inventory reported zero prompt and completion prices and
  no other pricing fields for `stealth/ox-alpha` on 2026-08-22. The corrected
  complete harness gate passed, so bounded delegation is enabled at $0 while
  the runtime model and pricing remain unchanged.
- Paid compute: not approved and not currently necessary for the next
  evidence-bearing checkpoint. No paid resource was started.

## Planning tiers (not spending authorization)

| Tier | Scope | Estimated charge | Runs | Wall time | Value |
| --- | --- | ---: | ---: | --- | --- |
| Local | deterministic baselines, retrieval, tiny smoke fine-tune | $0 | 3 baselines + 1 smoke | hours to days | proves the first closed loop |
| Low-cost | one small external adapter training confirmation plus bounded evaluation | $5–$15 | 1–2 | under 8 hours | tests whether local smoke behavior transfers |
| Recommended | successive-halving unified pilots plus calibrated evaluation | $35–$60 | 3–5 | 1–2 days | informs the architecture choice |
| Ambitious | finalist confirmation within the remaining ceiling | at most $100 total project spend | evidence-dependent | 2–4 days | useful only after free gates pass |

The paid tiers are provisional planning estimates. Provider, model/GPU,
per-run cost, hard limits, and shutdown procedure must be pinned in a scoped
budget request before any charge. Evaluation cost remains $0 for the current
deterministic slice. Paid model judging and convenience-only faster compute are
optional until benchmark validity and approved training data justify them.
