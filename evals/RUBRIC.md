# RFClear evaluation rubric

Score each dimension from 0 to 4. Judge against the case input and its fact inventory, not against exact wording or section names in the reference spec.

| Dimension | Weight | A score of 4 means |
| --- | ---: | --- |
| Factual fidelity | 30% | Every material claim is supported by the input; uncertainty and missing information are explicit; no behavior, rationale, or status is invented. |
| Decision completeness | 20% | The problem, goals, non-goals, chosen design, interfaces, constraints, and unresolved questions are covered when the input supports them. |
| Technical precision | 15% | APIs, data models, state transitions, algorithms, invariants, and examples are specific enough for implementation and review. |
| Failure and operational readiness | 15% | Relevant failure modes, security/privacy implications, compatibility, migration/rollout, observability, and test strategy are addressed. |
| Rationale and tradeoffs | 10% | The document separates facts from decisions and explains meaningful alternatives and consequences without manufacturing rationale. |
| Clarity and navigation | 10% | The spec is concise, logically ordered, terminology is stable, and readers can quickly find decisions and open questions. |

## Score anchors

- **4 — excellent:** ready for technical review with only cosmetic edits.
- **3 — good:** correct and useful; a few non-critical gaps or organization problems.
- **2 — mixed:** captures the core idea but needs material clarification before implementation.
- **1 — poor:** major omissions, ambiguity, or unsupported claims make it unreliable.
- **0 — unusable:** contradicts the input, misses the proposed change, or is largely fabricated.

## Failure gates

Regardless of weighted score, mark the case as failed when any of these occur:

- A fabricated API, invariant, security property, migration step, compatibility guarantee, or implementation status could change a reviewer or implementer's decision.
- A contradiction reverses required behavior.
- Sensitive data present in the input is reproduced when the case says it must be redacted.
- The output silently resolves an explicitly open question.

A material fidelity failure also caps the reported weighted score below the release threshold. Track these failures separately; averaging them away hides the most dangerous behavior for a specification-writing model.

## Recommended reporting

Report the mean and 25th percentile for each dimension, overall pass rate, material-fabrication rate, and scores by input type and domain. Pairwise preference against the baseline prompt is useful, but always retain absolute failure rates.
