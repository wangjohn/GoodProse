# Data

GoodProse keeps raw sources, metadata views, derived training records, and evaluation cases separate. Never silently modify raw data or move an example across splits to improve a score.

## `raw/` and `sources.json`

`raw/` contains exact upstream files at revisions pinned in [`sources.json`](sources.json). The current collection consists primarily of technical proposals assembled before the GoodProse pivot. These documents can supply complex source material for compression and audience-adaptation experiments; they are not executive-writing gold outputs.

The manifest assigns one of four roles:

- `train_reference`: may support training-side source material or annotation.
- `dev_eval`: public development holdout for prompt and harness iteration.
- `test_eval`: protected source-family holdout; never tune prompts or weights on it.
- `candidate`: metadata only until its review gate is cleared.

## `content-foundation/`

This metadata view identifies documents with useful reasoning, decisions, constraints, evidence, or operational consequences. Membership does not endorse the source's prose. See [`content-foundation/index.json`](content-foundation/index.json).

## `style-references/`

This collection separates approved GoodProse artifacts from external clarity references and held-out benchmarks. Only `approved_examples` may be referenced as training-side style examples. Read [`style-references/HOUSE_STYLE.md`](style-references/HOUSE_STYLE.md) before approving an artifact.

## `voice-profiles/`

Voice profiles describe observable writing traits without asking the model to impersonate a named person. Every training and eval input references a versioned profile from [`voice-profiles/index.json`](voice-profiles/index.json).

## `derived/`

Generated provider-neutral JSONL records conform to [`schemas/training-example.schema.json`](schemas/training-example.schema.json). This directory is ignored except for its README because real executive material may contain proprietary or personal information.

The preferred supervised pair is:

```text
rough notes, draft, transcript, or research
+ audience, channel, objective, constraints, and voice profile
    -> human-approved email, internal memo, or blog post
```

Every derived record identifies its creation method, lineage group, source documents, approved style references, licenses, voice profile, and reviewer status.

## Before adding a source

1. Confirm that collection, storage, annotation, training, and redistribution are permitted.
2. Record immutable provenance, licensing, and selection rationale.
3. Assign train, development, or test status before using the source in generation.
4. Group drafts, revisions, transcripts, and final artifacts from one communication under one lineage.
5. Keep private material out of Git and scan it before and after annotation.
6. Run `make validate` for registered public sources.
