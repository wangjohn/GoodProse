# Dataset and evaluation strategy

## The central distinction

Accepted RFCs demonstrate the shape and reasoning of a strong specification. They do not, by themselves, teach the transformation RFClear needs to perform.

The supervised task is:

```text
messy coding-agent output + grounded context -> faithful, clear technical specification
```

Training only on standalone RFC text would mostly teach continuation and style imitation. It would not reliably teach fact selection, uncertainty preservation, deduplication, or the conversion of implementation narration into reviewable decisions.

## What the seed sources contribute

| Source | Particular strength | Main caveat | Current role |
| --- | --- | --- | --- |
| Go proposals | Compatibility, invariants, implementation detail, worked examples | Document structure and maturity vary | training reference + public dev |
| React RFCs | Concise motivation, API design, adoption, teaching | Less coverage of operations, rollout, and security | training reference + public dev |
| Rust RFCs | Guide/reference separation, formal semantics, alternatives, unresolved questions | Strong language-design bias | training reference + public dev |
| Bytecode Alliance RFCs | Systems architecture, explicit proposals, open questions | Small enough that document-level splitting would leak its house style | full source-family test holdout |
| Teleport RFDs | Production UX, security, failure modes, operations, test plans | Repository is AGPL-3.0-only; training and redistribution need an explicit review | candidate only |

The best next public source is a carefully selected set of Kubernetes Enhancement Proposals. KEPs add rollout, graduation criteria, feature gates, observability, testing, and production failure handling—the dimensions least represented by language and framework RFCs. Hold out at least one entire source family rather than randomly mixing every source into every split.

## Build paired examples, in this order

### 1. Real agent output with human revision

This is the highest-value data. Capture Claude Code or Codex output from real, consented engineering tasks, then have a technically qualified reviewer produce the gold specification. Preserve the original request and only the context necessary to support the result.

Before storage, remove secrets, credentials, personal data, customer identifiers, proprietary material without permission, and irrelevant repository content. Record what was removed so the model is not penalized for omitting it.

Aim for multiple input shapes: implementation summaries, long tool transcripts, terse completion notes, diff walkthroughs, debugging reports, and outputs containing uncertainty or failed approaches.

### 2. Paired project history

Where licensing permits, pair a pre-design artifact with the final committed specification: an issue description, early checked-in draft, implementation plan, or PR description with an accepted RFC. Use the final document's commit history to study what expert reviewers added or removed.

Treat issue and pull-request comments as a separate licensing/provenance surface; do not assume a repository's file license automatically covers every piece of platform discussion. Prefer committed files or obtain a clear review before ingesting discussion text.

### 3. Synthetic degradation

Starting from a strong spec, create a deliberately messy agent-style input by flattening structure, repeating facts, mixing decisions with implementation notes, and removing editorial connective tissue. Never add facts that are absent from the target.

Label this data. Keep it a minority of the training mix so the model does not learn artifacts of the degradation prompt. Synthetic examples are useful for coverage and curriculum, but should not substitute for real agent-to-human revision pairs.

As an initial target, prefer roughly 200 deeply reviewed pairs over thousands of weak synthetic pairs. A reasonable first mix is 60% real agent/human revision, 25% paired history, and no more than 15% synthetic degradation. Adjust after error analysis rather than treating those percentages as permanent.

## Preserve the information boundary

The gold spec must not require the model to know facts missing from its input. For each example, annotate:

- facts that must appear;
- facts that may appear;
- claims the model must not make;
- decisions that remain open;
- sensitive details that must be omitted;
- source evidence for consequential claims.

This turns factual fidelity into something measurable and prevents a fluent model from scoring well by inventing plausible detail.

## Split by lineage, source, and time

Random row splits are unsafe. One feature may appear as an issue, draft RFC, final RFC, implementation PR, release note, and several synthetic variants.

Use three protections together:

1. Assign all artifacts and derivatives for one feature to a single `lineage_group`.
2. Reserve one or more complete source families or domains for generalization testing.
3. Apply a chronological cutoff so later work cannot leak backward through revisions or follow-up documents.

Run exact-hash and near-duplicate checks after normalization. Compare titles, code blocks, long n-grams, and semantic similarity; boilerplate templates should not be mistaken for substantive duplication.

## Public versus private evaluation

Public Go, React, Rust, and Bytecode Alliance RFCs are excellent rubric anchors, but a frontier base model may already know them. A public holdout measures pipeline discipline and some transformation ability; it cannot establish absence of memorization.

Maintain a final private suite of newly captured agent outputs and newly written gold specs. Use public `dev_eval` cases for prompt development, keep the Bytecode Alliance source holdout untouched until a release candidate exists, and use the private test once for model selection. Refresh a portion of the private suite after major iterations.

## Evaluation design

Combine three types of checks:

- **Deterministic checks:** required facts, forbidden claims, named APIs, explicit open questions, redaction requirements, and structural validity.
- **Rubric scoring:** fidelity, completeness, precision, operational readiness, tradeoffs, and clarity using [`../evals/RUBRIC.md`](../evals/RUBRIC.md).
- **Human calibration:** two independent reviewers on a stratified subset, with disagreements adjudicated and used to refine judge anchors.

Track the material-fabrication rate separately from the average score. Also report the 25th percentile and scores by domain/input type; a high mean can conceal dangerous failures on security or migration cases.

## Suggested project sequence

1. **Reference baseline:** finish the pinned corpus and use it to define the house rubric and spec template.
2. **Prompt baseline:** build 20–30 real dev cases and measure a strong prompted model before fine-tuning.
3. **Gold set:** collect and review the first 200 paired examples, with lineage and privacy metadata.
4. **Private eval:** author at least 50 cases across API, UI, data model, distributed systems, security, migration, and performance work.
5. **Fine-tune and ablate:** compare prompt-only, fine-tuned, and retrieval-assisted variants; remove each data source in turn to learn what actually helps.
6. **Scale from errors:** add examples targeted at observed fidelity or coverage failures, not merely more RFC prose.
