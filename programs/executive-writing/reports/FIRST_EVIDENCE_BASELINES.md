# First-evidence baseline comparison

The complete closed-loop table, including the genuine smoke fine-tune and
matched MLX evaluation, is now in `FIRST_EVIDENCE_RESULTS.md`. This report
retains the initial baseline and inference-iteration evidence in detail.

## Decision

Keep `qwen2.5-0.5b-retrieval-v1` as the baseline for the first improvement
iteration. It is the only prompted candidate that clears the preregistered
advancement gate against minimal prompting: +17.2761 paired development points
(95% paired bootstrap interval +6.8559 to +27.9577) with a +12.50 percentage
point hard-gate pass-rate change.

This is exploratory B1 search evidence, not a production recommendation. The
retrieval candidate passed only 9 of 24 hard gates, and its +0.5444-point mean
advantage over the profile candidate is practically inconclusive (95% interval
-4.8608 to +6.5040).

## Validity correction

The original frozen v1 scorer treated an explicitly negated enterprise caveat
as an affirmative forbidden claim for all three candidates. The raw outputs,
latencies, token counts, and v1 artifacts are preserved, but the v1 comparative
scores are invalidated. Scorer v1.1 applies the committed narrow negation rule
and changes exactly the shared `b1-011` result in each candidate. No inference
was rerun. Because this correction was frozen after generation, the results are
post-generation evaluator calibration and cannot be described as confirmatory.

## Shared results table

| Candidate | Mean quality | Median | Hard-gate pass | Mean latency | Prompt tokens | Output tokens | Cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Minimal | 67.5522 | 74.1263 | 25.00% | 1,293.9 ms | 4,523 | 2,937 | $0.00 |
| Profile card | 84.2839 | 85.0178 | 20.83% | 2,114.1 ms | 6,805 | 5,862 | $0.00 |
| Retrieval | 84.8283 | 86.0000 | 37.50% | 1,703.0 ms | 11,002 | 4,200 | $0.00 |
| Compact ledger + draft v2 | 87.1981 | 91.2353 | 50.00% | 2,850.5 ms | 22,812 | 6,362 | $0.00 |

“Mean quality” is the preregistered deterministic 0–100 development proxy.
It does not establish semantic fidelity, writing preference, or audience
quality.

## Paired comparisons

| Baseline → candidate | Mean Δ | Median Δ | Win/tie/loss | 95% bootstrap interval | Hard-gate Δ | Advance? |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Minimal → profile | +16.7317 | +16.0520 | 19/0/5 | +8.1738 to +25.3362 | -4.17 pp | No |
| Minimal → retrieval | +17.2761 | +14.6042 | 16/1/7 | +6.8559 to +27.9577 | +12.50 pp | Yes |
| Profile → retrieval | +0.5444 | 0.0000 | 11/2/11 | -4.8608 to +6.5040 | +16.67 pp | No |

Intervals use 10,000 paired bootstrap resamples with seed 20260822. The
advancement rule requires at least +2 mean points and no hard-gate regression.

After the initial table was frozen, iteration two advanced compact ledger plus
single-draft inference over retrieval v1 by +2.3698 paired points with a +12.50
hard-gate percentage-point change. Its 95% interval (-2.0211 to +6.7390)
crosses zero, so it is the directional B1 leader, not a confirmed winner. See
`ITERATION_2_LEDGER_DRAFT.md` for the complete preregistered gate result.

## Failure analysis

Retrieval reduces format failures to zero and has the strongest hard-gate
rate, but 14 cases still omit at least one registered critical fact. It also
loses one confidential placeholder and makes one real unsupported claim: it
turns “does not include new headcount” into “includes new headcount of 20
employees.” Four cases miss the requested next action.

The profile card improves the mean substantially over minimal prompting, but it
does not advance because hard-gate pass rate falls from 25.00% to 20.83%. Its
remaining failures include omissions on 17 cases, one placeholder loss, three
outputs beyond the 150% expansion gate, and nine format failures. Minimal
prompting has 18 omission cases, 21 format failures, and 12 actionability
failures.

Task-family slices are descriptive only: each has one to three cases. Retrieval
looks strongest on strategy updates, sensitive communication, and concise
revision, but lags on engineering documents, internal memos, and
content-controlled rendering. Those contrasts are useful for error targeting,
not subgroup conclusions.

## Next hypothesis

Add a structured fact-and-constraint ledger before drafting and an explicit
verification pass after drafting, using the same local model and retrieval
example. The iteration succeeds only if it reduces critical omissions and the
unsupported-transformation count without lowering the 37.50% retrieval hard
gate or adding more than a bounded latency/token increase. This is a prompt and
pipeline hypothesis, not a benchmark change.

Ox Alpha received a bounded critique assignment on this analysis. Its live
OpenRouter/OpenCode endpoint returned empty zero-token completions on fresh
default and high variants, a fork of the previously successful session, and a
minimal availability diagnostic. The model remained listed at $0, so this is a
harness/provider runtime failure rather than a budget or inventory rejection.
No critique was produced or inferred. Its intended role remains to challenge
scorer validity, selection logic, and the next hypothesis—not to generate
candidates, author the benchmark, or act as sole judge. The failed optimization
does not block the local evidence loop.

## Artifacts

- Machine-readable aggregate and paired analysis:
  `../experiments/goodprose-b1-v1.1-baselines.json`
- Machine-readable case-level results:
  `../experiments/goodprose-b1-v1.1-case-results.jsonl`
- Preserved invalidated v1 audit record:
  `../experiments/b1-v1-initial-baselines.json`
- Ox Alpha review runtime record:
  `../experiments/ox-baseline-failure-review-v1.json`
- Accepted iteration-two analysis:
  `../experiments/goodprose-compact-ledger-draft-v2-analysis.json`
- Frozen correction record:
  `../../../evals/executive-writing/goodprose-b1-v1/SCORER_CALIBRATION_v1.1.md`

Large raw output and corrected-score artifacts remain in ignored local result
directories. Their exact hashes are recorded in the committed analysis.
