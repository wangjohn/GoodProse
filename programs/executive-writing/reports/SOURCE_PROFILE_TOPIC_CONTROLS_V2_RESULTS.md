# Source-profile paired topic-control result

## Outcome

The versioned topic-swap coverage run is complete and negative. None of the
eleven descriptive profile cards is eligible for advancement or production
selection. The house control passed 2/6 hard gates; descriptive cards passed
between 0/6 and 3/6. Topic-pair sensitivity remained material even for the
best-scoring variants.

This closes the v1 topic-swap implementation gap without changing the
historical v1 evaluation. It does not make a source-specific adapter eligible,
provide authentic-task evidence, or create a finalist.

## Frozen design

- Evaluation: `source-profile-topic-controls-v2`.
- Cases: six project-authored cases in three paired topic swaps.
- Candidates: the house-profile control plus eleven source-text-free,
  descriptive profile cards.
- Model: Ollama 0.9.6, `qwen2.5:0.5b-instruct`, Q4_K_M, exact manifest
  `a8b0c515…` and blob `c5396e06…`.
- Decoding: temperature 0, seed 20260822, no retrieval.
- Scorer: `goodprose-deterministic-v1.1`.
- Execution revision: `059c3500f4d283890c90e12b4a3d485e26bb336f`.
- Calls: 72; 31,020 prompt and 14,208 output tokens; $0 settled cost.
- Timing: 2026-08-23T22:56:52Z to 2026-08-23T22:58:59Z; candidate-level
  mean latency averaged 1,770.1 ms.

The cases hold task family, format, objective, constraints, evidence shape,
quantities, uncertainty, and action structure fixed within each pair while
changing domain vocabulary. Prompts contain no named-person identity, external
URL, source route, rubric, or third-party source body.

## Results

The paired-gap column is the mean absolute deterministic score difference
between the two topics in each of the three pairs. A smaller value is only a
descriptive robustness signal; it cannot compensate for hard-gate failures.

| Candidate | Mean score | Hard gates | Mean absolute paired gap | Gate-disagreement pairs |
| --- | ---: | ---: | ---: | ---: |
| House profile | 85.7024 | 2/6 | 11.3730 | 0 |
| Concise curation brief | 82.1808 | 1/6 | 13.0435 | 1 |
| Conversational essay memo | 81.6937 | 1/6 | 3.5461 | 1 |
| Declarative trajectory update | 82.7326 | 1/6 | 6.9687 | 1 |
| Narrative anecdote advisory | 79.1373 | 1/6 | 16.9001 | 1 |
| Daily cadence note | 84.1754 | 1/6 | 8.9064 | 1 |
| Polemical product-philosophy note | 80.0968 | 1/6 | 14.8620 | 1 |
| Principle-driven manifesto memo | 79.8286 | 0/6 | 9.1576 | 0 |
| Technical link commentary | 81.9315 | 0/6 | 2.2706 | 0 |
| Policy-polemical analysis | 82.3467 | 3/6 | 18.0289 | 1 |
| Institutional narrative letter | 81.6991 | 0/6 | 8.2231 | 0 |
| Operational executive update | 81.4785 | 1/6 | 6.4015 | 1 |

Omissions appeared in 3–6 of six cases for every candidate. The
principle-driven card also produced one deterministic fabrication. The
technical card had the smallest paired score gap but passed no hard gates; the
policy-polemical card had the highest descriptive-profile gate count but the
largest paired gap. These tradeoffs provide no credible winner.

## Control interpretation

- Topic swap: completed with three explicit project-authored pairs.
- Leave-topic-out: structurally satisfied for this prompt-only experiment
  because no evaluation topic, case, example, or source body is fit or
  retrieved by a profile card.
- Leave-time-out: not applicable to this source-text-free prompt-only run.
  Dated leave-time-out evaluation remains required before any future
  corpus-trained or corpus-retrieval profile can advance.

The three pairs are too small for confidence intervals or confirmatory
inference. Deterministic lexical scores also cannot isolate semantic style
quality. The correct disposition is exploratory coverage only.

## Provenance and invalidated precursor

The accepted raw output, score, and summary hashes are respectively
`09381e11…`, `23aa9e13…`, and `0d5e864e…`. Compact committed result hashes are
`bc65bbe5…` and `2de48edb…` for the aggregate and case-level files.

An earlier full local matrix used source metadata with a rounded authorship
time six minutes after execution. It was caught before staging, invalidated,
and isolated with its compact result under the ignored profile-controls
artifact directory. No number from that invalid matrix is used here.

Machine evidence:

- `../experiments/source-profile-topic-controls-v2-results.json`
- `../experiments/source-profile-topic-controls-v2-case-results.json`

## Reproduction

After rebuilding and byte-comparing the cases as documented in the evaluation
README, run from the exact frozen revision with the pinned local model:

```bash
uv run python -m goodprose.executive_writing profile-controls run \
  --config programs/executive-writing/configs/source-profile-evaluation/source-profile-topic-controls-v2.json \
  --output-root programs/executive-writing/artifacts/profile-controls-reproduction \
  --code-revision 059c3500f4d283890c90e12b4a3d485e26bb336f

uv run python -m goodprose.executive_writing profile-controls publish \
  --config programs/executive-writing/configs/source-profile-evaluation/source-profile-topic-controls-v2.json \
  --run-dir programs/executive-writing/artifacts/profile-controls-reproduction/source-profile-topic-controls-v2 \
  --results /tmp/source-profile-topic-controls-v2-results.json \
  --case-results /tmp/source-profile-topic-controls-v2-case-results.json \
  --generated-at 2026-08-23T22:59:05Z
```

Latency-bearing raw hashes will differ across executions. Deterministic output
and score hashes should match on the exact model, runtime, prompt, decoding,
case, and code pins.
