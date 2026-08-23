# Iteration 2: compact ledger and single draft

## Decision

Keep `qwen2.5-0.5b-retrieval-ledger-draft-v2` as the leading B1
search-development candidate and the inference wrapper for the smoke fine-tune
comparison.

The candidate scored 87.1981 versus retrieval v1 at 84.8283, a paired +2.3698
points with 13/4/7 win/tie/loss. Hard-gate pass increased from 37.50% to 50.00%,
omission cases fell from 14 to 12, and the registered fabrication and
placeholder-loss counts fell from one each to zero.

The 95% paired bootstrap interval is -2.0211 to +6.7390. It crosses zero, so the
candidate is a directional leader under the preregistered practical-effect
rule, not statistically confirmed superiority or a production recommendation.

## Preregistered gates

| Gate | Threshold | Observed | Pass |
| --- | ---: | ---: | --- |
| Paired mean | at least +2.0 | +2.3698 | Yes |
| Hard-gate pass | at least 37.50% | 50.00% | Yes |
| Omission cases | at most 14 | 12 | Yes |
| Fabrication cases | at most 1 | 0 | Yes |
| Placeholder-loss cases | at most 1 | 0 | Yes |
| Mean latency | at most 4,257.554 ms | 2,850.460 ms | Yes |
| Generated tokens | at most 9,450 | 6,362 | Yes |
| Settled provider cost | $0 | $0 | Yes |

## What changed

Iteration one showed that the separate verifier/reviser caused a mean
-5.9482-point loss from draft to final. V2 removed those stages and regenerated
all outputs with a compact 192-token atomic ledger plus one 512-token draft.
The ledger stage averaged 1,100.578 ms and 2,244 total output tokens; drafting
averaged 1,749.882 ms and 4,118 output tokens.

The resulting candidate has no registered structural, expansion, fabrication,
or placeholder errors. The remaining error concentration is clearer: 12
omission cases and five actionability failures. It passes 12 of 24 hard gates,
which is a material search improvement but still far below production quality.

## Interpretation and next work

The result supports a bounded architecture claim: for this small local model
and visible project-authored B1 slice, explicit compact planning helps when it
feeds a single draft; a free-form model verifier/reviser harms fidelity and
efficiency.

Next, complete the required end-to-end fine-tuning smoke path on a separate,
project-authored training corpus with no B1 case reuse. The smoke experiment
must compare the genuinely updated model with the untuned model under matched
single-pass and leading two-stage inference, while treating training success as
pipeline evidence rather than assuming quality improvement.

## Artifacts

- Aggregate, paired, gate, and pipeline analysis:
  `../experiments/goodprose-compact-ledger-draft-v2-analysis.json`
- Case-level corrected results:
  `../experiments/goodprose-compact-ledger-draft-v2-case-results.jsonl`
- Frozen preregistration: `../configs/baselines/LEDGER_DRAFT_ITERATION_v2.md`

Raw ledgers and final outputs remain ignored locally. The committed analysis
records their exact hashes, model/config provenance, latency, token counts, and
zero provider cost.
