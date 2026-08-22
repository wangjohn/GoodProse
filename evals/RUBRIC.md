# GoodProse evaluation rubric

Score each dimension from 0 to 4. Judge against the input, channel, audience, objective, constraints, and fact inventory rather than similarity to reference wording.

| Dimension | Weight | A score of 4 means |
| --- | ---: | --- |
| Factual fidelity | 30% | Every material claim is supported; uncertainty and level of commitment are preserved; nothing decision-relevant is invented. |
| Objective fulfillment | 20% | The communication achieves the requested purpose and makes the decision, recommendation, or call to action unmistakable. |
| Audience fit | 15% | Context, vocabulary, evidence, and emphasis match what the intended readers need. |
| Channel fit | 10% | Structure, length, title or subject, opening, and close suit the requested email, memo, or blog post. |
| Reasoning and substance | 10% | The argument is coherent, important tradeoffs remain visible, and concrete evidence supports the conclusion. |
| House-style adherence | 10% | The output follows the selected voice profile without copying phrases or impersonating a person. |
| Clarity and concision | 5% | The writing is direct and easy to navigate without removing necessary nuance. |

## Score anchors

- **4 — excellent:** ready to send or publish with only cosmetic edits.
- **3 — good:** useful and correct; a few non-critical edits remain.
- **2 — mixed:** captures the core point but needs material editing.
- **1 — poor:** omissions, ambiguity, or unsupported framing make it unreliable.
- **0 — unusable:** contradicts the source, misses the objective, or is substantially fabricated.

## Failure gates

Fail the case regardless of its weighted score when the output:

- invents a material fact, decision, quotation, commitment, deadline, metric, or status;
- reverses the requested decision or call to action;
- silently resolves explicit uncertainty or disagreement;
- reveals information marked confidential or reproduces data that should be redacted;
- copies a distinctive phrase from a style reference or presents itself as a named person;
- uses the wrong channel or audience in a way that could cause a material communication failure.

## Reporting

Report means and 25th percentiles by dimension, pass rate, material-fabrication rate, required-fact recall, forbidden-claim rate, and results by channel. Include blinded pairwise preference and estimated human editing time against the baseline. Preserve per-example results and reviewer disagreements.
