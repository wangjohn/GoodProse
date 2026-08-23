# Source-profile paired topic controls v2

This visible B1-derived slice contains six project-authored cases arranged as
three topic-swap pairs. Within each pair, task family, format, objective,
constraints, evidence shape, quantities, uncertainty, and requested action are
held constant while domain vocabulary changes. It tests whether each of the
eleven descriptive, source-text-free profile cards behaves consistently across
topics; it does not test identity imitation or endorsement.

No third-party source body, retrieval example, hidden answer, or named-person
identity enters an evaluated prompt. The 12 candidates are the house-profile
control plus the eleven descriptive cards from the frozen named-source
manifest. All 72 outputs are scored with deterministic scorer v1.1. The run is
exploratory coverage only and cannot select a production profile.

For these prompt-only cards, every task is leave-topic-out by construction:
the cards fit or retrieve no evaluation topic, example, or source text. A
leave-time-out split is not applicable because no dated documents are fit or
retrieved. It remains mandatory before evaluating any future corpus-trained or
corpus-retrieval profile.

Rebuild the committed cases and manifest:

```bash
uv run python -m goodprose.executive_writing benchmark build \
  --source evals/executive-writing/source-profile-topic-controls-v2/cases.source.json \
  --cases /tmp/source-profile-topic-controls-v2-cases.jsonl \
  --manifest /tmp/source-profile-topic-controls-v2-manifest.json \
  --schema /tmp/source-profile-topic-controls-v2-schema.json \
  --benchmark-id source-profile-topic-controls-v2 \
  --limitation 'Six project-authored cases form three paired topic swaps and provide exploratory robustness evidence only.' \
  --limitation 'Lexical deterministic checks do not establish semantic writing quality or detect every unsupported claim.' \
  --limitation 'The source-text-free profile-card candidate has no dated fitting corpus, so leave-time-out is not applicable here and remains required before corpus-trained profile evaluation.'
```

Compare the three generated files byte-for-byte with `cases.jsonl`,
`manifest.json`, and `case.schema.json`. The runner and publisher commands are
documented in the program reproduction guide.
