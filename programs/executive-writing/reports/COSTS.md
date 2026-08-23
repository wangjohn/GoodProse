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
