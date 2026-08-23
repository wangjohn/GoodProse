# GoodProse B1 v1 preregistration

Status: frozen before candidate outputs were generated on 2026-08-22.

## Purpose and comparison set

B1 v1 screens the first-evidence candidates on matched cases:

1. an untuned/minimal-instruction local-model baseline;
2. a strong profile-card prompt using the same local model;
3. a retrieval/example-conditioned prompt using the same local model;
4. the smoke fine-tuned candidate, after the training path is complete.

The local model, exact revision, prompt hashes, decoding configuration, seed,
hardware, latency, and cost must be recorded for every run. Candidate outputs
must never see expected checks or scorer details.

## Primary metric and hard gates

The exploratory primary metric is paired mean development score on the 0-100
scale, with the contract weights frozen in `manifest.json`:

- 35% deterministic source fidelity and factual correctness;
- 20% clarity/coherence proxy;
- 15% concision proxy;
- 15% organization and actionability proxy;
- 10% audience and format proxy;
- 5% profile-control guardrail.

A candidate fails the screen if any registered critical fact, caveat,
must-preserve span, or confidential placeholder is missing; a registered
forbidden critical claim or identity signal appears; or output length exceeds
150% of the case maximum. Passing these lexical gates does not prove the absence
of semantic unsupported claims, privacy failures, or factual errors.

## Effect and analysis

The default minimum practically important effect is two absolute development
points versus the strongest existing baseline, with no lower hard-gate pass
rate. Report the paired mean difference, median difference, win/tie/loss count,
and a 95% paired bootstrap interval from 10,000 resamples using seed 20260822.
Report case-level results and task-family slices, but label all slice estimates
descriptive because each contains only one to three cases. Report all attempted
comparisons and negative results; do not treat a selected winner as
confirmatory.

## Search and shadow cadence

B1 is visible and may be run for every candidate. Tier B2 remains aggregate
only and may be queried after three accepted B1 improvements, after a major
architecture change, or at finalist readiness—whichever occurs first. A B1
gain paired with a B2 regression cannot advance without a documented cause.
Tier C remains sealed and is not part of this first-evidence run.

## Known limitations

The cases are project-authored rather than authentic permissioned rough-to-final
pairs. Lexical aliases can miss valid paraphrases and cannot detect all semantic
fabrications, tone failures, or writing-quality differences. Automated results
are development proxies only; later calibrated judging and intended-audience
human evaluation remain required by the research contract.
