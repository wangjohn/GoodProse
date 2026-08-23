# Ox Alpha B1 source-verifier/reviser preregistration v1

Status: frozen before candidate generation.

## Frontier justification

The hash-bound common frontier contains thirteen 24-case candidates and zero
finalist-ready rows. Ox v2 is the strongest score ceiling and a successful
artifact-only harness repair, but it still adds unsupported commitments,
workflows, restrictions, or guarantees in six cases and passes only 13 of 24
lexical hard gates. The active hypothesis registry ranks a source-only verifier
and reviser as the highest-value remaining architecture change.

This experiment creates a new candidate lineage. It does not repair, filter,
reuse, or send any v1/v2 output or audit finding to Ox.

## Question and causal change

Can a fresh `draft -> source verify/revise` pipeline remove unsupported
inference and preserve operative source wording well enough to pass all B1 hard
gates, while holding provider, model, reasoning, decoding, tool denial, input
cases, and external data boundary fixed?

For each case:

1. A fresh isolated Ox session receives only the B1 task family, objective,
   audience, format, constraints, and source material and drafts one artifact.
2. A second isolated Ox session receives the same task fields and source plus
   that fresh draft. It must make the smallest revision needed so every claim
   is directly entailed, remove inferred process or commitments, preserve all
   operative facts, and reuse source wording for uncertainty, negation,
   decisions, thresholds, and actions wherever grammatical.

The second stage is part of the candidate architecture. It is not an evaluation
judge, teacher, rejection sampler, or data generator. It receives no expected
answer, scorer, rubric, prior candidate, B2/Tier C content, private material, or
human result. Neither stage's output may enter training.

## Frozen candidate and integrity rules

- Experiment/candidate: `ox-alpha-b1-source-reviser-v1`
- Provider/model: OpenRouter / `stealth/ox-alpha`
- Harness: Ori `0.8.0+3511459`, official OpenCode `1.18.21`, high reasoning,
  temperature 0, top-p 1, two maximum agent steps per stage, wildcard tool
  denial
- Agent config: `opencode-source-reviser-v1.json`, SHA-256 `aaedc44…`
- Pipeline: exactly one fresh draft and one final revision per case; 48 stage
  sessions and 24 final candidate outputs in benchmark order
- Retry: one retry only after transport timeout, nonzero harness exit, empty
  event stream, or empty stage output. A nonempty draft remains fixed for its
  revision, and a nonempty revision is final. No quality resampling.
- Cost: execute only if exact live inventory, required parameters, and every
  reported price field remain zero.

The runner must validate every stage's exported model, provider, OpenCode
version, event/session cost, finish reason, prompt/output/event hash, token use,
latency, tool-event absence, and zero file changes. Draft and final output
bodies and event streams remain ignored. The manifest records stage hashes and
aggregates; committed results contain only final scores, hashes, and compact
audit findings.

## Frozen decision gates

Primary comparison: directly pinned deterministic-v1.1 results for
`qwen2.5-0.5b-retrieval-ledger-draft-v2` on the same 24 B1 cases. Ox v2 is a
secondary descriptive comparison only.

The candidate enters the common automated frontier only if all conditions
hold:

1. paired mean improvement over compact ledger is at least two points;
2. hard-gate pass rate does not regress;
3. all 24 deterministic hard gates pass;
4. all final responses are artifact-only with no agent, tool, step, session,
   instruction, task-status, or model commentary;
5. no final response introduces a placeholder or run-date metadata absent from
   the source/task fields;
6. permitted full-output review finds no material unsupported fact, decision,
   attribution, owner, approval, commitment, deadline, guarantee, restriction,
   workflow, rationale, or follow-up channel;
7. no privacy, rights, leakage, provider, or provenance gate fails.

Report paired mean and median effects, the 10,000-resample interval,
wins/ties/losses, dimensions, errors, all-hard-gates status, draft/revision
tokens and latency, settled cost, and every compact audit category. Any failure
rejects the candidate while preserving diagnostic evidence. No observed result
may change this candidate in place.

## Stopping implication

If this candidate fails, refresh the common frontier and hypothesis registry.
The only currently identified affordable challenger after it is one bounded
larger-local-model compact-ledger probe, contingent on inventory, disk, memory,
and model-pin feasibility. Current synthetic training and profile-specific
adapter branches remain pruned unless authentic rights-approved data appears.

B1 remains visible and lexical. A full pass would establish automated frontier
eligibility only; private-input acceptability, stable deployment, aggregate-only
B2, genuine sealed Tier C, and intended-audience human confirmation remain
mandatory.
