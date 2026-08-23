# Iteration 1: structured retrieval

## Decision

Reject `qwen2.5-0.5b-retrieval-ledger-verify-v1` and retain
`qwen2.5-0.5b-retrieval-v1` as the leading baseline.

The four-stage candidate scored 81.3694 versus 84.8283, a paired difference of
-3.4589 points (95% paired bootstrap interval -10.4503 to +3.6694). It lost on
15 cases, tied one, won eight, and regressed hard-gate pass rate from 37.50% to
33.33%. It also increased omission cases from 14 to 16.

## Preregistered gates

| Gate | Threshold | Observed | Pass |
| --- | ---: | ---: | --- |
| Paired mean | at least +2.0 | -3.4589 | No |
| Hard-gate pass | at least 37.50% | 33.33% | No |
| Omission cases | fewer than 14 | 16 | No |
| Fabrication cases | at most 1 | 0 | Yes |
| Placeholder-loss cases | at most 1 | 1 | Yes |
| Mean latency | at most 6,812.086 ms | 7,239.643 ms | No |
| Generated tokens | at most 16,800 | 16,861 | No |
| Settled provider cost | $0 | $0 | Yes |

The candidate failed the primary advancement rule and both efficiency
guardrails. It cannot advance even though the run avoided registered
fabrications.

## Stage attribution

The preserved draft stage provides a post hoc diagnostic, not a preregistered
candidate. Before the verifier/reviser, the ledger-conditioned drafts scored
87.3175 with the same 37.50% hard-gate rate as retrieval v1. Their paired mean
was +2.4892, but the interval spanned -3.2449 to +8.8155 and omissions increased
from 14 to 15.

The verifier/reviser then reduced the final score by 5.9482 points relative to
the draft (95% interval -10.4025 to -2.4572), changed 13 outputs, improved only
one, and worsened ten. Two revisions collapsed to less than half the draft
length. On `b1-011`, the verifier repeated the draft until its 512-token cap and
the reviser collapsed the complete source-preserving email to one sentence.

Two ledger calls, two verifier calls, and two revision calls hit the 512-token
cap. The ledger also introduced unsupported planning text in at least one
inspected case, confirming that intermediate model artifacts cannot be treated
as authoritative facts.

## Next hypothesis

Remove the external verifier and reviser. Test a two-stage candidate with a
strictly compact atomic ledger followed by one retrieval-conditioned draft that
must internally check every ledger item before emitting only the artifact. Cap
the ledger at 192 tokens, prohibit tables and boilerplate, repeat that the
source—not the ledger—is authoritative, and preserve every negation,
placeholder, number, date, and requested action.

This next candidate must be preregistered and regenerated. The post hoc draft
diagnostic cannot be promoted directly, and its omission regression means a
mere truncation of the existing pipeline is not enough.

## Artifacts

- Aggregate, paired, gate, and post hoc stage analysis:
  `../experiments/goodprose-structured-retrieval-v1-analysis.json`
- Case-level corrected results:
  `../experiments/goodprose-structured-retrieval-v1-case-results.jsonl`
- Frozen preregistration: `../configs/baselines/STRUCTURED_ITERATION_v1.md`

Raw final and intermediate outputs remain ignored locally. The committed
analysis records their exact hashes, model/config provenance, latency, tokens,
and zero cost.
